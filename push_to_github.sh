#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否安装Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}未安装Git，请先安装Git${NC}"
    exit 1
fi

# 检查是否有.git目录
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}初始化Git仓库...${NC}"
    git init
fi

# 检查远程仓库是否已配置
if ! git remote | grep -q "origin"; then
    echo -e "${YELLOW}请输入GitHub仓库地址：${NC}"
    read repo_url
    git remote add origin $repo_url
fi

# 创建.gitignore文件
echo -e "${YELLOW}创建.gitignore文件...${NC}"
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 项目特定
uploads/*
!uploads/.gitkeep
*.log
.env
*.db
*.sqlite3

# 临时文件
*.tmp
*.bak
*.swp
*~

# 测试文件
tests/
test_*.py
*_test.py

# 文档
docs/
*.md
!README.md

# 其他
.coverage
.pytest_cache/
.mypy_cache/
EOL

# 创建空的uploads目录
mkdir -p uploads
touch uploads/.gitkeep

# 清理远程仓库
echo -e "${YELLOW}清理远程仓库...${NC}"
git push origin --delete main 2>/dev/null || true

# 添加文件
echo -e "${YELLOW}添加文件到Git...${NC}"
git add .

# 提交更改
echo -e "${YELLOW}提交更改...${NC}"
git commit -m "Initial commit: 网络文件柜系统"

# 切换到main分支
git checkout -B main

# 强制推送到远程仓库
echo -e "${YELLOW}推送到GitHub...${NC}"
if git push -f origin main; then
    echo -e "${GREEN}推送成功！${NC}"
    echo -e "${GREEN}仓库地址：$(git remote get-url origin)${NC}"
else
    echo -e "${RED}推送失败，请检查GitHub仓库地址和权限${NC}"
    exit 1
fi

# 显示部署说明
echo -e "\n${GREEN}部署说明：${NC}"
echo "1. 克隆仓库："
echo "   git clone $(git remote get-url origin)"
echo "2. 进入目录："
echo "   cd CM-ADD"
echo "3. 运行部署脚本："
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"

# 检查必要文件
echo -e "\n${YELLOW}检查必要文件...${NC}"
required_files=(
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    "deploy.sh"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file 未找到${NC}"
    fi
done 