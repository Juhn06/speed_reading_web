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

    # 🔥 IMPORT ROUTES
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.reading import reading_bp
    from routes.admin import admin_bp
    from routes.classes import class_bp        # ✅ thêm          # ✅ thêm

    # 🔥 REGISTER BLUEPRINT
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reading_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(class_bp)           # ✅ thêm

    # LOGIN
    from flask_login import LoginManager
    from backend.models import User

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # TIMEZONE
    @app.post('/timezone')
    def set_timezone():
        data = request.get_json(silent=True) or {}
        tz = data.get('tz')
        offset = data.get('offset')

        resp = jsonify({'ok': True})
        if tz:
            resp.set_cookie('tz', tz, max_age=31536000)
        if offset is not None:
            resp.set_cookie('tz_offset', str(offset), max_age=31536000)
        return resp

    @app.before_request
    def load_timezone():
        g.tz = get_request_timezone()

    app.template_filter('local_date')(format_local_date)
    app.template_filter('local_datetime')(format_local_datetime)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)