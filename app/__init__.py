import os
from flask import Flask
from config import Config

def create_app():
    # Inicializar Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(Config)
    
    # Asegurar que exista la carpeta temporal
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    
    # Registrar Blueprints (Rutas)
    from app.routes import main
    app.register_blueprint(main)
    
    return app