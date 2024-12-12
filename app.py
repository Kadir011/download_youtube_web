import os 
import secrets 
from flask import Flask, render_template, redirect, url_for, flash, request 
from yt_dlp import YoutubeDL 

app = Flask(__name__) 
app.secret_key = secrets.token_hex(32) 

# Carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Función para descargar video
def download_video_yt_dlp(url, output_path):
    options = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Título desconocido') 

# Función para descargar audio 
def download_audio_yt_dlp(url, output_path):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_path}/%(title)s.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
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
        try:
            title = download_video_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"El video '{title}' se descargó correctamente.", "success")
        except Exception as e:
            flash(f"Error al descargar el video: {str(e)}", "danger")
            print(f"Error al descargar el video: {str(e)}")  # Para depuración
        return redirect(url_for('download_mp4'))
    return render_template('download_mp4.html')

@app.route('/download_mp3', methods=['GET', 'POST'])
def download_mp3():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("Por favor, ingresa una URL válida.", "danger")
            return redirect(url_for('download_mp3'))
        try:
            title = download_audio_yt_dlp(url, DOWNLOAD_FOLDER)
            flash(f"El audio MP3 '{title}' se descargó correctamente.", "success")
        except Exception as e:
            flash(f"Error al descargar el MP3: {str(e)}", "danger")
            print(f"Error al descargar el MP3: {str(e)}")  # Para depuración
        return redirect(url_for('download_mp3'))
    return render_template('download_mp3.html')

if __name__ == '__main__':
    app.run(debug=True) 



