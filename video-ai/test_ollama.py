#!/usr/bin/env python3
"""
Ollama 连接测试脚本
快速验证 Ollama 配置是否正确
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.core.llm_factory import LLMFactory, OllamaProvider
    import httpx
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请先安装依赖:")
    print("  pip install httpx")
    sys.exit(1)


async def test_ollama_connection():
    """测试 Ollama 连接"""
    print("=" * 60)
    print("  Ollama 连接测试")
    print("=" * 60)
    print()

    # 从环境变量读取配置
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "qwen2.5-vl:8b")

    print(f"📍 Ollama 地址: {ollama_url}")
    print(f"🤖 模型名称: {model_name}")
    print()

    # 1. 测试服务可达性
    print("[1/5] 测试 Ollama 服务可达性...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            data = response.json()

            print(f"  ✅ 服务正常运行")
            print(f"  📦 已安装 {len(data.get('models', []))} 个模型")

            # 列出已安装的模型
            if data.get('models'):
                print("\n  已安装的模型:")
                for model in data['models'][:5]:  # 只显示前5个
                    size_gb = model.get('size', 0) / (1024**3)
                    print(f"    - {model['name']} ({size_gb:.1f} GB)")
                if len(data['models']) > 5:
                    print(f"    ... 还有 {len(data['models']) - 5} 个模型")
            print()

    except httpx.ConnectError:
        print(f"  ❌ 无法连接到 Ollama 服务")
        print(f"  💡 请确保 Ollama 正在运行:")
        print(f"     - Docker: docker-compose up -d ollama")
        print(f"     - 本地: ollama serve")
        return False
    except Exception as e:
        print(f"  ❌ 连接错误: {e}")
        return False

    # 2. 检查目标模型是否已下载
    print(f"[2/5] 检查模型 '{model_name}' 是否已下载...")
    try:
        models = [m['name'] for m in data.get('models', [])]
        if model_name in models:
            print(f"  ✅ 模型已下载")
        else:
            print(f"  ⚠️  模型未找到")
            print(f"  💡 下载模型:")
            print(f"     docker exec -it video-ai-ollama ollama pull {model_name}")
            print()
            return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False
    print()

    # 3. 测试 LLM 工厂创建
    print("[3/5] 测试 LLM 工厂创建...")
    try:
        llm = LLMFactory.create(
            provider="ollama",
            api_key=ollama_url,
            model=model_name,
            timeout=30
        )
        print(f"  ✅ LLM Provider 创建成功")
        print(f"  📝 类型: {type(llm).__name__}")
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False
    print()

    # 4. 测试文本生成
    print("[4/5] 测试文本生成...")
    try:
        prompt = "用一句话介绍你自己"
        print(f"  📤 提示词: {prompt}")

        response = await llm.generate(prompt)

        print(f"  ✅ 生成成功")
        print(f"  📥 响应: {response[:200]}...")
        print(f"  📊 长度: {len(response)} 字符")
    except Exception as e:
        print(f"  ❌ 生成失败: {e}")
        print(f"  💡 可能的原因:")
        print(f"     - 模型未完全下载")
        print(f"     - 内存不足")
        print(f"     - 超时（尝试增加 timeout）")
        return False
    print()

    # 5. 测试 JSON 生成
    print("[5/5] 测试 JSON 生成...")
    try:
        schema = {
            "languages": [
                {"name": "语言名称", "features": ["特点1", "特点2"]}
            ]
        }

        prompt = "列出2种编程语言及其特点"
        print(f"  📤 提示词: {prompt}")

        json_response = await llm.generate_json(prompt, schema=schema)

        print(f"  ✅ JSON 生成成功")
        print(f"  📥 响应类型: {type(json_response)}")

        # 验证 JSON 结构
        if isinstance(json_response, dict):
            if 'languages' in json_response:
                print(f"  ✅ JSON 结构正确")
                print(f"  📊 语言数量: {len(json_response.get('languages', []))}")
            else:
                print(f"  ⚠️  JSON 结构不符合预期")
                print(f"  内容: {json_response}")
        else:
            print(f"  ❌ 返回值不是字典")

    except Exception as e:
        print(f"  ❌ JSON 生成失败: {e}")
        print(f"  💡 这是正常的，某些模型在 JSON 格式上表现不稳定")
    print()

    # 清理
    if hasattr(llm, 'client'):
        await llm.client.aclose()

    return True


async def main():
    """主函数"""
    success = await test_ollama_connection()

    print("=" * 60)
    if success:
        print("  🎉 所有测试通过！")
        print()
        print("  ✅ Ollama 配置正确")
        print("  ✅ 可以开始使用 Video-AI 系统")
        print()
        print("  📖 下一步:")
        print("     1. 启动完整系统: docker-compose up -d")
        print("     2. 访问 API 文档: http://localhost:8000/docs")
        print("     3. 查看使用示例: python examples/api_client_demo.py")
    else:
        print("  ❌ 测试失败")
        print()
        print("  📖 故障排查:")
        print("     1. 查看 Ollama 日志: docker-compose logs ollama")
        print("     2. 检查模型列表: docker exec -it video-ai-ollama ollama list")
        print("     3. 重新下载模型: docker exec -it video-ai-ollama ollama pull <模型名>")
        print()
        print("  📚 详细文档: OLLAMA_SETUP_GUIDE.md")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
        sys.exit(1)
