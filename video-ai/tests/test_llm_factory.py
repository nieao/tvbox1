"""
测试 LLM 工厂模式

测试所有LLM提供商的基本功能
"""

import os
import sys
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.llm_factory import LLMFactory, LLMConfig


async def test_llm_creation():
    """测试 LLM 创建"""
    print("\n=== 测试 LLM 工厂创建 ===\n")

    # 测试 OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✓ 创建 OpenAI 提供商...")
        llm = LLMFactory.create("openai", api_key, model="gpt-4-turbo-preview")
        print(f"  模型: {llm.config.model}")
        print(f"  Max tokens: {llm.config.max_tokens}")
        print(f"  Temperature: {llm.config.temperature}")
    else:
        print("✗ 未设置 OPENAI_API_KEY,跳过 OpenAI 测试")

    # 测试 Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        print("\n✓ 创建 Gemini 提供商...")
        llm = LLMFactory.create("gemini", google_key)
        print(f"  模型: {llm.config.model}")
    else:
        print("\n✗ 未设置 GOOGLE_API_KEY,跳过 Gemini 测试")

    # 测试 Claude
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("\n✓ 创建 Claude 提供商...")
        llm = LLMFactory.create("claude", anthropic_key)
        print(f"  模型: {llm.config.model}")
    else:
        print("\n✗ 未设置 ANTHROPIC_API_KEY,跳过 Claude 测试")


async def test_text_generation():
    """测试文本生成"""
    print("\n=== 测试文本生成 ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ 需要 OPENAI_API_KEY 进行测试")
        return

    llm = LLMFactory.create("openai", api_key, temperature=0.5)

    prompt = "用一句话解释什么是人工智能"
    print(f"提示词: {prompt}")
    print("生成中...")

    try:
        response = await llm.generate(prompt, max_tokens=100)
        print(f"\n响应: {response}\n")
        print("✓ 文本生成成功")
    except Exception as e:
        print(f"✗ 文本生成失败: {e}")


async def test_json_generation():
    """测试 JSON 生成"""
    print("\n=== 测试 JSON 生成 ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ 需要 OPENAI_API_KEY 进行测试")
        return

    llm = LLMFactory.create("openai", api_key, temperature=0.3)

    prompt = "列出3种常见的编程语言及其主要特点"

    schema = {
        "languages": [
            {
                "name": "",
                "features": []
            }
        ]
    }

    print(f"提示词: {prompt}")
    print(f"期望结构: {schema}")
    print("生成中...")

    try:
        response = await llm.generate_json(prompt, schema, max_tokens=500)
        print(f"\nJSON响应:")
        import json
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("\n✓ JSON生成成功")
    except Exception as e:
        print(f"✗ JSON生成失败: {e}")


async def test_retry_mechanism():
    """测试重试机制"""
    print("\n=== 测试重试机制 ===\n")

    # 使用无效的 API 密钥测试重试
    print("使用无效密钥测试(预期失败)...")

    try:
        llm = LLMFactory.create(
            "openai",
            "invalid_key",
            max_retries=2,
            retry_delay=0.5
        )

        await llm.generate("测试", max_tokens=10)
        print("✗ 应该失败但成功了")
    except Exception as e:
        print(f"✓ 按预期失败: {type(e).__name__}")


async def test_from_config():
    """测试从配置字典创建"""
    print("\n=== 测试配置字典创建 ===\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ 需要 OPENAI_API_KEY 进行测试")
        return

    config = {
        "provider": "openai",
        "api_key": api_key,
        "model": "gpt-4-turbo-preview",
        "max_tokens": 2048,
        "temperature": 0.7,
        "max_retries": 3
    }

    print("配置字典:")
    print(f"  Provider: {config['provider']}")
    print(f"  Model: {config['model']}")

    llm = LLMFactory.create_from_config(config)

    print(f"\n✓ 成功创建: {llm.config.model}")


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("LLM Factory 测试套件")
    print("=" * 60)

    # 检查环境变量
    print("\n环境变量检查:")
    print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"  GOOGLE_API_KEY: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
    print(f"  ANTHROPIC_API_KEY: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")

    # 运行测试
    await test_llm_creation()
    await test_from_config()
    await test_text_generation()
    await test_json_generation()
    await test_retry_mechanism()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
