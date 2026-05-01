from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

from config.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200), nullable=True)

    reading_sessions = db.relationship('ReadingSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_total_sessions(self):
        return self.reading_sessions.count()

    def get_completed_sessions(self):
        return self.reading_sessions.filter_by(completed=True).count()

    def get_total_words_read(self):
        total = db.session.query(db.func.sum(ReadingSession.words_read)) \
            .filter_by(user_id=self.id).scalar()
        return total or 0

    def get_total_time(self):
        total = db.session.query(db.func.sum(ReadingSession.duration)) \
            .filter_by(user_id=self.id).scalar()
        return total or 0

    def get_average_speed(self):
        avg = db.session.query(db.func.avg(ReadingSession.speed)) \
            .filter_by(user_id=self.id).scalar()
        return round(avg) if avg else 0

    def get_stats(self):
        return {
            'total_sessions': self.get_total_sessions(),
            'completed_sessions': self.get_completed_sessions(),
            'total_words': self.get_total_words_read(),
            'total_time': self.get_total_time(),
            'avg_speed': self.get_average_speed(),
            'total_documents': self.documents.count()
        }

from models.reading_session import ReadingSession
