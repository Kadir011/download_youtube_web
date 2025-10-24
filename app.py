import os
from flask import Flask, render_template, redirect, url_for, flash, request
from yt_dlp import YoutubeDL
from server import Config

app = Flask(__name__)
app.config.from_object(Config)

# Carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Función para descargar video
def download_video_yt_dlp(url, output_path):
    options = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'merge_output_format': 'mp4',
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        # Opciones para evitar bloqueos
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'extract_flat': False,
        'skip_download': False,
        # Importante: Evitar playlists
        'noplaylist': True,
        # User agent y headers
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        # Configuraciones adicionales
        'geo_bypass': True,
        'age_limit': None,
        # Opciones adicionales para evitar 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Título desconocido') 

# Función para descargar audio 
def download_audio_yt_dlp(url, output_path):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_path}/%(title)s.%(ext)s", 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Opciones para evitar bloqueos
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'extract_flat': False,
        'skip_download': False,
        # Importante: Evitar playlists
        'noplaylist': True,
        # User agent y headers
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        # Configuraciones adicionales
        'geo_bypass': True,
        'age_limit': None,
        # Opciones adicionales para evitar 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Título desconocido') 
    
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/download_mp4', methods=['GET', 'POST'])
def download_mp4():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("Por favor, ingresa una URL válida.", "danger")
            return redirect(url_for('download_mp4'))
        
        # Limpiar URL de parámetros de playlist
        if '&list=' in url:
            url = url.split('&list=')[0]
        if '?list=' in url and 'watch?v=' in url:
            # Mantener solo el video ID
            video_id = url.split('watch?v=')[1].split('&')[0]
            url = f"https://www.youtube.com/watch?v={video_id}"
            
        try:
            title = download_video_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"El video '{title}' se descargó correctamente.", "success")
        except Exception as e:
            flash(f"Error al descargar el video: {str(e)}", "danger")
            print(f"Error al descargar el video: {str(e)}")
        return redirect(url_for('download_mp4'))
    return render_template('download_mp4.html')

@app.route('/download_mp3', methods=['GET', 'POST'])
def download_mp3():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("Por favor, ingresa una URL válida.", "danger")
            return redirect(url_for('download_mp3'))
        
        # Limpiar URL de parámetros de playlist
        if '&list=' in url:
            url = url.split('&list=')[0]
        if '?list=' in url and 'watch?v=' in url:
            # Mantener solo el video ID
            video_id = url.split('watch?v=')[1].split('&')[0]
            url = f"https://www.youtube.com/watch?v={video_id}"
            
        try:
            title = download_audio_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"El audio MP3 '{title}' se descargó correctamente.", "success")
        except Exception as e:
            flash(f"Error al descargar el MP3: {str(e)}", "danger")
            print(f"Error al descargar el MP3: {str(e)}")
        return redirect(url_for('download_mp3'))
    return render_template('download_mp3.html')

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)