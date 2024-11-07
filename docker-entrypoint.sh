#!/bin/bash
set -e

# 等待数据库就绪
echo "Waiting for database..."
max_retries=60
count=0

until MYSQL_PWD=$DB_PASSWORD mysql -h db -u $DB_USER -e "SELECT 1" $DB_NAME > /dev/null 2>&1
do
    echo "Database is unavailable - sleeping"
    count=$((count+1))
    if [ $count -gt $max_retries ]; then
        echo "Error: Timed out waiting for database"
        exit 1
    fi
    sleep 5
done

echo "Database is up - executing command"

# 初始化数据库
flask db upgrade

# 启动Gunicorn
exec gunicorn --bind 0.0.0.0:6789 --workers 4 --timeout 120 "backend:create_app()"