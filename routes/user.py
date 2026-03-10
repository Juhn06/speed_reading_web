"""
User routes
Dashboard, profile, history, documents
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from config.database import db
from config.settings import Config
from models.reading_session import ReadingSession
from models.document import Document
from services.stats_calculator import StatsCalculator

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - trang upload"""
    # Thống kê
    stats = current_user.get_stats()

    # Lịch sử gần đây
    recent_sessions = ReadingSession.query.filter_by(user_id=current_user.id) \
        .order_by(ReadingSession.created_at.desc()).limit(5).all()

    # Tài liệu gần đây
    recent_docs = Document.query.filter_by(user_id=current_user.id) \
        .order_by(Document.created_at.desc()).limit(5).all()

    return render_template('reading/upload.html',
                           stats=stats,
                           recent_sessions=recent_sessions,
                           recent_docs=recent_docs)


@user_bp.route('/profile')
@login_required
def profile():
    """Trang cá nhân"""
    stats = current_user.get_stats()

    # Thống kê 7 ngày
    chart_data = StatsCalculator.get_user_stats_by_date_range(current_user.id, days=7)

    return render_template('auth/profile.html',
                           stats=stats,
                           chart_data=chart_data)


@user_bp.route('/history')
@login_required
def history():
    """Lịch sử đọc"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE

    pagination = ReadingSession.query.filter_by(user_id=current_user.id) \
        .order_by(ReadingSession.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('reading/history.html', pagination=pagination)


@user_bp.route('/documents')
@login_required
def documents():
    """Tài liệu đã lưu"""
    docs = Document.query.filter_by(user_id=current_user.id) \
        .order_by(Document.created_at.desc()).all()

    return render_template('reading/documents.html', documents=docs)


@user_bp.route('/delete-session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Xóa phiên đọc"""
    session = ReadingSession.query.filter_by(id=session_id, user_id=current_user.id).first()

    if not session:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    db.session.delete(session)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Đã xóa!'})


@user_bp.route('/delete-document/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    """Xóa tài liệu"""
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    db.session.delete(doc)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Đã xóa tài liệu!'})