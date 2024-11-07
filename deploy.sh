#!/bin/bash

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 错误处理
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo -e "${RED}错误: 命令 ${last_command} 失败${NC}"' ERR

# 检查系统要求
echo -e "${YELLOW}检查系统要求...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}安装 Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}安装 Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 设置镜像加速
echo -e "${YELLOW}配置镜像加速...${NC}"
DOCKER_CONFIG_DIR="/etc/docker"
mkdir -p $DOCKER_CONFIG_DIR
cat > $DOCKER_CONFIG_DIR/daemon.json <<EOF
{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://registry.docker-cn.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com"
    ]
}
EOF
systemctl restart docker

# 克隆项目代码
echo -e "${YELLOW}克隆项目代码...${NC}"
if [ ! -d "CM-ADD" ]; then
    git clone https://github.com/clover-eric/CM-ADD.git
    cd CM-ADD
else
    cd CM-ADD
    git pull
fi

# 生成环境配置
echo -e "${YELLOW}生成环境配置...${NC}"
if [ ! -f ".env" ]; then
    cat > .env <<EOF
DB_NAME=filecabinet
DB_USER=dbuser
DB_PASSWORD=$(openssl rand -hex 16)
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
MAX_CONTENT_LENGTH=16777216
EOF
fi

# 创建必要的目录
echo -e "${YELLOW}创建必要的目录...${NC}"
mkdir -p uploads

# 预拉取基础镜像
echo -e "${YELLOW}预拉取基础镜像...${NC}"
docker pull mysql:8.0 &
docker pull python:3.9-slim &
wait

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose down -v
docker-compose build --parallel
docker-compose up -d

# 等待服务就绪
echo -e "${YELLOW}等待服务就绪...${NC}"
attempt=0
max_attempts=30
until curl -s http://localhost:5000/health > /dev/null || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo -e "${YELLOW}等待服务启动 ($attempt/$max_attempts)...${NC}"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}服务启动超时，请检查日志${NC}"
    docker-compose logs
    exit 1
fi

# 显示部署信息
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}访问地址: http://localhost:6789${NC}"
echo -e "${GREEN}默认管理员账号: admin${NC}"
echo -e "${GREEN}默认管理员密码: admin123${NC}"
echo -e "${YELLOW}请及时修改默认密码！${NC}"

# 显示系统信息
echo -e "\n${YELLOW}系统信息:${NC}"
docker-compose ps
echo -e "\n${YELLOW}如需查看日志，请运行:${NC}"
echo "docker-compose logs -f" 