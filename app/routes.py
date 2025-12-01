import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_file, current_app
from app.services import process_download
from app.utils import generate_captcha, validate_captcha, cleanup_file_delayed
from app.storage import download_files

# Crear el Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/favicon.ico')
def favicon():
    return '', 204

@main.route('/download_mp4', methods=['GET', 'POST'])
def download_mp4():
    return handle_download_request(is_audio=False)

@main.route('/download_mp3', methods=['GET', 'POST'])
def download_mp3():
    return handle_download_request(is_audio=True)

def handle_download_request(is_audio):
    """Lógica común para manejar las peticiones de las rutas"""
    endpoint = 'main.download_mp3' if is_audio else 'main.download_mp4'
    template = 'download_mp3.html' if is_audio else 'download_mp4.html'
    
    if request.method == 'POST':
        if not validate_captcha(request.form.get('captcha')):
            flash("Captcha incorrecto. Intenta de nuevo.", "danger")
            return redirect(url_for(endpoint))

        url = request.form.get('url')
        if not url:
            flash("URL inválida.", "danger")
            return redirect(url_for(endpoint))
        
        # Limpieza de URL
        if '&list=' in url: url = url.split('&list=')[0]
        if '?list=' in url: url = url.split('?list=')[0]

        try:
            # Usamos la configuración centralizada
            temp_folder = current_app.config['TEMP_FOLDER']
            file_path, title = process_download(url, temp_folder, is_audio=is_audio)
            
            download_id = str(uuid.uuid4())
            download_files[download_id] = {
                'path': file_path,
                'name': f"{title}.{'mp3' if is_audio else 'mp4'}",
                'type': 'audio/mpeg' if is_audio else 'video/mp4'
            }
            
            cleanup_file_delayed(file_path, download_id)
            
            flash(f"{'Audio' if is_audio else 'Video'} procesado exitosamente.", "success")
            session['download_id'] = download_id
            return redirect(url_for(endpoint))
            
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            print(f"DEBUG ERROR: {e}")
            return redirect(url_for(endpoint))

    captcha_question = generate_captcha()
    download_id = session.pop('download_id', None)
    
    download_ready = False
    download_url = None
    if download_id and download_id in download_files:
        download_ready = True
        download_url = url_for('main.serve_file', download_id=download_id)
    
    return render_template(template, 
                         captcha_question=captcha_question,
                         download_ready=download_ready,
                         download_url=download_url)

@main.route('/serve/<download_id>')
def serve_file(download_id):
    if download_id not in download_files:
        flash("El archivo ya no está disponible.", "warning")
        return redirect(url_for('main.index'))
    
    file_info = download_files[download_id]
    return send_file(
        file_info['path'],
        as_attachment=True,
        download_name=file_info['name'],
        mimetype=file_info['type']
    )