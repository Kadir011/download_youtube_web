import os
import time
import threading
import random
from flask import session
from app.storage import download_files

# --- LÓGICA DE CAPTCHA ---
def generate_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_result'] = num1 + num2
    return f"{num1} + {num2}"

def validate_captcha(user_answer):
    try:
        if int(user_answer) == session.get('captcha_result'):
            return True
    except (ValueError, TypeError):
        pass
    return False

# --- LIMPIEZA AUTOMÁTICA ---
def cleanup_file_delayed(filepath, download_id, delay=30):
    """Elimina el archivo y la entrada del diccionario después de un tiempo"""
    def delete():
        time.sleep(delay)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Archivo eliminado del servidor: {filepath}")
            
            # Eliminar del diccionario compartido
            if download_id in download_files:
                del download_files[download_id]
        except Exception as e:
            print(f"Error al eliminar archivo: {e}")
    
    thread = threading.Thread(target=delete, daemon=True)
    thread.start()