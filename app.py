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
    """Opciones comunes para yt-dlp para evitar repetición de código"""
    return {
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'writethumbnail': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'extract_flat': False,
        'skip_download': False,
        'noplaylist': True,
        'geo_bypass': True,
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
    options.update({
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'merge_output_format': 'mp4',
        'postprocessors': [
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
    })
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Título desconocido') 

def download_audio_yt_dlp(url, output_path):
    options = get_common_options(output_path)
    options.update({
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
    })
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Título desconocido') 

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
        
        # Limpieza básica de URL
        if '&list=' in url: url = url.split('&list=')[0]
            
        try:
            title = download_video_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"Video '{title}' descargado exitosamente.", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('download_mp4'))
    
    # GET: Generar nuevo captcha
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
            
        try:
            title = download_audio_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"Audio '{title}' descargado exitosamente.", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('download_mp3'))
    
    captcha_question = generate_captcha()
    return render_template('download_mp3.html', captcha_question=captcha_question)

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)