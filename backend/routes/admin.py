from flask import Blueprint, render_template, abort, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from backend.models import User, Document, ReadingSession, Class
from config.database import db
from sqlalchemy import extract

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ===== DASHBOARD =====
@admin_bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)

    stats = {
        'total_users': User.query.count(),
        'total_docs': Document.query.count(),
        'total_sessions': ReadingSession.query.count()
    }

    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_docs = Document.query.order_by(Document.id.desc()).limit(5).all()

    monthly_sessions = []
    monthly_docs = []
    monthly_users = []

    for m in range(1, 13):
        monthly_sessions.append(
            ReadingSession.query.filter(
                extract('month', ReadingSession.created_at) == m
            ).count()
        )
        monthly_docs.append(
            Document.query.filter(
                extract('month', Document.created_at) == m
            ).count()
        )
        monthly_users.append(
            User.query.filter(
                extract('month', User.created_at) == m
            ).count()
        )

    completed = ReadingSession.query.filter_by(completed=True).count()
    uncompleted = ReadingSession.query.filter_by(completed=False).count()
    classes_count = Class.query.count()

    from datetime import datetime as _dt, timedelta as _td
    current_year = _dt.utcnow().year

    # New users per day last 7 days
    today = _dt.utcnow().date()
    weekly_labels = []
    weekly_new_users = []
    for i in range(6, -1, -1):
        day = today - _td(days=i)
        cnt = User.query.filter(
            db.func.date(User.created_at) == day
        ).count()
        weekly_labels.append(day.strftime('%d/%m'))
        weekly_new_users.append(cnt)

    # New users per day last 30 days
    monthly_labels = []
    monthly_new_users = []
    for i in range(29, -1, -1):
        day = today - _td(days=i)
        cnt = User.query.filter(
            db.func.date(User.created_at) == day
        ).count()
        monthly_labels.append(day.strftime('%d/%m'))
        monthly_new_users.append(cnt)

    # New users per month this year
    yearly_labels = ['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12']
    yearly_new_users = []
    for m in range(1, 13):
        cnt = User.query.filter(
            extract('month', User.created_at) == m,
            extract('year',  User.created_at) == current_year
        ).count()
        yearly_new_users.append(cnt)

    # Top 5 users by sessions
    from sqlalchemy import func as _func
    top_readers = db.session.query(
        User,
        _func.count(ReadingSession.id).label('session_count'),
        _func.sum(ReadingSession.words_read).label('total_words')
    ).join(ReadingSession, ReadingSession.user_id == User.id)     .group_by(User.id)     .order_by(_func.count(ReadingSession.id).desc())     .limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_docs=recent_docs,
        monthly_sessions=monthly_sessions,
        monthly_docs=monthly_docs,
        monthly_users=monthly_users,
        completed=completed,
        uncompleted=uncompleted,
        classes_count=classes_count,
        current_year=current_year,
        weekly_labels=weekly_labels,
        weekly_new_users=weekly_new_users,
        monthly_labels=monthly_labels,
        monthly_new_users=monthly_new_users,
        yearly_labels=yearly_labels,
        yearly_new_users=yearly_new_users,
        top_readers=top_readers,
    )


# ===== LIST CLASS =====
@admin_bp.route('/classes')
@login_required
def classes():
    if not current_user.is_admin:
        abort(403)

    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)


# ===== CREATE CLASS =====
@admin_bp.route('/classes/create', methods=['POST'])
@login_required
def create_class():
    if not current_user.is_admin:
        abort(403)

    name = request.form.get('name')
    if not name:
        return "Tên lớp không được để trống"

    new_class = Class(name=name)
    db.session.add(new_class)
    db.session.commit()

    return redirect(url_for('admin.classes'))


# ===== DELETE CLASS =====
@admin_bp.route('/classes/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    if not current_user.is_admin:
        abort(403)

    class_obj = Class.query.get_or_404(class_id)

    # Xóa tất cả tài liệu trong lớp trước
    Document.query.filter_by(class_id=class_id).delete()

    db.session.delete(class_obj)
    db.session.commit()

    return redirect(url_for('admin.classes'))


# ===== CLASS DETAIL =====
@admin_bp.route('/classes/<int:class_id>')
@login_required
def class_detail(class_id):
    if not current_user.is_admin:
        abort(403)

    class_obj = Class.query.get_or_404(class_id)
    documents = Document.query.filter_by(class_id=class_id).all()

    return render_template(
        'admin/class_detail.html',
        class_obj=class_obj,
        documents=documents
    )


# ===== UPLOAD LESSON INTO CLASS =====
@admin_bp.route('/classes/<int:class_id>/upload', methods=['POST'])
@login_required
def upload_to_class(class_id):
    if not current_user.is_admin:
        abort(403)

    file = request.files.get('file')
    if not file:
        return "No file uploaded"

    import pdfplumber
    from docx import Document as DocxReader

    filename = file.filename
    ext = filename.split('.')[-1].lower()

    content = ""

    if ext == "txt":
        raw = file.read().replace(b'\x00', b'')
        content = raw.decode('utf-8', errors='ignore')

    elif ext == "pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content += page.extract_text() or ""

    elif ext == "docx":
        docx = DocxReader(file)
        content = "\n".join([p.text for p in docx.paragraphs])

    else:
        return "Không hỗ trợ file này"

    words = content.split()

    new_doc = Document(
        user_id=current_user.id,
        filename=filename,
        original_filename=filename,
        file_type=ext,
        word_count=len(words),
        content=content,
        class_id=class_id
    )

    db.session.add(new_doc)
    db.session.commit()

    return redirect(url_for('admin.class_detail', class_id=class_id))


# ===== DELETE DOCUMENT FROM CLASS =====
@admin_bp.route('/classes/<int:class_id>/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_class_document(class_id, doc_id):
    if not current_user.is_admin:
        abort(403)

    doc = Document.query.filter_by(id=doc_id, class_id=class_id).first_or_404()
    db.session.delete(doc)
    db.session.commit()

    return redirect(url_for('admin.class_detail', class_id=class_id))


# ===== LIST USERS =====
@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        abort(403)

    q = request.args.get('q', '').strip()
    role = request.args.get('role', 'all')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    query = User.query

    if q:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%')
            )
        )

    if role == 'admin':
        query = query.filter_by(is_admin=True)
    elif role == 'user':
        query = query.filter_by(is_admin=False)

    if sort == 'oldest':
        query = query.order_by(User.created_at.asc())
    else:
        query = query.order_by(User.created_at.desc())

    pagination = query.paginate(page=page, per_page=15, error_out=False)

    filters = {'q': q, 'role': role, 'sort': sort}

    return render_template('admin/users.html', pagination=pagination, filters=filters)


