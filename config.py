import os

class Config:
    # Usar variable de entorno para SECRET_KEY en producción
    SECRET_KEY = os.environ.get('SECRET_KEY') or '4f6a5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d'
    DEBUG = os.environ.get('FLASK_ENV') != 'production'
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Definir carpetas aquí para que estén centralizadas
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')