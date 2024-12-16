import os
from datetime import timedelta

class Config:
    # Basic configurations
    HOST = '0.0.0.0'  # Allow external connections
    PORT = 5001       # Default Flask port
    DEBUG = True      # Enable debug mode for development
    
    # Static folder configuration
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    # Security configurations
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    CSRF_ENABLED = True
    
    # JWT configurations
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_BLACKLIST_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False
    
    # CORS configurations
    CORS_ORIGINS = "*"  # Allow all origins in development
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization"]
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ["Content-Type", "Authorization"]
    
    # SQLite database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'todos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional configurations
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size 16MB
    PROPAGATE_EXCEPTIONS = True  # Propagate exceptions to get better error messages
