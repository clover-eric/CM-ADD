CREATE DATABASE IF NOT EXISTS filecabinet;
USE filecabinet;

CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_first_login BOOLEAN DEFAULT TRUE,
    api_key VARCHAR(64) UNIQUE,
    api_key_created_at TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(255) NOT NULL,
    user_id INT NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(50),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY user_file_unique (user_id)
);

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
);

CREATE INDEX idx_api_key ON users(api_key);

INSERT INTO roles (name, description) VALUES
('admin', '系统管理员'),
('user', '普通用户')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO users (username, email, password_hash, role_id, is_first_login) VALUES
('admin', 'admin@example.com', 'pbkdf2:sha256:260000$rMQd4IXBxRXrcvYw$41dacd778c83a8b5c1065c86e09755f9b19f8166f2f51c3ab0d4495f0e800ba6',
(SELECT id FROM roles WHERE name = 'admin'), TRUE)
ON DUPLICATE KEY UPDATE 
    email = VALUES(email),
    role_id = VALUES(role_id),
    is_first_login = VALUES(is_first_login);

DELIMITER //
CREATE TRIGGER IF NOT EXISTS update_file_modification_time
BEFORE UPDATE ON files
FOR EACH ROW
BEGIN
    SET NEW.last_modified = CURRENT_TIMESTAMP;
END//
DELIMITER ;

DELIMITER //
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

-- 在users表中添加管理员相关字段
ALTER TABLE users 
ADD COLUMN is_admin BOOLEAN DEFAULT FALSE,
ADD COLUMN is_active BOOLEAN DEFAULT TRUE,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN last_login TIMESTAMP;

-- 更新默认管理员账号
UPDATE users 
SET is_admin = TRUE, is_active = TRUE 
WHERE username = 'admin';