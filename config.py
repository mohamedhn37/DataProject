import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
