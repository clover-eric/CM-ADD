import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, jsonify, current_app, send_file, session
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, File, User
from .forms import UploadFileForm
from .utils import allowed_file, generate_unique_filename, get_file_type_icon, format_file_size
from functools import wraps

main = Blueprint('main', __name__)

def csrf_protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            token = request.headers.get('X-CSRFToken')
            if not token or token != session.get('csrf_token'):
                return jsonify({'status': 'error', 'message': 'CSRF验证失败'}), 403
        return f(*args, **kwargs)
    return decorated_function

@main.before_request
def before_request():
    if 'csrf_token' not in session:
        session['csrf_token'] = os.urandom(32).hex()

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            # 检查用户是否已有文件
            existing_file = File.query.filter_by(user_id=current_user.id).first()
            if existing_file:
                flash('文件柜已有文件，请先清空文件柜', 'warning')
                return redirect(url_for('main.cabinet'))
            
            try:
                # 生成安全的文件名
                original_filename = secure_filename(file.filename)
                new_filename = generate_unique_filename(original_filename)
                
                # 确保上传目录存在
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                           str(current_user.id))
                os.makedirs(upload_folder, exist_ok=True)
                
                # 保存文件
                filepath = os.path.join(upload_folder, new_filename)
                file.save(filepath)
                
                # 创建文件记录
                new_file = File(
                    filename=original_filename,
                    stored_filename=new_filename,
                    filepath=filepath,
                    user_id=current_user.id,
                    file_size=os.path.getsize(filepath),
                    file_type=original_filename.rsplit('.', 1)[1].lower()
                )
                
                db.session.add(new_file)
                db.session.commit()
                
                flash('文件上传成功', 'success')
                return redirect(url_for('main.cabinet'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'文件上传失败：{str(e)}', 'danger')
                return redirect(url_for('main.upload'))
        else:
            flash('不支持的文件格式', 'danger')
    
    return render_template('upload.html', form=form)

@main.route('/cabinet')
@login_required
def cabinet():
    # 检查用户是否有文件
    file = File.query.filter_by(user_id=current_user.id).first()
    if not file:
        return redirect(url_for('main.upload'))
    
    return render_template('cabinet.html', 
                         file=file,
                         format_file_size=format_file_size)

@main.route('/clear-cabinet', methods=['POST'])
@login_required
def clear_cabinet():
    try:
        file = File.query.filter_by(user_id=current_user.id).first()
        if file:
            # 删除物理文件
            if os.path.exists(file.filepath):
                os.remove(file.filepath)
            
            # 删除数据库记录
            db.session.delete(file)
            db.session.commit()
            
            flash('文件柜已清空', 'success')
            return jsonify({'status': 'success', 'message': '文件柜已清空'})
        
        return jsonify({'status': 'error', 'message': '文件柜为空'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

@main.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('无权访问此文件', 'danger')
        return redirect(url_for('main.cabinet'))
    
    try:
        return send_file(
            file.filepath,
            as_attachment=True,
            download_name=file.filename
        )
    except Exception as e:
        flash(f'文件下载失败：{str(e)}', 'danger')
        return redirect(url_for('main.cabinet'))

@main.route('/api/generate_key', methods=['POST'])
@login_required
def generate_api_key():
    try:
        api_key = current_user.generate_api_key()
        db.session.commit()
        return jsonify({
            'status': 'success',
            'api_key': api_key,
            'created_at': current_user.api_key_created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/upload', methods=['POST'])
def api_upload():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'status': 'error', 'message': 'Missing API key'}), 401
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
    
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400
    
    # 检查用户是否已有文件
    existing_file = File.query.filter_by(user_id=user.id).first()
    if existing_file:
        return jsonify({'status': 'error', 'message': 'Cabinet not empty'}), 400
    
    try:
        filename = secure_filename(file.filename)
        new_filename = generate_unique_filename(filename)
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user.id))
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)
        
        new_file = File(
            filename=filename,
            stored_filename=new_filename,
            filepath=filepath,
            user_id=user.id,
            file_size=os.path.getsize(filepath),
            file_type=filename.rsplit('.', 1)[1].lower()
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'file_id': new_file.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/view/<int:file_id>')
@login_required
def view_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('无权访问此文件', 'danger')
        return redirect(url_for('main.cabinet'))
    
    try:
        # 读取文件内容
        with open(file.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根据文件类型返回不同的视图
        if file.file_type == 'csv':
            # CSV文件以表格形式显示
            import csv
            from io import StringIO
            csv_data = list(csv.reader(StringIO(content)))
            return render_template('view_csv.html', 
                                 filename=file.filename,
                                 headers=csv_data[0] if csv_data else [],
                                 rows=csv_data[1:])
        else:
            # TXT文件直接显示
            return render_template('view_text.html', 
                                 filename=file.filename,
                                 content=content)
    except Exception as e:
        flash(f'文件读取失败：{str(e)}', 'danger')
        return redirect(url_for('main.cabinet'))

@main.route('/health')
def health_check():
    try:
        # 测试数据库连接
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500