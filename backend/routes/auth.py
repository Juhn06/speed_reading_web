from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from config.database import db
from models.user import User
from utils.validators import validate_username, validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        valid, msg = validate_email(email)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Mật khẩu không khớp!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Tài khoản chưa tồn tại!', 'danger')
        elif not user.check_password(password):
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
        else:
            login_user(user, remember=remember)

            next_page = request.args.get('next')
            flash(f'Chào mừng trở lại, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('main.index'))
