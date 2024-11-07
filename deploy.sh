#!/bin/bash

# 设置错误时退出
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查系统要求
echo -e "${YELLOW}检查系统要求...${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}未安装Docker，正在安装...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}未安装Docker Compose，正在安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 克隆项目
echo -e "${YELLOW}克隆项目代码...${NC}"
if [ ! -d "CM-ADD" ]; then
    git clone https://github.com/clover-eric/CM-ADD.git
    cd CM-ADD
else
    cd CM-ADD
    git pull
fi

# 生成环境变量
echo -e "${YELLOW}生成环境配置...${NC}"
if [ ! -f ".env" ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
    echo "DB_PASSWORD=$(openssl rand -hex 16)" >> .env
    echo "DB_NAME=filecabinet" >> .env
    echo "DB_USER=dbuser" >> .env
    echo "FLASK_ENV=production" >> .env
    echo "MAX_CONTENT_LENGTH=16777216" >> .env
fi

# 创建必要的目录
echo -e "${YELLOW}创建必要的目录...${NC}"
mkdir -p uploads
chmod 777 uploads

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
if ! docker-compose pull; then
    echo -e "${RED}拉取镜像失败，尝试使用备用镜像源...${NC}"
    # 如果官方镜像拉取失败，尝试使用阿里云镜像
    sed -i 's|image: mysql:8.0|image: registry.cn-hangzhou.aliyuncs.com/mysql/mysql:8.0|g' docker-compose.yml
    docker-compose pull
fi
docker-compose up --build -d

# 等待服务就绪
echo -e "${YELLOW}等待服务就绪...${NC}"
sleep 10

# 检查服务状态
if curl -s http://localhost:5000/health > /dev/null; then
    echo -e "${GREEN}部署成功！${NC}"
    echo -e "${GREEN}访问 http://localhost:5000 使用系统${NC}"
    echo -e "${YELLOW}默认管理员账号：admin${NC}"
    echo -e "${YELLOW}默认密码：admin123${NC}"
else
    echo -e "${RED}部署失败，请检查日志${NC}"
    docker-compose logs
fi

# 显示使用说明
echo -e "\n${GREEN}使用说明：${NC}"
echo "1. 首次登录请立即修改管理员密码"
echo "2. 查看日志：docker-compose logs -f"
echo "3. 停止服务：docker-compose down"
echo "4. 重启服务：docker-compose restart" 