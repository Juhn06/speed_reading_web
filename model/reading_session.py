"""
ReadingSession model
Quản lý phiên đọc
"""
from datetime import datetime
from config.database import db


class ReadingSession(db.Model):
    """Model phiên đọc"""
    __tablename__ = 'reading_sessions'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    total_words = db.Column(db.Integer, nullable=False)
    words_read = db.Column(db.Integer, default=0)
    speed = db.Column(db.Integer, nullable=False)  # từ/phút
    duration = db.Column(db.Integer, default=0)  # giây
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ReadingSession {self.filename}>'

    def get_completion_rate(self):
        """Tỷ lệ hoàn thành (%)"""
        if self.total_words == 0:
            return 0
        return round((self.words_read / self.total_words) * 100, 1)

    def format_duration(self):
        """Format thời gian mm:ss"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"

    def format_created_at(self):
        """Format ngày giờ"""
        return self.created_at.strftime('%d/%m/%Y %H:%M')