#!/bin/bash
set -e

# 等待数据库就绪
echo "Waiting for database..."
until python -c "import pymysql; pymysql.connect(host='db', user='$DB_USER', password='$DB_PASSWORD', database='$DB_NAME')" 2>/dev/null
do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "Database is up - executing command"

# 执行数据库初始化脚本
echo "Initializing database..."
chmod +x /app/database/init_db.sh
/app/database/init_db.sh

# 初始化数据库
flask db upgrade

# 启动Gunicorn
exec gunicorn --bind 0.0.0.0:6789 --workers 4 --timeout 120 "backend:create_app()" 