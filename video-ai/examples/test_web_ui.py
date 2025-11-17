"""
测试 Web UI 代码结构和依赖
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Video-AI Web UI 代码验证")
print("=" * 60)

# 测试核心模块导入
print("\n1. 测试核心模块导入...")

try:
    from src.core.editor import VideoEditor
    print("   ✅ VideoEditor")
except ImportError as e:
    print(f"   ❌ VideoEditor: {e}")

try:
    from src.services.personalization import PersonalizationConfig
    print("   ✅ PersonalizationConfig")
except ImportError as e:
    print(f"   ❌ PersonalizationConfig: {e}")

try:
    from src.utils.youtube_downloader import YouTubeDownloader
    print("   ✅ YouTubeDownloader")
except ImportError as e:
    print(f"   ❌ YouTubeDownloader: {e}")

# 测试配置创建
print("\n2. 测试配置创建...")

try:
    config = PersonalizationConfig(
        interests=["AI", "编程"],
        skip_topics=["广告"],
        output_length="medium",
        transition_style="text"
    )
    print(f"   ✅ 配置创建成功")
    print(f"   - 兴趣: {config.interests}")
    print(f"   - 跳过: {config.skip_topics}")
    print(f"   - 长度: {config.output_length}")
    print(f"   - 风格: {config.transition_style}")
except Exception as e:
    print(f"   ❌ 配置创建失败: {e}")

# 测试目录结构
print("\n3. 测试目录结构...")

directories = [
    project_root / "data",
    project_root / "data" / "input",
    project_root / "data" / "output",
    project_root / "data" / "temp",
]

for directory in directories:
    if directory.exists():
        print(f"   ✅ {directory}")
    else:
        print(f"   ⚠️  {directory} (不存在)")

# 检查依赖
print("\n4. 检查依赖安装...")

dependencies = [
    ("streamlit", "Streamlit Web 框架"),
    ("moviepy", "视频处理"),
    ("whisper", "语音识别"),
    ("yt_dlp", "YouTube 下载"),
]

for module_name, description in dependencies:
    try:
        __import__(module_name)
        print(f"   ✅ {module_name}: {description}")
    except ImportError:
        print(f"   ❌ {module_name}: {description} (未安装)")

# 检查系统命令
print("\n5. 检查系统依赖...")

import subprocess

commands = [
    ("ffmpeg", "视频处理工具"),
    ("python3", "Python 解释器"),
]

for cmd, description in commands:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ {cmd}: {description}")
        else:
            print(f"   ⚠️  {cmd}: {description} (可能有问题)")
    except FileNotFoundError:
        print(f"   ❌ {cmd}: {description} (未安装)")
    except Exception as e:
        print(f"   ⚠️  {cmd}: {description} ({e})")

# Web UI 文件检查
print("\n6. 检查 Web UI 文件...")

web_ui_file = project_root / "examples" / "web_ui.py"
readme_file = project_root / "examples" / "WEB_UI_README.md"
startup_script = project_root / "run_web_ui.sh"

files = [
    (web_ui_file, "Web UI 主文件"),
    (readme_file, "使用说明"),
    (startup_script, "启动脚本"),
]

for file_path, description in files:
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   ✅ {description}: {file_path.name} ({size} bytes)")
    else:
        print(f"   ❌ {description}: 不存在")

# 统计信息
print("\n7. 代码统计...")

if web_ui_file.exists():
    with open(web_ui_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

    print(f"   总行数: {total_lines}")
    print(f"   代码行: {code_lines}")
    print(f"   注释行: {comment_lines}")

# 总结
print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)

print("\n如果所有核心模块都安装成功，可以运行以下命令启动 Web UI:")
print("\n  方法 1: ./run_web_ui.sh")
print("  方法 2: streamlit run examples/web_ui.py")
print("\n如果缺少依赖，请运行:")
print("\n  pip install streamlit moviepy openai-whisper yt-dlp")
print("\n" + "=" * 60)
