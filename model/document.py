"""
Document model
Quản lý tài liệu
"""
from datetime import datetime
from config.database import db


class Document(db.Model):
    """Model tài liệu"""
    __tablename__ = 'documents'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    sessions = db.relationship('ReadingSession', backref='document', lazy='dynamic')

    def __repr__(self):
        return f'<Document {self.original_filename}>'

    def times_read(self):
        """Số lần đã đọc"""
        return self.sessions.count()

    def get_words_list(self):
        """Lấy danh sách từ"""
        return self.content.split()