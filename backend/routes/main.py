from flask import Blueprint, render_template

from config.database import db
from models.user import User
from models.reading_session import ReadingSession
from models.document import Document

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    total_users = User.query.count()
    total_sessions = ReadingSession.query.count()
    total_words_read = db.session.query(db.func.sum(ReadingSession.words_read)).scalar() or 0
    avg_speed = db.session.query(db.func.avg(ReadingSession.speed)).scalar()
    avg_speed = round(avg_speed) if avg_speed else 0
    total_documents = Document.query.count()

    stats = {
        'total_users': total_users,
        'total_sessions': total_sessions,
        'total_words_read': total_words_read,
        'avg_speed': avg_speed,
        'total_documents': total_documents
    }

    return render_template('home/index.html', stats=stats)

@main_bp.route('/about')
def about():
    return render_template('home/about.html')

from flask import redirect, url_for
