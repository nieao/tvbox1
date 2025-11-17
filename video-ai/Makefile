# Video-AI API Makefile

.PHONY: help install install-api test test-api run run-dev docker-build docker-run clean

help:
	@echo "Video-AI API - 可用命令:"
	@echo "  make install      - 安装所有依赖"
	@echo "  make install-api  - 仅安装 API 依赖"
	@echo "  make test         - 运行所有测试"
	@echo "  make test-api     - 运行 API 测试"
	@echo "  make run          - 启动生产服务器"
	@echo "  make run-dev      - 启动开发服务器（热重载）"
	@echo "  make docker-build - 构建 Docker 镜像"
	@echo "  make docker-run   - 运行 Docker 容器"
	@echo "  make docker-dev   - 启动开发环境"
	@echo "  make clean        - 清理临时文件"

install:
	pip install -r requirements.txt
	pip install -r requirements-api.txt

install-api:
	pip install -r requirements-api.txt

test:
	pytest tests/ -v

test-api:
	pytest tests/test_api.py -v

run:
	python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

run-dev:
	python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t video-ai-api:latest .

docker-run:
	docker run -d -p 8000:8000 --name video-ai-api video-ai-api:latest

docker-dev:
	docker-compose -f docker-compose.dev.yml up

docker-prod:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f api

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf /tmp/video-ai/*

format:
	black api/ src/ tests/
	isort api/ src/ tests/

lint:
	flake8 api/ src/ tests/
	pylint api/ src/ tests/

docs:
	@echo "API 文档地址:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc: http://localhost:8000/redoc"
	@echo "  完整文档: docs/API_DOCUMENTATION.md"
