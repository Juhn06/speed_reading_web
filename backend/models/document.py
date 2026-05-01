from datetime import datetime
from config.database import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_mime = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_hash = db.Column(db.String(64), nullable=True, index=True)
    storage_path = db.Column(db.String(400), nullable=True)
    file_data = db.Column(db.LargeBinary, nullable=True)
    word_count = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    tz_name = db.Column(db.String(64), nullable=True)
    tz_offset = db.Column(db.Integer, nullable=True)
    is_starred = db.Column(db.Boolean, default=False, index=True)

    sessions = db.relationship('ReadingSession', backref='document', lazy='dynamic')

    def __repr__(self):
        return f'<Document {self.original_filename}>'

    def times_read(self):
        return self.sessions.count()

    def get_words_list(self):
        return self.content.split()
