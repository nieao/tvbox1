"""
LLM工厂模块

支持多个LLM后端:OpenAI GPT-4, Google Gemini, Anthropic Claude
提供统一的接口抽象、自动重试机制、配置管理和错误处理
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import re
import asyncio
import logging
from dataclasses import dataclass
import time

# 可选依赖导入
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0  # 初始重试延迟(秒)


class LLMProvider(ABC):
    """LLM提供商抽象基类"""

    def __init__(self, config: LLMConfig):
        """
        初始化LLM提供商

        Args:
            config: LLM配置对象
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本响应

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            生成的文本
        """
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """
        生成JSON格式响应

        Args:
            prompt: 提示词
            schema: 期望的JSON结构
            **kwargs: 额外参数

        Returns:
            解析后的JSON对象
        """
        pass

    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        指数退避重试机制

        Args:
            func: 要重试的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数返回值
        """
        delay = self.config.retry_delay
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"尝试 {attempt + 1}/{self.config.max_retries} 失败: {e}"
                )

                if attempt < self.config.max_retries - 1:
                    self.logger.info(f"等待 {delay:.1f} 秒后重试...")
                    await asyncio.sleep(delay)
                    delay *= 2  # 指数退避

        self.logger.error(f"所有重试失败: {last_error}")
        raise last_error

    def _parse_json_fallback(self, text: str, schema: Optional[Dict] = None) -> dict:
        """
        JSON解析容错机制

        Args:
            text: 包含JSON的文本
            schema: 期望的JSON结构

        Returns:
            解析后的JSON对象
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取任何类似JSON的结构
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 如果都失败,返回错误信息
        self.logger.error(f"无法从响应中提取JSON: {text[:200]}...")
        return {"error": "JSON解析失败", "raw_text": text}


class OpenAIProvider(LLMProvider):
    """OpenAI GPT提供商"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not OPENAI_AVAILABLE:
            raise ImportError("请安装 openai: pip install openai>=1.3.0")

        self.client = AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout
        )
        self.logger.info(f"初始化 OpenAI 提供商,模型: {config.model}")

    async def _call_api(self, prompt: str, **kwargs) -> str:
        """调用OpenAI API"""
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            temperature=kwargs.get('temperature', self.config.temperature)
        )

        return response.choices[0].message.content

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        self.logger.debug(f"生成文本,提示词长度: {len(prompt)}")
        return await self._retry_with_backoff(self._call_api, prompt, **kwargs)

    async def generate_json(self, prompt: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """生成JSON"""
        # 添加JSON格式指令
        json_prompt = f"""{prompt}

请以有效的JSON格式返回结果。"""

        if schema:
            json_prompt += f"""
期望的JSON结构:
{json.dumps(schema, indent=2, ensure_ascii=False)}"""

        json_prompt += """

只返回JSON,不要包含其他文字。"""

        self.logger.debug(f"生成JSON,提示词长度: {len(json_prompt)}")

        response_text = await self._retry_with_backoff(self._call_api, json_prompt, **kwargs)

        # 解析JSON
        return self._parse_json_fallback(response_text, schema)


class GeminiProvider(LLMProvider):
    """Google Gemini提供商"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not GEMINI_AVAILABLE:
            raise ImportError("请安装 google-generativeai: pip install google-generativeai>=0.3.0")

        genai.configure(api_key=config.api_key)

        # 配置生成参数
        self.generation_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
        }

        self.model = genai.GenerativeModel(
            model_name=config.model,
            generation_config=self.generation_config
        )

        self.logger.info(f"初始化 Gemini 提供商,模型: {config.model}")

    async def _call_api(self, prompt: str, **kwargs) -> str:
        """调用Gemini API"""
        # Gemini 的 generate_content 是同步的,需要在线程池中运行
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )

        return response.text

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        self.logger.debug(f"生成文本,提示词长度: {len(prompt)}")
        return await self._retry_with_backoff(self._call_api, prompt, **kwargs)

    async def generate_json(self, prompt: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """生成JSON"""
        # 添加JSON格式指令
        json_prompt = f"""{prompt}

请以有效的JSON格式返回结果。"""

        if schema:
            json_prompt += f"""
期望的JSON结构:
{json.dumps(schema, indent=2, ensure_ascii=False)}"""

        json_prompt += """

只返回JSON,不要包含其他文字或解释。"""

        self.logger.debug(f"生成JSON,提示词长度: {len(json_prompt)}")

        response_text = await self._retry_with_backoff(self._call_api, json_prompt, **kwargs)

        # 解析JSON
        return self._parse_json_fallback(response_text, schema)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude提供商"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("请安装 anthropic: pip install anthropic>=0.7.0")

        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
        self.logger.info(f"初始化 Claude 提供商,模型: {config.model}")

    async def _call_api(self, prompt: str, **kwargs) -> str:
        """调用Claude API"""
        message = await self.client.messages.create(
            model=self.config.model,
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            temperature=kwargs.get('temperature', self.config.temperature),
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        self.logger.debug(f"生成文本,提示词长度: {len(prompt)}")
        return await self._retry_with_backoff(self._call_api, prompt, **kwargs)

    async def generate_json(self, prompt: str, schema: Optional[Dict] = None, **kwargs) -> dict:
        """生成JSON"""
        # 添加JSON格式指令
        json_prompt = f"""{prompt}

请以有效的JSON格式返回结果。"""

        if schema:
            json_prompt += f"""

期望的JSON结构:
{json.dumps(schema, indent=2, ensure_ascii=False)}"""

        json_prompt += """

重要:只返回JSON对象,不要包含任何其他文字、解释或markdown标记。"""

        self.logger.debug(f"生成JSON,提示词长度: {len(json_prompt)}")

        response_text = await self._retry_with_backoff(self._call_api, json_prompt, **kwargs)

        # 解析JSON
        return self._parse_json_fallback(response_text, schema)


class LLMFactory:
    """LLM工厂类"""

    # 注册的提供商
    _providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "anthropic": ClaudeProvider,  # 别名
    }

    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMProvider:
        """
        创建LLM提供商实例

        Args:
            provider: 提供商名称 ('openai', 'gemini', 'claude')
            api_key: API密钥
            model: 模型名称(可选,使用默认值)
            **kwargs: 其他配置参数

        Returns:
            LLMProvider实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider = provider.lower()

        if provider not in cls._providers:
            raise ValueError(
                f"不支持的提供商: {provider}. "
                f"支持的提供商: {list(cls._providers.keys())}"
            )

        # 设置默认模型
        if model is None:
            default_models = {
                "openai": "gpt-4-turbo-preview",
                "gemini": "gemini-pro",
                "claude": "claude-3-sonnet-20240229",
                "anthropic": "claude-3-sonnet-20240229",
            }
            model = default_models.get(provider)

        # 创建配置
        config = LLMConfig(
            api_key=api_key,
            model=model,
            max_tokens=kwargs.get('max_tokens', 4096),
            temperature=kwargs.get('temperature', 0.7),
            timeout=kwargs.get('timeout', 60),
            max_retries=kwargs.get('max_retries', 3),
            retry_delay=kwargs.get('retry_delay', 1.0)
        )

        # 创建提供商实例
        provider_class = cls._providers[provider]
        return provider_class(config)

    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> LLMProvider:
        """
        从配置字典创建LLM提供商

        Args:
            config_dict: 配置字典,包含provider和相关配置

        Returns:
            LLMProvider实例
        """
        provider = config_dict.get('provider', 'openai')
        api_key = config_dict.get('api_key')

        if not api_key:
            raise ValueError("API密钥不能为空")

        return cls.create(
            provider=provider,
            api_key=api_key,
            model=config_dict.get('model'),
            max_tokens=config_dict.get('max_tokens', 4096),
            temperature=config_dict.get('temperature', 0.7),
            timeout=config_dict.get('timeout', 60),
            max_retries=config_dict.get('max_retries', 3),
            retry_delay=config_dict.get('retry_delay', 1.0)
        )

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        注册自定义LLM提供商

        Args:
            name: 提供商名称
            provider_class: 提供商类(必须继承LLMProvider)
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError("提供商类必须继承LLMProvider")

        cls._providers[name.lower()] = provider_class
        logger.info(f"注册新的LLM提供商: {name}")


# 便捷函数
async def quick_generate(
    prompt: str,
    provider: str = "openai",
    api_key: Optional[str] = None,
    **kwargs
) -> str:
    """
    快速生成文本(便捷函数)

    Args:
        prompt: 提示词
        provider: 提供商名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        生成的文本
    """
    if not api_key:
        raise ValueError("需要提供API密钥")

    llm = LLMFactory.create(provider, api_key, **kwargs)
    return await llm.generate(prompt)


async def quick_generate_json(
    prompt: str,
    schema: Optional[Dict] = None,
    provider: str = "openai",
    api_key: Optional[str] = None,
    **kwargs
) -> dict:
    """
    快速生成JSON(便捷函数)

    Args:
        prompt: 提示词
        schema: JSON结构
        provider: 提供商名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        JSON对象
    """
    if not api_key:
        raise ValueError("需要提供API密钥")

    llm = LLMFactory.create(provider, api_key, **kwargs)
    return await llm.generate_json(prompt, schema)


if __name__ == "__main__":
    # 测试代码
    import os

    async def test_llm():
        """测试LLM工厂"""
        print("=== LLM Factory 测试 ===\n")

        # 测试OpenAI(如果有API密钥)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("1. 测试 OpenAI...")
            llm = LLMFactory.create("openai", openai_key)

            # 测试文本生成
            response = await llm.generate("用一句话介绍人工智能")
            print(f"响应: {response}\n")

            # 测试JSON生成
            json_response = await llm.generate_json(
                "列出3种编程语言及其特点",
                schema={"languages": [{"name": "", "features": []}]}
            )
            print(f"JSON响应: {json.dumps(json_response, indent=2, ensure_ascii=False)}\n")

        print("✅ 测试完成!")

    # 运行测试
    asyncio.run(test_llm())
