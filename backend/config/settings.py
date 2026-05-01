import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
INSTANCE_DIR = DATA_DIR / 'instance'
UPLOAD_DIR = DATA_DIR / 'uploads'
AVATAR_DIR = FRONTEND_DIR / 'static' / 'uploads' / 'avatars'
DEFAULT_DB_PATH = INSTANCE_DIR / 'speedreading.db'

load_dotenv(PROJECT_ROOT / '.env')

def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}

def _normalize_database_url(database_url):
    if database_url.startswith('mysql://'):
        return database_url.replace('mysql://', 'mysql+pymysql://', 1)
    if database_url.startswith('postgres://'):
        return database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    if database_url.startswith('postgresql://'):
        return database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return database_url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get('DATABASE_URL') or f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    if SQLALCHEMY_DATABASE_URI.startswith('mysql'):
        SQLALCHEMY_ENGINE_OPTIONS['pool_recycle'] = 1800

    AUTO_CREATE_TABLES = _env_bool('AUTO_CREATE_TABLES', False)
    AUTO_SQLITE_COMPAT_PATCHES = _env_bool('AUTO_SQLITE_COMPAT_PATCHES', True)

    UPLOAD_FOLDER = str(UPLOAD_DIR)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    AVATAR_UPLOAD_FOLDER = str(AVATAR_DIR)
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
