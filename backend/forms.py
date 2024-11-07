from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('记住我')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('电子邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='两次输入的密码不一致')
    ])

class ChangeDefaultPasswordForm(FlaskForm):
    new_username = StringField('新用户名', validators=[
        DataRequired(), 
        Length(min=3, max=20)
    ])
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=8, message='密码长度至少8个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的密码不一致')
    ])

class UploadFileForm(FlaskForm):
    file = FileField('文件', validators=[
        FileRequired(),
        FileAllowed(['csv', 'txt'], '只允许上传CSV和TXT文件')
    ]) 