import os
from datetime import timedelta

class Config:
    # Secret key for session signing
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///skillswap.db'
    
    # Fix for SQLite connections on Render - convert postgres:// to postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload

    # CSRF settings - relaxed for development
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_SSL_STRICT = False  # Allows HTTP -> HTTPS and vice versa
    
    # Only set SERVER_NAME if needed - can cause routing issues
    SERVER_NAME = os.environ.get('SERVER_NAME') or os.environ.get('HOSTNAME') or "localhost:8000"
    
    # This is safer than using SERVER_NAME for CSRF
    WTF_CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'https://localhost:8000',
        f"https://{os.environ.get('HOSTNAME')}"
    ]

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Enable HTTPS
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'True') == 'True'
    # Prevent CSRF
    WTF_CSRF_ENABLED = True
    # For production, add your actual domain
    WTF_CSRF_TRUSTED_ORIGINS = [
        f"https://{os.environ.get('DOMAIN_NAME', 'yourdomain.com')}",
        f"http://{os.environ.get('DOMAIN_NAME', 'yourdomain.com')}"
    ]