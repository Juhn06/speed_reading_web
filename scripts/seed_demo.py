from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import app
from config.database import db
from models.user import User
from models.document import Document
from models.reading_session import ReadingSession

DEMO_USERS = [
    {
        "username": "admin_demo",
        "email": "admin_demo@example.com",
        "password": "Admin@123",
        "is_admin": True,
    },
    {
        "username": "demo_user",
        "email": "demo_user@example.com",
        "password": "Demo@123",
        "is_admin": False,
    },
    {
        "username": "demo_reader",
        "email": "demo_reader@example.com",
        "password": "Reader@123",
        "is_admin": False,
    },
]

def upsert_user(username: str, email: str, password: str, is_admin: bool) -> User:
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        return user

    user.email = email
    user.is_admin = is_admin
    user.set_password(password)
    db.session.flush()
    return user

def clear_user_data(user_id: int) -> None:
    ReadingSession.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    Document.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    db.session.flush()

def build_document(
    user_id: int,
    original_filename: str,
    content: str,
    file_type: str,
    days_ago: int,
    is_starred: bool = False,
) -> Document:
    payload = content.encode("utf-8")
    digest = sha256(payload).hexdigest()
    created_at = datetime.utcnow() - timedelta(days=days_ago)
    filename = original_filename.replace(" ", "_")
    return Document(
        user_id=user_id,
        filename=filename,
        original_filename=original_filename,
        file_type=file_type,
        file_mime="text/plain",
        file_size=len(payload),
        file_hash=digest,
        storage_path=None,
        word_count=len(content.split()),
        content=content,
        created_at=created_at,
        tz_name="Asia/Bangkok",
        tz_offset=420,
        is_starred=is_starred,
    )

def build_session(
    user_id: int,
    document: Document,
    speed: int,
    words_read: int,
    duration: int,
    completed: bool,
    days_ago: int,
) -> ReadingSession:
    return ReadingSession(
        user_id=user_id,
        document=document,
        filename=document.original_filename,
        total_words=document.word_count,
        words_read=words_read,
        speed=speed,
        duration=duration,
        completed=completed,
        created_at=datetime.utcnow() - timedelta(days=days_ago),
        tz_name="Asia/Bangkok",
        tz_offset=420,
    )

def seed_user_dataset(user: User) -> tuple[int, int]:
    if user.username == "demo_user":
        doc_primary = build_document(
            user.id,
            "focus_techniques.txt",
            (
                "Speed reading works best when your eyes move smoothly over phrases "
                "instead of stopping on every single word. Practice in short sessions, "
                "track progress, and increase pace gradually to keep comprehension high."
            ),
            "txt",
            days_ago=1,
            is_starred=True,
        )
        doc_secondary = build_document(
            user.id,
            "time_management_notes.txt",
            (
                "Before each reading session, define one clear goal and one stopping rule. "
                "This prevents endless skimming and improves retention by forcing active recall "
                "at the end of every section."
            ),
            "txt",
            days_ago=3,
        )
        db.session.add_all([doc_primary, doc_secondary])
        db.session.flush()

        sessions = [
            build_session(user.id, doc_primary, speed=320, words_read=doc_primary.word_count, duration=420, completed=True, days_ago=1),
            build_session(user.id, doc_primary, speed=350, words_read=int(doc_primary.word_count * 0.85), duration=300, completed=False, days_ago=0),
            build_session(user.id, doc_secondary, speed=290, words_read=doc_secondary.word_count, duration=380, completed=True, days_ago=3),
        ]
        db.session.add_all(sessions)
        return 2, 3

    if user.username == "demo_reader":
        doc = build_document(
            user.id,
            "daily_reading_plan.txt",
            (
                "A realistic reading plan uses fixed blocks, review checkpoints, and simple notes. "
                "Consistency over many days improves speed more than occasional long sessions."
            ),
            "txt",
            days_ago=2,
            is_starred=True,
        )
        db.session.add(doc)
        db.session.flush()

        session = build_session(
            user.id,
            doc,
            speed=275,
            words_read=doc.word_count,
            duration=360,
            completed=True,
            days_ago=2,
        )
        db.session.add(session)
        return 1, 1

    doc = build_document(
        user.id,
        "admin_overview.txt",
        (
            "This account is used to validate admin pages, user management, and "
            "system-wide statistics in the project demo environment."
        ),
        "txt",
        days_ago=4,
    )
    db.session.add(doc)
    db.session.flush()

    session = build_session(
        user.id,
        doc,
        speed=260,
        words_read=doc.word_count,
        duration=240,
        completed=True,
        days_ago=4,
    )
    db.session.add(session)
    return 1, 1

def main() -> None:
    with app.app_context():
        users = []
        for row in DEMO_USERS:
            users.append(
                upsert_user(
                    username=row["username"],
                    email=row["email"],
                    password=row["password"],
                    is_admin=row["is_admin"],
                )
            )
        db.session.flush()

        for user in users:
            clear_user_data(user.id)

        total_docs = 0
        total_sessions = 0
        for user in users:
            docs, sessions = seed_user_dataset(user)
            total_docs += docs
            total_sessions += sessions

        db.session.commit()
        print("Demo seed completed.")
        print(f"Users: {len(users)}")
        print(f"Documents: {total_docs}")
        print(f"Reading sessions: {total_sessions}")

if __name__ == "__main__":
    main()
