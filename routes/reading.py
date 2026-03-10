"""
Reading routes
Upload, đọc, lưu phiên
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from config.database import db
from models.document import Document
from models.reading_session import ReadingSession
from services.file_handler import FileHandler
from services.text_processor import TextProcessor

reading_bp = Blueprint('reading', __name__, url_prefix='/reading')


@reading_bp.route('/reader')
@login_required
def reader():
    """Trang đọc"""
    return render_template('reading/reader.html')


@reading_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload file"""
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file'}), 400

    if not FileHandler.allowed_file(file.filename):
        return jsonify({'error': 'Chỉ chấp nhận file .txt, .docx, .pdf'}), 400

    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Read content
        text = FileHandler.read_file(filepath)

        # Delete temp file
        FileHandler.delete_file(filepath)

        # Process text
        words = TextProcessor.split_into_words(text)

        if len(words) == 0:
            return jsonify({'error': 'File không có nội dung!'}), 400

        content = ' '.join(words)

        # Deduplicate by original filename + content for this user
        existing_doc = Document.query.filter_by(
            user_id=current_user.id,
            original_filename=file.filename,
            content=content
        ).first()

        if existing_doc:
            return jsonify({
                'error': 'Trung file. Vui long upload file khac.'
            }), 409

        # Save document to database
        doc = Document(
            user_id=current_user.id,
            filename=filename,
            original_filename=file.filename,
            file_type=filename.rsplit('.', 1)[1].lower(),
            word_count=len(words),
            content=content
        )
        db.session.add(doc)
        db.session.commit()

        return jsonify({
            'success': True,
            'words': words,
            'total': len(words),
            'filename': file.filename,
            'doc_id': doc.id
        })

    except Exception as e:
        if 'filepath' in locals():
            FileHandler.delete_file(filepath)
        return jsonify({'error': f'Lỗi xử lý file: {str(e)}'}), 500


@reading_bp.route('/load-document/<int:doc_id>')
@login_required
def load_document(doc_id):
    """Load tài liệu đã lưu"""
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


@reading_bp.route('/save-session', methods=['POST'])
@login_required
def save_session():
    """Lưu phiên đọc"""
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
            completed=data.get('completed', False)
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
