"""
Custom decorators
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator yêu cầu quyền admin
    Usage: @admin_required
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập!', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('main'))

        return f(*args, **kwargs)

    return decorated_function