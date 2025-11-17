"""
LLM 工厂使用示例

演示如何使用 LLM 工厂创建和使用不同的 LLM 提供商
"""

import os
import sys
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.llm_factory import LLMFactory


async def example_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "=" * 60)
    print("示例1: 基本文本生成")
    print("=" * 60 + "\n")

    # 从环境变量获取 API 密钥
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return

    # 创建 LLM 实例
    llm = LLMFactory.create(
        provider="openai",
        api_key=api_key,
        model="gpt-4-turbo-preview",
        temperature=0.7
    )

    # 生成文本
    prompt = "请用简单的语言解释什么是机器学习"

    print(f"提示词: {prompt}\n")
    print("生成中...\n")

    response = await llm.generate(prompt, max_tokens=200)

    print("响应:")
    print(response)


async def example_json_generation():
    """示例2: JSON 格式生成"""
    print("\n" + "=" * 60)
    print("示例2: JSON 格式生成")
    print("=" * 60 + "\n")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return

    llm = LLMFactory.create("openai", api_key, temperature=0.3)

    # 定义期望的 JSON 结构
    schema = {
        "topics": [
            {
                "title": "主题标题",
                "description": "主题描述",
                "keywords": ["关键词1", "关键词2"]
            }
        ]
    }

    prompt = """
    从以下文本中提取主要主题:

    "人工智能正在改变我们的生活。机器学习让计算机能够从数据中学习,
    深度学习使用神经网络解决复杂问题,自然语言处理帮助计算机理解人类语言。"
    """

    print("提示词:", prompt.strip())
    print("\n生成中...\n")

    result = await llm.generate_json(prompt, schema, max_tokens=500)

    print("JSON 结果:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


async def example_multi_provider():
    """示例3: 多提供商使用"""
    print("\n" + "=" * 60)
    print("示例3: 使用不同的 LLM 提供商")
    print("=" * 60 + "\n")

    providers = [
        ("openai", os.getenv("OPENAI_API_KEY")),
        ("gemini", os.getenv("GOOGLE_API_KEY")),
        ("claude", os.getenv("ANTHROPIC_API_KEY"))
    ]

    prompt = "用一句话描述人工智能"

    for provider_name, api_key in providers:
        if not api_key:
            print(f"⊘ 跳过 {provider_name} (未设置 API 密钥)\n")
            continue

        print(f"使用 {provider_name}...")

        try:
            llm = LLMFactory.create(provider_name, api_key)
            response = await llm.generate(prompt, max_tokens=100)

            print(f"  响应: {response}\n")
        except Exception as e:
            print(f"  错误: {e}\n")


async def example_config_dict():
    """示例4: 使用配置字典"""
    print("\n" + "=" * 60)
    print("示例4: 从配置字典创建")
    print("=" * 60 + "\n")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return

    # 配置字典(可以从配置文件加载)
    config = {
        "provider": "openai",
        "api_key": api_key,
        "model": "gpt-4-turbo-preview",
        "max_tokens": 2048,
        "temperature": 0.5,
        "max_retries": 3,
        "retry_delay": 1.0
    }

    print("配置:")
    for key, value in config.items():
        if key != "api_key":  # 不显示 API 密钥
            print(f"  {key}: {value}")

    # 从配置创建
    llm = LLMFactory.create_from_config(config)

    prompt = "列出3个编程语言"

    print(f"\n提示词: {prompt}\n")

    response = await llm.generate(prompt, max_tokens=150)

    print("响应:")
    print(response)


async def example_video_analysis():
    """示例5: 视频内容分析场景"""
    print("\n" + "=" * 60)
    print("示例5: 视频内容分析")
    print("=" * 60 + "\n")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return

    llm = LLMFactory.create("openai", api_key, temperature=0.3)

    # 模拟视频转录文本
    transcript = """
    [0:00] 大家好,今天我们来讨论机器学习的基础知识。
    [0:15] 机器学习是人工智能的一个重要分支,它让计算机能够从数据中学习模式。
    [0:45] 有三种主要的机器学习类型:监督学习、无监督学习和强化学习。
    [1:20] 监督学习使用标注的数据来训练模型,比如图像分类和语音识别。
    [2:00] 无监督学习从未标注的数据中发现模式,比如聚类和降维。
    [2:40] 强化学习通过试错来学习最佳策略,常用于游戏AI和机器人控制。
    """

    # 提取主题
    prompt = f"""
    从以下视频转录中提取主要主题:

    {transcript}

    请以JSON格式返回,包含每个主题的标题、描述和时间范围。
    """

    schema = {
        "topics": [
            {
                "title": "",
                "description": "",
                "start_time": "",
                "end_time": "",
                "keywords": []
            }
        ]
    }

    print("分析视频转录...\n")

    result = await llm.generate_json(prompt, schema)

    print("提取的主题:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("LLM 工厂使用示例")
    print("=" * 60)

    # 检查环境变量
    print("\n环境变量检查:")
    print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"  GOOGLE_API_KEY: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
    print(f"  ANTHROPIC_API_KEY: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")

    # 运行示例
    await example_basic_usage()
    await example_json_generation()
    await example_multi_provider()
    await example_config_dict()
    await example_video_analysis()

    print("\n" + "=" * 60)
    print("所有示例完成!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
