from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import or_

from config.database import db
from config.settings import Config
from models.user import User
from models.document import Document
from models.reading_session import ReadingSession
from services.stats_calculator import StatsCalculator
from utils.decorators import admin_required
from utils.timezone import format_local_date, format_local_datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = StatsCalculator.get_system_stats()

    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

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
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    search = request.args.get('q', '', type=str).strip()
    role = request.args.get('role', 'all', type=str)
    sort_by = request.args.get('sort', 'newest', type=str)

    query = User.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(like),
                User.email.ilike(like)
            )
        )

    if role == 'admin':
        query = query.filter(User.is_admin.is_(True))
    elif role == 'user':
        query = query.filter(User.is_admin.is_(False))

    if sort_by == 'oldest':
        query = query.order_by(User.created_at.asc())
    elif sort_by == 'most_active':
        query = query.outerjoin(ReadingSession) \
            .group_by(User.id) \
            .order_by(db.func.count(ReadingSession.id).desc(), User.created_at.desc())
    else:
        query = query.order_by(User.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/users.html',
        pagination=pagination,
        filters={
            'q': search,
            'role': role,
            'sort': sort_by
        }
    )

@admin_bp.route('/user/<int:user_id>/details')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    stats = user.get_stats()
    recent_sessions = ReadingSession.query \
        .filter_by(user_id=user.id) \
        .order_by(ReadingSession.created_at.desc()) \
        .limit(5) \
        .all()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'created_at': format_local_date(user.created_at),
        'stats': {
            'total_sessions': stats.get('total_sessions', 0),
            'completed_sessions': stats.get('completed_sessions', 0),
            'total_words': stats.get('total_words', 0),
            'total_time': stats.get('total_time', 0),
            'avg_speed': stats.get('avg_speed', 0),
            'total_documents': stats.get('total_documents', 0)
        },
        'recent_sessions': [
            {
                'id': session.id,
                'filename': session.filename,
                'created_at': format_local_datetime(session.created_at, session.tz_offset, session.tz_name),
                'speed': session.speed,
                'completed': session.completed,
                'progress': session.get_completion_rate()
            }
            for session in recent_sessions
        ]
    })

@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    search = request.args.get('q', '', type=str).strip()
    file_type = request.args.get('type', 'all', type=str)
    sort_by = request.args.get('sort', 'newest', type=str)

    base_query = Document.query.join(User)

    if search:
        like = f"%{search}%"
        base_query = base_query.filter(
            or_(
                Document.original_filename.ilike(like),
                User.username.ilike(like)
            )
        )

    if file_type != 'all':
        base_query = base_query.filter(Document.file_type == file_type)

    total_docs = base_query.count()
    pdf_count = base_query.filter(Document.file_type == 'pdf').count()
    docx_count = base_query.filter(Document.file_type == 'docx').count()
    txt_count = base_query.filter(Document.file_type == 'txt').count()

    query = base_query
    if sort_by == 'oldest':
        query = query.order_by(Document.created_at.asc())
    elif sort_by == 'most_read':
        query = query.outerjoin(ReadingSession) \
            .group_by(Document.id) \
            .order_by(db.func.count(ReadingSession.id).desc(), Document.created_at.desc())
    elif sort_by == 'largest':
        query = query.order_by(Document.word_count.desc())
    else:
        query = query.order_by(Document.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/documents.html',
        pagination=pagination,
        stats={
            'total_docs': total_docs,
            'pdf_count': pdf_count,
            'docx_count': docx_count,
            'txt_count': txt_count
        },
        filters={
            'q': search,
            'type': file_type,
            'sort': sort_by
        }
    )

@admin_bp.route('/document/<int:doc_id>/details')
@login_required
@admin_required
def document_details(doc_id):
    doc = Document.query.get(doc_id)

    if not doc:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    recent_sessions = ReadingSession.query \
        .filter_by(document_id=doc.id) \
        .order_by(ReadingSession.created_at.desc()) \
        .limit(5) \
        .all()

    return jsonify({
        'id': doc.id,
        'filename': doc.original_filename,
        'file_type': doc.file_type,
        'word_count': doc.word_count,
        'created_at': format_local_date(doc.created_at, doc.tz_offset, doc.tz_name),
        'uploader': {
            'id': doc.user.id,
            'username': doc.user.username,
            'email': doc.user.email
        },
        'total_reads': doc.times_read(),
        'recent_sessions': [
            {
                'id': session.id,
                'user': session.user.username,
                'created_at': format_local_datetime(session.created_at, session.tz_offset, session.tz_name),
                'speed': session.speed,
                'duration': session.duration,
                'completed': session.completed,
                'progress': session.get_completion_rate()
            }
            for session in recent_sessions
        ]
    })

@admin_bp.route('/sessions')
@login_required
@admin_required
def sessions():
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    search = request.args.get('q', '', type=str).strip()
    status = request.args.get('status', 'all', type=str)
    date_filter = request.args.get('date', 'all', type=str)
    sort_by = request.args.get('sort', 'newest', type=str)

    query = ReadingSession.query.join(User)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(like),
                ReadingSession.filename.ilike(like)
            )
        )

    if status == 'completed':
        query = query.filter(ReadingSession.completed.is_(True))
    elif status == 'incomplete':
        query = query.filter(ReadingSession.completed.is_(False))

    if date_filter != 'all':
        now = datetime.now()
        if date_filter == 'today':
            start_date = datetime(now.year, now.month, now.day)
        elif date_filter == 'week':
            start_date = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
        elif date_filter == 'month':
            start_date = datetime(now.year, now.month, 1)
        else:
            start_date = None

        if start_date:
            query = query.filter(ReadingSession.created_at >= start_date)

    total_sessions = query.count()
    completed_count = query.filter(ReadingSession.completed.is_(True)).count()
    incomplete_count = query.filter(ReadingSession.completed.is_(False)).count()
    avg_speed = query.with_entities(db.func.avg(ReadingSession.speed)).scalar() or 0

    if sort_by == 'oldest':
        query = query.order_by(ReadingSession.created_at.asc())
    elif sort_by == 'fastest':
        query = query.order_by(ReadingSession.speed.desc())
    else:
        query = query.order_by(ReadingSession.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/sessions.html',
        pagination=pagination,
        stats={
            'total_sessions': total_sessions,
            'completed_count': completed_count,
            'incomplete_count': incomplete_count,
            'avg_speed': round(avg_speed)
        },
        filters={
            'q': search,
            'status': status,
            'date': date_filter,
            'sort': sort_by
        }
    )

@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Không tìm thấy!'}), 404

    if user.is_admin:
        return jsonify({'error': 'Không thể xóa admin!'}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Đã xóa user {user.username}!'})
