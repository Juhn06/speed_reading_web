"""
Admin routes
Quản lý hệ thống
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from config.database import db
from config.settings import Config
from models.user import User
from models.document import Document
from models.reading_session import ReadingSession
from services.stats_calculator import StatsCalculator
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = StatsCalculator.get_system_stats()

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Recent sessions
    recent_sessions = ReadingSession.query \
        .order_by(ReadingSession.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_users=recent_users,
                           recent_sessions=recent_sessions)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Quản lý users"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE

    pagination = User.query.order_by(User.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/users.html', pagination=pagination)


@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    """Quản lý tài liệu"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE

    pagination = Document.query.order_by(Document.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/documents.html', pagination=pagination)


@admin_bp.route('/sessions')
@login_required
@admin_required
def sessions():
    """Quản lý phiên đọc"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE

    pagination = ReadingSession.query.order_by(ReadingSession.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/sessions.html', pagination=pagination)


@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Xóa user"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    if user.is_admin:
        return jsonify({'error': 'Không thể xóa admin!'}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Đã xóa user {user.username}!'})