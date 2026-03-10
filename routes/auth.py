"""
Auth routes
Đăng ký, đăng nhập, đăng xuất
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from config.database import db
from models.user import User
from utils.validators import validate_username, validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký tài khoản"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate username
        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        # Validate email
        valid, msg = validate_email(email)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        # Validate password
        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'danger')
            return redirect(url_for('auth.register'))

        # Check password match
        if password != confirm_password:
            flash('Mật khẩu không khớp!', 'danger')
            return redirect(url_for('auth.register'))

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('auth.register'))

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            flash(f'Chào mừng trở lại, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('user.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Đăng xuất"""
    logout_user()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('main'))