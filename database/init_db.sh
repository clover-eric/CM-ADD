#!/bin/bash

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}开始初始化数据库...${NC}"

# 等待MySQL服务就绪
until mysqladmin ping -h"db" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    echo -e "${YELLOW}等待数据库服务就绪...${NC}"
    sleep 2
done

echo -e "${GREEN}数据库服务已就绪${NC}"

# 创建数据库和用户
mysql -h"db" -u"$DB_USER" -p"$DB_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE $DB_NAME;

-- 删除已存在的触发器（如果有）
DROP TRIGGER IF EXISTS update_file_modification_time;
DROP TRIGGER IF EXISTS before_file_insert;

-- 创建表
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_first_login BOOLEAN DEFAULT TRUE,
    api_key VARCHAR(64) UNIQUE,
    api_key_created_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS file_shares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    shared_by INT NOT NULL,
    shared_with INT NOT NULL,
    share_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_time TIMESTAMP NULL,
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (shared_by) REFERENCES users(id),
    FOREIGN KEY (shared_with) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建索引
CREATE INDEX idx_api_key ON users(api_key);

-- 插入默认角色
INSERT INTO roles (name, description) VALUES
('admin', '系统管理员'),
('user', '普通用户')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 插入默认管理员账号
INSERT INTO users (username, email, password_hash, role_id, is_admin, is_active, is_first_login) VALUES
('admin', 'admin@example.com', 'pbkdf2:sha256:260000\$rMQd4IXBxRXrcvYw\$41dacd778c83a8b5c1065c86e09755f9b19f8166f2f51c3ab0d4495f0e800ba6',
(SELECT id FROM roles WHERE name = 'admin'), TRUE, TRUE, TRUE)
ON DUPLICATE KEY UPDATE 
    email = VALUES(email),
    role_id = VALUES(role_id),
    is_first_login = VALUES(is_first_login);

-- 创建触发器
DELIMITER //

CREATE TRIGGER update_file_modification_time
BEFORE UPDATE ON files
FOR EACH ROW
BEGIN
    SET NEW.last_modified = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER before_file_insert
BEFORE INSERT ON files
FOR EACH ROW
BEGIN
    DECLARE file_count INT;
    SELECT COUNT(*) INTO file_count FROM files WHERE user_id = NEW.user_id;
    IF file_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User already has a file in cabinet';
    END IF;
END//

DELIMITER ;

EOF

# 检查执行结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}数据库初始化成��！${NC}"
else
    echo -e "${RED}数据库初始化失败！${NC}"
    exit 1
fi 