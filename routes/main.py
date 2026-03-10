"""
Main routes
Trang chủ, giới thiệu
"""
from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Trang chủ"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    return render_template('home/index.html')

@main_bp.route('/about')
def about():
    """Giới thiệu"""
    return render_template('home/about.html')

from flask import redirect, url_for