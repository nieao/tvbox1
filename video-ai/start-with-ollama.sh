#!/bin/bash

# Video-AI with Ollama 一键启动脚本
# 自动下载模型并启动所有服务

set -e

echo "========================================="
echo "  Video-AI + Ollama 一键启动"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker
echo -e "${YELLOW}[1/6]${NC} 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误: 未安装 Docker${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 错误: 未安装 Docker Compose${NC}"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境正常${NC}"
echo ""

# 检查 .env 文件
echo -e "${YELLOW}[2/6]${NC} 检查配置文件..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，从模板创建...${NC}"
    cp .env.example .env

    echo ""
    echo -e "${YELLOW}⚙️  请配置以下关键参数:${NC}"
    read -p "数据库密码 (DB_PASSWORD): " db_pass
    read -p "MongoDB 密码 (MONGO_PASSWORD): " mongo_pass
    read -p "Redis 密码 (REDIS_PASSWORD): " redis_pass

    # 使用 sed 替换密码（兼容 macOS 和 Linux）
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/DB_PASSWORD=.*/DB_PASSWORD=$db_pass/" .env
        sed -i '' "s/MONGO_PASSWORD=.*/MONGO_PASSWORD=$mongo_pass/" .env
        sed -i '' "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$redis_pass/" .env
    else
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_pass/" .env
        sed -i "s/MONGO_PASSWORD=.*/MONGO_PASSWORD=$mongo_pass/" .env
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$redis_pass/" .env
    fi

    echo -e "${GREEN}✅ 配置文件已创建${NC}"
else
    echo -e "${GREEN}✅ 配置文件已存在${NC}"
fi
echo ""

# 询问模型选择
echo -e "${YELLOW}[3/6]${NC} 选择 Ollama 模型..."
echo ""
echo "可用模型："
echo "  1) qwen2.5-vl:8b (推荐，多模态，5GB)"
echo "  2) qwen2.5:7b (中文优化，4.7GB)"
echo "  3) llama3.2:3b (轻量级，2GB)"
echo "  4) llama3.1:8b (通用，4.7GB)"
echo "  5) 自定义"
echo ""
read -p "请选择模型 [1-5] (默认: 1): " model_choice
model_choice=${model_choice:-1}

case $model_choice in
    1) MODEL_NAME="qwen2.5-vl:8b" ;;
    2) MODEL_NAME="qwen2.5:7b" ;;
    3) MODEL_NAME="llama3.2:3b" ;;
    4) MODEL_NAME="llama3.1:8b" ;;
    5)
        read -p "请输入模型名称（例如 mistral:7b）: " MODEL_NAME
        ;;
    *)
        echo -e "${YELLOW}使用默认模型: qwen2.5-vl:8b${NC}"
        MODEL_NAME="qwen2.5-vl:8b"
        ;;
esac

echo -e "${GREEN}✅ 已选择模型: $MODEL_NAME${NC}"

# 更新 .env 中的模型配置
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/LLM_MODEL=.*/LLM_MODEL=$MODEL_NAME/" .env
else
    sed -i "s/LLM_MODEL=.*/LLM_MODEL=$MODEL_NAME/" .env
fi
echo ""

# 启动服务
echo -e "${YELLOW}[4/6]${NC} 启动 Docker 服务..."
docker-compose up -d

echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# 等待 Ollama 就绪
echo -e "${YELLOW}[5/6]${NC} 等待 Ollama 服务就绪..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec video-ai-ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama 服务已就绪${NC}"
        break
    fi

    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Ollama 服务启动超时${NC}"
    echo "请检查日志: docker-compose logs ollama"
    exit 1
fi
echo ""

# 下载模型
echo -e "${YELLOW}[6/6]${NC} 下载 Ollama 模型: $MODEL_NAME"
echo -e "${YELLOW}⏳ 这可能需要几分钟，请耐心等待...${NC}"
echo ""

if docker exec video-ai-ollama ollama pull "$MODEL_NAME"; then
    echo ""
    echo -e "${GREEN}✅ 模型下载完成${NC}"
else
    echo ""
    echo -e "${RED}❌ 模型下载失败${NC}"
    echo "请手动运行: docker exec -it video-ai-ollama ollama pull $MODEL_NAME"
fi
echo ""

# 测试模型
echo -e "${YELLOW}🧪 测试模型...${NC}"
test_response=$(docker exec video-ai-ollama ollama run "$MODEL_NAME" "你好" 2>&1 | head -n 5)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 模型测试成功${NC}"
    echo "响应预览: $test_response"
else
    echo -e "${YELLOW}⚠️  模型测试失败，但可能已经下载完成${NC}"
fi
echo ""

# 完成
echo "========================================="
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "========================================="
echo ""
echo "📌 服务访问地址："
echo "   - API 服务:    http://localhost:8000"
echo "   - API 文档:    http://localhost:8000/docs"
echo "   - Ollama API:  http://localhost:11434"
echo "   - Grafana:     http://localhost:3000"
echo ""
echo "📌 使用的模型: $MODEL_NAME"
echo ""
echo "📌 常用命令："
echo "   - 查看日志:     docker-compose logs -f"
echo "   - 停止服务:     docker-compose down"
echo "   - 重启服务:     docker-compose restart"
echo "   - 测试模型:     docker exec -it video-ai-ollama ollama run $MODEL_NAME"
echo "   - 切换模型:     docker exec -it video-ai-ollama ollama pull <模型名>"
echo ""
echo "📖 详细文档: OLLAMA_SETUP_GUIDE.md"
echo ""
echo -e "${GREEN}开始使用吧！ 🚀${NC}"
