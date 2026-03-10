"""
User routes
Dashboard, profile, history, documents
"""
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
from datetime import datetime, timedelta

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

    date_filter = request.args.get('date', 'all')
    status_filter = request.args.get('status', 'all')
    sort_filter = request.args.get('sort', 'newest')

    query = ReadingSession.query.filter_by(user_id=current_user.id)

    if status_filter == 'completed':
        query = query.filter_by(completed=True)
    elif status_filter == 'incomplete':
        query = query.filter_by(completed=False)

    if date_filter != 'all':
        now = datetime.now()
        if date_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == 'week':
            start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = None

        if start_date:
            query = query.filter(ReadingSession.created_at >= start_date)

    if sort_filter == 'oldest':
        query = query.order_by(ReadingSession.created_at.asc())
    elif sort_filter == 'speed':
        query = query.order_by(ReadingSession.speed.desc())
    else:
        query = query.order_by(ReadingSession.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('reading/history.html', pagination=pagination)


@user_bp.route('/documents')
@login_required
def documents():
    """Tài liệu đã lưu"""
    _dedupe_documents_for_user(current_user.id)
    docs = Document.query.filter_by(user_id=current_user.id) \
        .order_by(Document.created_at.desc()).all()

    return render_template('reading/documents.html', documents=docs)


def _dedupe_documents_for_user(user_id):
    """Remove duplicate documents for a user by original filename + content."""
    docs = Document.query.filter_by(user_id=user_id).order_by(Document.id.asc()).all()
    keep = {}
    removed = 0

    for doc in docs:
        key = (doc.original_filename, doc.content)
        if key in keep:
            ReadingSession.query.filter_by(user_id=user_id, document_id=doc.id).update(
                {ReadingSession.document_id: keep[key].id},
                synchronize_session=False
            )
            db.session.delete(doc)
            removed += 1
        else:
            keep[key] = doc

    if removed:
        db.session.commit()
    return removed


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

@user_bp.route('/avatar', methods=['POST'])
@login_required
def update_avatar():
    """Update user avatar"""
    if 'avatar' not in request.files:
        return jsonify({'error': 'Kh??ng c?? file'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Ch??a ch???n file'}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1].lower().lstrip('.')
    allowed = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())
    if ext not in allowed:
        return jsonify({'error': 'Ch??? ch???p nh???n ???nh PNG, JPG, JPEG, GIF, WEBP'}), 400

    avatar_dir = os.path.join(current_app.root_path, current_app.config['AVATAR_UPLOAD_FOLDER'])
    os.makedirs(avatar_dir, exist_ok=True)

    filename = f"user_{current_user.id}_{uuid4().hex}.{ext}"
    filepath = os.path.join(avatar_dir, filename)
    file.save(filepath)

    # Remove old avatar if exists
    if current_user.avatar:
        old_path = os.path.join(avatar_dir, current_user.avatar)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    current_user.avatar = filename
    db.session.commit()

    return jsonify({
        'success': True,
        'avatar_url': url_for('static', filename=f"uploads/avatars/{filename}")
    })
