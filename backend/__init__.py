from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@db/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # 配置登录
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from .auth import auth
    from .admin import admin
    from .routes import main
    
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(main)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_xhr:
            return jsonify({'status': 'error', 'message': '页面未找到'}), 404
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.is_xhr:
            return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
        return render_template('errors/500.html'), 500
        
    @app.errorhandler(413)
    def request_entity_too_large(error):
        if request.is_xhr:
            return jsonify({'status': 'error', 'message': '文件大小超过限制'}), 413
        return render_template('errors/413.html'), 413

# 用户加载��
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))