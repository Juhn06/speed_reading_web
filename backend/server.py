from pathlib import Path
import os
import sys

from flask import Flask, g, jsonify, request
from sqlalchemy import text

from config.database import db, migrate
from config.settings import Config
from utils.timezone import format_local_date, format_local_datetime, get_request_timezone

def _is_migration_command():
    migration_tokens = {
        'db', 'init', 'migrate', 'upgrade', 'downgrade', 'stamp',
        'revision', 'heads', 'current', 'history'
    }
    args = set(sys.argv[1:])
    return 'db' in args and bool(args.intersection(migration_tokens - {'db'}))

def create_app():
    project_root = Path(__file__).resolve().parent.parent
    frontend_dir = project_root / 'frontend'
    instance_dir = project_root / 'data' / 'instance'

    app = Flask(
        __name__,
        template_folder=str(frontend_dir / 'templates'),
        static_folder=str(frontend_dir / 'static'),
        instance_path=str(instance_dir),
        instance_relative_config=False
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.reading import reading_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reading_bp)
    app.register_blueprint(admin_bp)

    from flask_login import LoginManager
    from models.user import User

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.post('/timezone')
    def set_timezone():
        data = request.get_json(silent=True) or {}
        tz = data.get('tz')
        offset = data.get('offset')

        resp = jsonify({'ok': True})
        if tz:
            resp.set_cookie('tz', tz, max_age=31536000, samesite='Lax')
        if offset is not None:
            resp.set_cookie('tz_offset', str(offset), max_age=31536000, samesite='Lax')
        return resp

    @app.before_request
    def load_timezone():
        g.tz = get_request_timezone()

    app.template_filter('local_date')(format_local_date)
    app.template_filter('local_datetime')(format_local_datetime)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATAR_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'storage'), exist_ok=True)

    with app.app_context():
        if app.config.get('AUTO_CREATE_TABLES', False) and not _is_migration_command():
            db.create_all()

        if (
            db.engine.dialect.name == 'sqlite'
            and app.config.get('AUTO_SQLITE_COMPAT_PATCHES', True)
            and not _is_migration_command()
        ):
            _ensure_avatar_column()
            _ensure_document_star_column()
            _ensure_timezone_columns()
            _ensure_document_storage_columns()

    return app

def _ensure_avatar_column():
    engine = db.engine
    if engine.dialect.name != 'sqlite':
        return

    if not _sqlite_table_exists('users'):
        return

    columns = [row[1] for row in db.session.execute(text("PRAGMA table_info(users)")).fetchall()]
    if 'avatar' not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(200)"))
        db.session.commit()

def _ensure_document_star_column():
    engine = db.engine
    if engine.dialect.name != 'sqlite':
        return

    if not _sqlite_table_exists('documents'):
        return

    columns = [row[1] for row in db.session.execute(text("PRAGMA table_info(documents)")).fetchall()]
    if 'is_starred' not in columns:
        db.session.execute(text("ALTER TABLE documents ADD COLUMN is_starred BOOLEAN DEFAULT 0"))
        db.session.commit()

def _ensure_timezone_columns():
    engine = db.engine
    if engine.dialect.name != 'sqlite':
        return

    def ensure_column(table, column, column_type):
        if not _sqlite_table_exists(table):
            return

        cols = [row[1] for row in db.session.execute(text(f"PRAGMA table_info({table})")).fetchall()]
        if column not in cols:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
            db.session.commit()

    ensure_column('documents', 'tz_name', 'VARCHAR(64)')
    ensure_column('documents', 'tz_offset', 'INTEGER')
    ensure_column('reading_sessions', 'tz_name', 'VARCHAR(64)')
    ensure_column('reading_sessions', 'tz_offset', 'INTEGER')

def _ensure_document_storage_columns():
    engine = db.engine
    if engine.dialect.name != 'sqlite':
        return

    def ensure_column(table, column, column_type):
        if not _sqlite_table_exists(table):
            return

        cols = [row[1] for row in db.session.execute(text(f"PRAGMA table_info({table})")).fetchall()]
        if column not in cols:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
            db.session.commit()

    ensure_column('documents', 'file_mime', 'VARCHAR(100)')
    ensure_column('documents', 'file_size', 'INTEGER')
    ensure_column('documents', 'file_hash', 'VARCHAR(64)')
    ensure_column('documents', 'storage_path', 'VARCHAR(400)')
    ensure_column('documents', 'file_data', 'BLOB')

def _sqlite_table_exists(table_name):
    query = text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table")
    row = db.session.execute(query, {'table': table_name}).fetchone()
    return row is not None

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
