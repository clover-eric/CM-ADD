from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .forms import LoginForm, RegisterForm, ChangeDefaultPasswordForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已被注册', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/change_default_password', methods=['POST'])
@login_required
def change_default_password():
    if not current_user.is_first_login:
        return jsonify({'status': 'error', 'message': '非首次登录用户'}), 403
    
    form = ChangeDefaultPasswordForm()
    if form.validate_on_submit():
        # 检查新用户名是否已存在
        if form.new_username.data != current_user.username and \
           User.query.filter_by(username=form.new_username.data).first():
            return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
        
        try:
            current_user.username = form.new_username.data
            current_user.password_hash = generate_password_hash(form.new_password.data)
            current_user.is_first_login = False
            db.session.commit()
            return jsonify({'status': 'success', 'message': '密码修改成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'error', 'message': form.errors}), 400 