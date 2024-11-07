#!/bin/bash
set -e

echo "Waiting for database..."
max_retries=30
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
echo "Running database migrations..."
flask db upgrade || {
    echo "Database migration failed"
    exit 1
}

# 启动应用
echo "Starting application..."
exec gunicorn \
    --bind 0.0.0.0:6789 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "backend:create_app()"