import os
import random
import subprocess
from flask import Flask, render_template, redirect, url_for, flash, request, session
from yt_dlp import YoutubeDL
from server import Config

app = Flask(__name__)
app.config.from_object(Config)

# Carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configurar ruta de FFmpeg
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
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'noplaylist': True,
        'geo_bypass': True,
        'prefer_ffmpeg': True,
        'ffmpeg_location': r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }

def embed_thumbnail_manually(mp3_file, thumbnail_file):
    """Incrusta la miniatura manualmente usando FFmpeg"""
    try:
        temp_output = mp3_file.replace('.mp3', '_temp.mp3')
        
        cmd = [
            FFMPEG_PATH,
            '-i', mp3_file,
            '-i', thumbnail_file,
            '-map', '0:0',
            '-map', '1:0',
            '-c', 'copy',
            '-id3v2_version', '3',
            '-metadata:s:v', 'title=Album cover',
            '-metadata:s:v', 'comment=Cover (front)',
            '-y',
            temp_output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_output):
            os.remove(mp3_file)
            os.rename(temp_output, mp3_file)
            print(f"✓ Portada incrustada exitosamente en: {mp3_file}")
            return True
        else:
            print(f"✗ Error al incrustar portada: {result.stderr}")
            if os.path.exists(temp_output):
                os.remove(temp_output)
            return False
            
    except Exception as e:
        print(f"✗ Excepción al incrustar portada: {e}")
        return False

def embed_thumbnail_to_mp4(mp4_file, thumbnail_file):
    """Incrusta la miniatura en MP4 usando FFmpeg"""
    try:
        temp_output = mp4_file.replace('.mp4', '_temp.mp4')
        
        cmd = [
            FFMPEG_PATH,
            '-i', mp4_file,
            '-i', thumbnail_file,
            '-map', '0',
            '-map', '1',
            '-c', 'copy',
            '-c:v:1', 'mjpeg',
            '-disposition:v:1', 'attached_pic',
            '-y',
            temp_output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_output):
            os.remove(mp4_file)
            os.rename(temp_output, mp4_file)
            print(f"✓ Portada incrustada exitosamente en: {mp4_file}")
            return True
        else:
            print(f"✗ Error al incrustar portada en MP4: {result.stderr}")
            if os.path.exists(temp_output):
                os.remove(temp_output)
            return False
            
    except Exception as e:
        print(f"✗ Excepción al incrustar portada en MP4: {e}")
        return False

def download_video_yt_dlp(url, output_path):
    options = get_common_options(output_path)
    
    # Configuración para descargar MP4 y miniatura por separado
    options.update({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'writethumbnail': True,
    })

    with YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Título desconocido')
            
            base_name = os.path.join(output_path, title)
            mp4_file = base_name + '.mp4'
            
            # Buscar el archivo de miniatura
            thumbnail_file = None
            for ext in ['.webp', '.jpg', '.png']:
                thumb = base_name + ext
                if os.path.exists(thumb):
                    thumbnail_file = thumb
                    break
            
            # Si existe la miniatura, incrustarla manualmente
            if thumbnail_file and os.path.exists(mp4_file):
                print(f"📥 MP4 descargado: {mp4_file}")
                print(f"🖼️ Miniatura encontrada: {thumbnail_file}")
                
                # Convertir miniatura a JPG si es necesario
                if thumbnail_file.endswith('.webp'):
                    jpg_file = base_name + '.jpg'
                    convert_cmd = [
                        FFMPEG_PATH,
                        '-i', thumbnail_file,
                        '-y',
                        jpg_file
                    ]
                    subprocess.run(convert_cmd, capture_output=True)
                    if os.path.exists(jpg_file):
                        os.remove(thumbnail_file)
                        thumbnail_file = jpg_file
                        print(f"✓ Miniatura convertida a JPG")
                
                # Incrustar la portada
                if embed_thumbnail_to_mp4(mp4_file, thumbnail_file):
                    print(f"✓ Portada incrustada exitosamente en MP4")
                else:
                    print(f"✗ No se pudo incrustar la portada en MP4")
                
                # Eliminar archivo de miniatura
                if os.path.exists(thumbnail_file):
                    os.remove(thumbnail_file)
                    print(f"✓ Miniatura temporal eliminada")
            else:
                print(f"⚠️ No se encontró miniatura o archivo MP4")
            
            return title
            
        except Exception as e:
            print(f"Error durante la descarga de MP4: {e}")
            raise 

def download_audio_yt_dlp(url, output_path):
    options = get_common_options(output_path)
    
    # Configuración para descargar MP3 y miniatura por separado
    options.update({
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
        ],
    })
    
    with YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Título desconocido')
            
            base_name = os.path.join(output_path, title)
            mp3_file = base_name + '.mp3'
            
            # Buscar el archivo de miniatura
            thumbnail_file = None
            for ext in ['.webp', '.jpg', '.png']:
                thumb = base_name + ext
                if os.path.exists(thumb):
                    thumbnail_file = thumb
                    break
            
            # Si existe la miniatura, incrustarla manualmente
            if thumbnail_file and os.path.exists(mp3_file):
                print(f"📥 MP3 descargado: {mp3_file}")
                print(f"🖼️ Miniatura encontrada: {thumbnail_file}")
                
                # Convertir miniatura a JPG si es necesario
                if thumbnail_file.endswith('.webp'):
                    jpg_file = base_name + '.jpg'
                    convert_cmd = [
                        FFMPEG_PATH,
                        '-i', thumbnail_file,
                        '-y',
                        jpg_file
                    ]
                    subprocess.run(convert_cmd, capture_output=True)
                    if os.path.exists(jpg_file):
                        os.remove(thumbnail_file)
                        thumbnail_file = jpg_file
                        print(f"✓ Miniatura convertida a JPG")
                
                # Incrustar la portada
                if embed_thumbnail_manually(mp3_file, thumbnail_file):
                    print(f"✓ Portada incrustada exitosamente")
                else:
                    print(f"✗ No se pudo incrustar la portada")
                
                # Eliminar archivo de miniatura
                if os.path.exists(thumbnail_file):
                    os.remove(thumbnail_file)
                    print(f"✓ Miniatura temporal eliminada")
            else:
                print(f"⚠️ No se encontró miniatura o archivo MP3")
            
            # Limpiar archivos temporales de audio
            for ext in ['.webm', '.m4a', '.opus']:
                temp_file = base_name + ext
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        print(f"✓ Archivo temporal eliminado: {temp_file}")
                    except Exception as e:
                        print(f"✗ No se pudo eliminar {temp_file}: {e}")
            
            return title
            
        except Exception as e:
            print(f"Error durante la descarga: {e}")
            raise

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