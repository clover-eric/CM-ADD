from flask_login import UserMixin
from . import db
from datetime import datetime
import secrets

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_first_login = db.Column(db.Boolean, default=True)
    api_key = db.Column(db.String(64), unique=True)
    api_key_created_at = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    
    files = db.relationship('File', backref='owner', lazy=True)
    shared_files = db.relationship('FileShare', foreign_keys='FileShare.shared_with',
                                 backref='shared_user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_admin(self):
        return self.role.name == 'admin'
    
    def generate_api_key(self):
        """生成新的API密钥"""
        self.api_key = secrets.token_urlsafe(32)
        self.api_key_created_at = datetime.utcnow()
        return self.api_key

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储的文件名
    filepath = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    shares = db.relationship('FileShare', backref='file', lazy=True)

    def __repr__(self):
        return f'<File {self.filename}>'

class FileShare(db.Model):
    __tablename__ = 'file_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    share_time = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_time = db.Column(db.DateTime, nullable=True)