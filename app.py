import os
import random
from flask import Flask, render_template, redirect, url_for, flash, request, session
from yt_dlp import YoutubeDL
from server import Config

app = Flask(__name__)
app.config.from_object(Config)

# Carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configurar ruta de FFmpeg (ajusta según tu instalación)
FFMPEG_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
FFPROBE_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe'

if os.path.exists(FFMPEG_PATH):
    os.environ['FFMPEG_BINARY'] = FFMPEG_PATH
    os.environ['FFPROBE_BINARY'] = FFPROBE_PATH

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
# -------------------------

def get_common_options(output_path):
    """Opciones comunes para yt-dlp"""
    return {
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'writethumbnail': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'noplaylist': True,
        'geo_bypass': True,
        'prefer_ffmpeg': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }

def download_video_yt_dlp(url, output_path):
    options = get_common_options(output_path)
    
    # Configuración específica para MP4 con portada incrustada
    options.update({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Título desconocido')
        
        # Limpiar archivos de miniaturas después de la descarga
        try:
            base_name = os.path.join(output_path, title)
            for ext in ['.webp', '.jpg', '.png']:
                thumb_file = base_name + ext
                if os.path.exists(thumb_file):
                    os.remove(thumb_file)
                    print(f"Miniatura eliminada: {thumb_file}")
        except Exception as e:
            print(f"No se pudo eliminar miniatura: {e}")
        
        return title 

def download_audio_yt_dlp(url, output_path):
    options = get_common_options(output_path)
    
    # Configuración específica para MP3 con portada incrustada
    options.update({
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    })
    
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Título desconocido')
        
        # Limpiar archivos de miniaturas y temporales después de la descarga
        try:
            base_name = os.path.join(output_path, title)
            # Eliminar miniaturas
            for ext in ['.webp', '.jpg', '.png']:
                thumb_file = base_name + ext
                if os.path.exists(thumb_file):
                    os.remove(thumb_file)
                    print(f"Miniatura eliminada: {thumb_file}")
            
            # Eliminar archivo webm si existe
            webm_file = base_name + '.webm'
            if os.path.exists(webm_file):
                os.remove(webm_file)
                print(f"Archivo temporal eliminado: {webm_file}")
                
        except Exception as e:
            print(f"No se pudo eliminar archivos temporales: {e}")
        
        return title

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/download_mp4', methods=['GET', 'POST'])
def download_mp4():
    if request.method == 'POST':
        captcha_answer = request.form.get('captcha')
        if not validate_captcha(captcha_answer):
            flash("Captcha incorrecto. Intenta de nuevo.", "danger")
            return redirect(url_for('download_mp4'))

        url = request.form.get('url')
        if not url:
            flash("Por favor, ingresa una URL válida.", "danger")
            return redirect(url_for('download_mp4'))
        
        # Limpieza de URL
        if '&list=' in url: url = url.split('&list=')[0]
        if '?list=' in url: url = url.split('?list=')[0]
            
        try:
            title = download_video_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"Video '{title}' descargado exitosamente con portada incrustada.", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            print(f"DEBUG ERROR: {e}")
        return redirect(url_for('download_mp4'))
    
    captcha_question = generate_captcha()
    return render_template('download_mp4.html', captcha_question=captcha_question)

@app.route('/download_mp3', methods=['GET', 'POST'])
def download_mp3():
    if request.method == 'POST':
        captcha_answer = request.form.get('captcha')
        if not validate_captcha(captcha_answer):
            flash("Captcha incorrecto.", "danger")
            return redirect(url_for('download_mp3'))

        url = request.form.get('url')
        if not url:
            flash("URL inválida.", "danger")
            return redirect(url_for('download_mp3'))
        
        if '&list=' in url: url = url.split('&list=')[0]
        if '?list=' in url: url = url.split('?list=')[0]
            
        try:
            title = download_audio_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"Audio '{title}' descargado exitosamente con portada incrustada.", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            print(f"DEBUG ERROR: {e}")
        return redirect(url_for('download_mp3'))
    
    captcha_question = generate_captcha()
    return render_template('download_mp3.html', captcha_question=captcha_question)

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)