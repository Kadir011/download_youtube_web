import os

class Config:
    SECRET_KEY = '4f6a5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d'
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 5000
    # Definir carpetas aquí para que estén centralizadas
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')