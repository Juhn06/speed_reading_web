"""
Application settings
Centralized configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///speedreading.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

    # Pagination
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False