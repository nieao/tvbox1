#!/bin/bash
# Video-AI Web UI 启动脚本

echo "================================"
echo "启动 Video-AI Web UI"
echo "================================"

# 进入项目目录
cd "$(dirname "$0")"

# 检查依赖
echo "检查依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查 Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "警告: 未安装 Streamlit"
    echo "安装中: pip install streamlit"
    pip install streamlit
fi

# 启动 Web UI
echo "启动 Streamlit 应用..."
echo "访问地址: http://localhost:8501"
echo "================================"
echo ""

streamlit run examples/web_ui.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
