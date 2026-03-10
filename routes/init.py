"""
Routes package
All blueprints
"""
from routes.auth import auth_bp
from routes.main import main_bp
from routes.reading import reading_bp
from routes.user import user_bp
from routes.admin import admin_bp

__all__ = ['auth_bp', 'main_bp', 'reading_bp', 'user_bp', 'admin_bp']