# ===== USER DETAIL API =====
@admin_bp.route('/users/<int:user_id>/detail')
@login_required
def user_detail(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    stats = user.get_stats()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'created_at': user.created_at.strftime('%d/%m/%Y %H:%M'),
        'stats': stats
    })


# ===== DELETE USER =====
@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)

    if user.is_admin:
        return jsonify({'error': 'Không thể xóa tài khoản Admin'}), 403

    if user.id == current_user.id:
        return jsonify({'error': 'Không thể tự xóa tài khoản của mình'}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True})


# ===== REPORT =====
@admin_bp.route('/report')
@login_required
def report():
    if not current_user.is_admin:
        abort(403)

    from datetime import datetime, timedelta

    # --- filters ---
    date_from_str = request.args.get('date_from', '')
    date_to_str   = request.args.get('date_to', '')
    user_id_str   = request.args.get('user_id', '')
    class_id_str  = request.args.get('class_id', '')
    page          = request.args.get('page', 1, type=int)

    date_from = None
    date_to   = None
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
        if date_to_str:
            date_to   = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        pass

    # --- KPI ---
    total_users    = User.query.count()
    total_docs     = Document.query.count()
    total_sessions = ReadingSession.query.count()
    avg_speed_raw  = db.session.query(db.func.avg(ReadingSession.speed)).scalar()
    avg_speed      = round(avg_speed_raw) if avg_speed_raw else 0
    completed_count   = ReadingSession.query.filter_by(completed=True).count()
    uncompleted_count = ReadingSession.query.filter_by(completed=False).count()

    # --- chart: sessions per month (current year) ---
    current_year = datetime.utcnow().year
    monthly = []
    for m in range(1, 13):
        cnt = ReadingSession.query.filter(
            extract('month', ReadingSession.created_at) == m,
            extract('year',  ReadingSession.created_at) == current_year
        ).count()
        monthly.append(cnt)

    # --- detail table query ---
    q = db.session.query(ReadingSession, User)\
        .join(User, ReadingSession.user_id == User.id)

    if date_from:
        q = q.filter(ReadingSession.created_at >= date_from)
    if date_to:
        q = q.filter(ReadingSession.created_at < date_to)
    if user_id_str:
        try:
            q = q.filter(ReadingSession.user_id == int(user_id_str))
        except ValueError:
            pass

    q = q.order_by(ReadingSession.created_at.desc())
    pagination = q.paginate(page=page, per_page=20, error_out=False)

    all_users   = User.query.order_by(User.username).all()
    all_classes = Class.query.order_by(Class.name).all()

    filters = {
        'date_from': date_from_str,
        'date_to':   date_to_str,
        'user_id':   user_id_str,
        'class_id':  class_id_str,
    }

    return render_template(
        'admin/report.html',
        total_users=total_users,
        total_docs=total_docs,
        total_sessions=total_sessions,
        avg_speed=avg_speed,
        completed_count=completed_count,
        uncompleted_count=uncompleted_count,
        monthly=monthly,
        pagination=pagination,
        all_users=all_users,
        all_classes=all_classes,
        filters=filters,
        current_year=current_year,
    )


# ===== EXPORT CSV =====
@admin_bp.route('/report/export')
@login_required
def export_report():
    if not current_user.is_admin:
        abort(403)

    from datetime import datetime, timedelta
    import csv, io
    from flask import Response

    date_from_str = request.args.get('date_from', '')
    date_to_str   = request.args.get('date_to', '')
    user_id_str   = request.args.get('user_id', '')

    date_from = None
    date_to   = None
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
        if date_to_str:
            date_to   = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        pass

    q = db.session.query(ReadingSession, User)\
        .join(User, ReadingSession.user_id == User.id)

    if date_from:
        q = q.filter(ReadingSession.created_at >= date_from)
    if date_to:
        q = q.filter(ReadingSession.created_at < date_to)
    if user_id_str:
        try:
            q = q.filter(ReadingSession.user_id == int(user_id_str))
        except ValueError:
            pass

    q = q.order_by(ReadingSession.created_at.desc())
    rows = q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Người dùng', 'Tài liệu', 'Tổng từ', 'Từ đã đọc',
                     'Tốc độ (từ/phút)', 'Thời gian (giây)', 'Hoàn thành', 'Ngày tạo'])

    for session, user in rows:
        writer.writerow([
            session.id,
            user.username,
            session.filename,
            session.total_words,
            session.words_read,
            session.speed,
            session.duration,
            'Có' if session.completed else 'Chưa',
            session.created_at.strftime('%d/%m/%Y %H:%M'),
        ])

    output.seek(0)
    filename = f"baocao_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        '\ufeff' + output.getvalue(),   # BOM for Excel UTF-8
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )