#!/bin/bash
# Synapse 开发环境设置脚本

set -e

echo "=== Synapse 开发环境设置 ==="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "安装 Python..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-asyncio pytest-cov black ruff mypy

# 创建配置文件
if [ ! -f "config/local.yaml" ]; then
    echo "创建本地配置..."
    cp config/development.yaml config/local.yaml
fi

# 初始化数据库
echo "初始化数据库..."
python3 -c "from src.persistence.models import init_db; init_db()"

# 运行测试
echo "运行测试..."
pytest tests/ -v

echo ""
echo "=== 开发环境设置完成 ==="
echo ""
echo "启动开发服务器:"
echo "  source venv/bin/activate"
echo "  python -m src.start"
echo ""
echo "启动 API 服务:"
echo "  uvicorn src.api:app --reload"
