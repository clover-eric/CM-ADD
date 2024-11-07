# 网络文件柜系统

这是一个基于Flask和MySQL的网络文件柜系统，使用Docker进行容器化部署。

## 一键部署

## 功能特性

- 用户认证（登录/注册）
- 文件上传和下载
- 文件分类管理
- 文件共享功能
- 用户权限管理

## 技术栈

- 前端：HTML5, CSS3, JavaScript, Bootstrap 5
- 后端：Python Flask
- 数据库：MySQL 8.0
- 容器化：Docker

## 安装说明

```bash

curl -fsSL https://raw.githubusercontent.com/clover-eric/CM-ADD/main/deploy.sh | bash

```

或者使用以下命令手动部署：

```bash

git clone https://github.com/clover-eric/CM-ADD.git

cd CM-ADD

chmod +x deploy.sh

./deploy.sh

``` 

## 功能特性

- 用户认证（登录/注册）

- 文件上传和下载

- 文件分类管理

- 文件共享功能

- 用户权限管理

## 技术栈

- 前端：HTML5, CSS3, JavaScript, Bootstrap 5

- 后端：Python Flask

- 数据库：MySQL 8.0

- 容器化：Docker

## 系统要求

- Docker 20.10+

- Docker Compose 2.0+

- 2GB+ RAM

- 10GB+ 磁盘空间

## 部署说明

### 使用Docker Compose部署

1. 确保已安装 Docker 和 Docker Compose
2. 克隆项目代码
3. 在项目根目录运行：

  ```bash

  docker-compose up --build

  ```

4. 访问 http://localhost:5000 即可使用系统

### 开发环境配置

1. 安装Python 3.9+
2. 安装项目依赖：

  ```bash

  pip install -r requirements.txt

  ```

3. 配置环境变量
4. 运行开发服务器

## 默认账号

- 管理员账号：admin

- 默认密码：admin123

- 首次登录需修改密码

## 项目结构

file-cabinet/

├── frontend/

│ ├── static/

│ │ ├── css/

│ │ │ └── style.css

│ │ ├── js/

│ │ │ └── main.js

│ │ └── images/

│ └── templates/

│ ├── base.html

│ ├── login.html

│ └── dashboard.html

├── backend/

│ ├── init.py

│ ├── config.py

│ ├── models.py

│ ├── routes.py

│ └── utils.py

├── database/

│ └── init.sql

├── requirements.txt

├── Dockerfile

├── docker-compose.yml

└── README.md

Apply

Copy

## 目录说明

- frontend/: 前端代码

- backend/: Flask后端代码

- database/: 数据库相关文件

## 安全说明

- 所有密码都在.env文件中配置

- 数据库root密码随机生成

- 使用非root用户运行服务

- 限制容器资源使用

## 数据备份

bash

# 备份数据库

docker-compose exec db mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup.sql

# 备份上传文件

docker run --rm --volumes-from filecabinet_web_1 -v $(pwd):/backup ubuntu tar czf /backup/files.tar.gz /app/uploads

## 问题排查

如果遇到部署问题，请检查：

1. Docker服务是否正常运行
2. 端口5000是否被占用
3. 系统内存是否充足

## 贡献指南

欢迎提交Issue和Pull Request。

## 许可证

MIT License