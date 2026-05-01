from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import hashlib

from config.database import db
from models.document import Document
from models.reading_session import ReadingSession
from services.file_handler import FileHandler
from services.text_processor import TextProcessor
from utils.timezone import get_request_tz_name, get_request_tz_offset
from flask import current_app

reading_bp = Blueprint('reading', __name__, url_prefix='/reading')

@reading_bp.route('/reader')
@login_required
def reader():
    return render_template('reading/reader.html')

@reading_bp.route('/train')
@login_required
def train():
    return render_template('reading/upload.html')

@reading_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file'}), 400

    if not FileHandler.allowed_file(file.filename):
        return jsonify({'error': 'Chỉ chấp nhận file .txt, .docx, .pdf'}), 400

    try:
        file_bytes = file.read()
        file_size = len(file_bytes)
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_mime = file.mimetype
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()

        storage_root = os.path.join(current_app.instance_path, 'storage')
        storage_rel = f"user_{current_user.id}/{file_hash}.{ext}"
        storage_path = os.path.join(storage_root, *storage_rel.split('/'))
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)

        wrote_storage = False
        if not os.path.exists(storage_path):
            with open(storage_path, 'wb') as f:
                f.write(file_bytes)
            wrote_storage = True

        text = FileHandler.read_file(storage_path)

        words = TextProcessor.split_into_words(text)

        if len(words) == 0:
            return jsonify({'error': 'File không có nội dung!'}), 400

        content = ' '.join(words)

        # Check for duplicate content attached to user
        existing_doc = Document.query.filter_by(
            user_id=current_user.id,
            original_filename=file.filename,
            content=content
        ).first()

        if existing_doc:
            if wrote_storage:
                FileHandler.delete_file(storage_path)
            return jsonify({
                'error': 'Trùng file. Vui lòng upload file khác.'
            }), 409

        # Do NOT create a persistent Document record yet. Return uploaded words and metadata
        # The client will call /reading/commit-upload when the user confirms (Bắt đầu đọc).
        return jsonify({
            'success': True,
            'words': words,
            'total': len(words),
            'filename': file.filename,
            'storage_rel': storage_rel,
            'file_hash': file_hash,
            'file_size': file_size,
            'file_mime': file_mime,
            'ext': ext
        })

    except Exception as e:
        if 'storage_path' in locals() and 'wrote_storage' in locals() and wrote_storage:
            FileHandler.delete_file(storage_path)
        return jsonify({'error': f'Lỗi xử lý file: {str(e)}'}), 500

@reading_bp.route('/load-document/<int:doc_id>')
@login_required
def load_document(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        return jsonify({'error': 'Không tìm thấy tài liệu!'}), 404

    words = doc.get_words_list()

    return jsonify({
        'success': True,
        'words': words,
        'total': len(words),
        'filename': doc.original_filename,
        'doc_id': doc.id
    })


@reading_bp.route('/document-content/<int:doc_id>')
@login_required
def document_content(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        return jsonify({'error': 'Không tìm thấy tài liệu!'}), 404

    # Try to read the original stored file if available, fall back to stored content
    try:
        if doc.storage_path:
            storage_abs = os.path.join(current_app.instance_path, 'storage', doc.storage_path)
            if os.path.exists(storage_abs):
                text = FileHandler.read_file(storage_abs)
                return jsonify({'success': True, 'text': text, 'filename': doc.original_filename, 'doc_id': doc.id})

        # fallback to content field
        return jsonify({'success': True, 'text': doc.content or '', 'filename': doc.original_filename, 'doc_id': doc.id})

    except Exception as e:
        return jsonify({'error': f'Lỗi đọc tài liệu: {str(e)}'}), 500

@reading_bp.route('/save-session', methods=['POST'])
@login_required
def save_session():
    data = request.json

    try:
        session = ReadingSession(
            user_id=current_user.id,
            document_id=data.get('doc_id'),
            filename=data.get('filename'),
            total_words=data.get('total_words'),
            words_read=data.get('words_read'),
            speed=data.get('speed'),
            duration=data.get('duration'),
            completed=data.get('completed', False),
            tz_name=get_request_tz_name(),
            tz_offset=get_request_tz_offset()
        )

        db.session.add(session)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Đã lưu phiên đọc!',
            'session_id': session.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reading_bp.route('/commit-upload', methods=['POST'])
@login_required
def commit_upload():
    data = request.json or {}
    storage_rel = data.get('storage_rel')
    original_filename = data.get('filename')

    if not storage_rel or not original_filename:
        return jsonify({'error': 'Thiếu thông tin upload.'}), 400

    storage_abs = os.path.join(current_app.instance_path, 'storage', storage_rel)
    if not os.path.exists(storage_abs):
        return jsonify({'error': 'File không tìm thấy trên server.'}), 404

    try:
        text = FileHandler.read_file(storage_abs)
        words = TextProcessor.split_into_words(text)
        if len(words) == 0:
            return jsonify({'error': 'File không có nội dung!'}), 400

        content = ' '.join(words)

        # prevent duplicates
        existing_doc = Document.query.filter_by(
            user_id=current_user.id,
            original_filename=original_filename,
            content=content
        ).first()
        if existing_doc:
            return jsonify({'error': 'Tài liệu đã tồn tại.'}), 409

        # infer ext/mime/size from file
        filename = secure_filename(original_filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        file_size = os.path.getsize(storage_abs)

        doc = Document(
            user_id=current_user.id,
            filename=filename,
            original_filename=original_filename,
            file_type=ext,
            file_mime=data.get('file_mime'),
            file_size=file_size,
            file_hash=data.get('file_hash'),
            storage_path=storage_rel,
            word_count=len(words),
            content=content,
            tz_name=get_request_tz_name(),
            tz_offset=get_request_tz_offset()
        )
        db.session.add(doc)
        db.session.commit()

        return jsonify({
            'success': True,
            'doc_id': doc.id,
            'words': words,
            'total': len(words),
            'filename': original_filename
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi khi lưu tài liệu: {str(e)}'}), 500
