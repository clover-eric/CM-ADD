from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from .models import db, User, File, Role
import os
import shutil

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_files = File.query.count()
    storage_used = sum(file.file_size for file in File.query.all())
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_files=total_files,
                         storage_used=storage_used)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
    })

@admin.route('/user/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        return jsonify({'status': 'error', 'message': '不能修改管理员账号'}), 403
    
    data = request.get_json()
    try:
        if User.query.filter(User.username == data['username'], 
                           User.id != user_id).first():
            return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
            
        if User.query.filter(User.email == data['email'], 
                           User.id != user_id).first():
            return jsonify({'status': 'error', 'message': '邮箱已被使用'}), 400
        
        user.username = data['username']
        user.email = data['email']
        user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '用户更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        return jsonify({'status': 'error', 'message': '不能删除管理员账号'}), 403
    
    try:
        # 删除用户的文件
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user.id))
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin.route('/system/reset', methods=['POST'])
@login_required
@admin_required
def system_reset():
    try:
        # 删除所有上传的文件
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            shutil.rmtree(upload_folder)
            os.makedirs(upload_folder)
        
        # 清空数据库表（除了角色表）
        File.query.delete()
        User.query.filter(User.username != 'admin').delete()
        
        # 重置管理员账号
        admin_user = User.query.filter_by(username='admin').first()
        admin_user.password_hash = generate_password_hash('123456')
        admin_user.is_first_login = True
        admin_user.api_key = None
        admin_user.api_key_created_at = None
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '系统重置成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin.route('/stats')
@login_required
@admin_required
def get_stats():
    active_users = User.query.filter_by(is_active=True).count()
    total_storage = sum(file.file_size for file in File.query.all())
    
    return jsonify({
        'active_users': active_users,
        'total_storage': total_storage,
        'total_files': File.query.count()
    })