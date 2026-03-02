.PHONY: help install test run clean lint format

help: ## 显示帮助信息
	@echo "可用命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -r requirements.txt

test: ## 运行测试
	pytest -v --cov=src --cov-report=term-missing

test-fast: ## 快速测试（无覆盖率）
	pytest -v

run: ## 启动服务
	cd src && python demo.py

lint: ## 代码检查
	flake8 src/ tests/ --max-line-length=100
	mypy src/ --ignore-missing-imports

format: ## 格式化代码
	black src/ tests/
	isort src/ tests/

clean: ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -f {} +
	rm -rf htmlcov/

setup: ## 首次设置
	pip install -r requirements.txt
	cp config/api_keys.example.json config/api_keys.json
	@echo "✅ 安装完成！请编辑 config/api_keys.json 填入你的API密钥"
