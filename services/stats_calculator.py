"""
Stats Calculator Service
Tính toán thống kê
"""
from datetime import datetime, timedelta
from config.database import db
from models.reading_session import ReadingSession


class StatsCalculator:
    """Tính toán thống kê"""

    @staticmethod
    def get_user_stats_by_date_range(user_id, days=7):
        """
        Lấy thống kê theo ngày
        Args:
            user_id: ID user
            days: Số ngày gần nhất
        Returns:
            dict: {labels: [], sessions: [], words: []}
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days - 1)

        # Query sessions theo ngày
        sessions_by_day = db.session.query(
            db.func.date(ReadingSession.created_at).label('date'),
            db.func.count(ReadingSession.id).label('count'),
            db.func.sum(ReadingSession.words_read).label('words')
        ).filter(
            ReadingSession.user_id == user_id,
            ReadingSession.created_at >= start_date
        ).group_by(db.func.date(ReadingSession.created_at)).all()

        # Format data
        labels = []
        counts = []
        words = []

        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            labels.append(date.strftime('%d/%m'))

            # Tìm data cho ngày này
            found = False
            for session in sessions_by_day:
                if str(session.date) == date_str:
                    counts.append(session.count)
                    words.append(session.words or 0)
                    found = True
                    break

            if not found:
                counts.append(0)
                words.append(0)

        return {
            'labels': labels,
            'sessions': counts,
            'words': words
        }

    @staticmethod
    def get_system_stats():
        """Thống kê toàn hệ thống (cho admin)"""
        from models.user import User
        from models.document import Document

        total_users = User.query.count()
        total_sessions = ReadingSession.query.count()
        total_documents = Document.query.count()

        # User mới 7 ngày
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users = User.query.filter(User.created_at >= week_ago).count()

        # Phiên đọc hôm nay
        today = datetime.utcnow().date()
        sessions_today = ReadingSession.query.filter(
            db.func.date(ReadingSession.created_at) == today
        ).count()

        return {
            'total_users': total_users,
            'new_users': new_users,
            'total_sessions': total_sessions,
            'sessions_today': sessions_today,
            'total_documents': total_documents
        }

    @staticmethod
    def format_time(seconds):
        """Format giây thành HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"