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

# 初始化数据库
flask db upgrade

# 创建默认管理员账号（如果不存在）
python -c "
from backend import create_app, db
from backend.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
        
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role=admin_role,
            is_active=True,
            is_first_login=True
        )
        db.session.add(admin)
        db.session.commit()
"

# 启动Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "backend:create_app()" 