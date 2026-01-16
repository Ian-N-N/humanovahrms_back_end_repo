import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    # Handle Render's DATABASE_URL which often starts with postgres:// (incompatible with newer SQLAlchemy)
    _db_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///hrms.db')
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret')
    PROPAGATE_EXCEPTIONS = True
    from datetime import timedelta
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Cloudinary Configuration (Placeholder)
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'your_cloud_name')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', 'your_api_key')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'your_api_secret')
    # Gmail SMTP Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'austineochieng101@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') # 16-character App Password
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'austineochieng101@gmail.com')
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
