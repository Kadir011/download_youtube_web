import os
import subprocess
import tempfile
import random
from yt_dlp import YoutubeDL

# --- CONFIGURACIÓN DE FFMPEG ---
def get_ffmpeg_path():
    # 1. Entorno Local (Windows)
    if os.name == 'nt':
        return r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
    
    # 2. Entorno Render (Linux)
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    local_ffmpeg = os.path.join(base_dir, 'ffmpeg_bin', 'ffmpeg')
    
    if os.path.exists(local_ffmpeg):
        try:
            os.chmod(local_ffmpeg, 0o755)
        except:
            pass
        return local_ffmpeg
    return 'ffmpeg'

FFMPEG_PATH = get_ffmpeg_path()

def get_common_options(output_path, cookie_file_path=None):
    """Opciones optimizadas para simular un dispositivo Android"""
    opts = {
        'restrictfilenames': True,
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'noplaylist': True,
        'geo_bypass': True,
        'ffmpeg_location': FFMPEG_PATH,
        
        # --- ESTRATEGIA: MÁSCARA ANDROID ---
        # Le decimos a YouTube que somos un móvil Android.
        # Esto suele funcionar bien para MP3 y MP4.
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        # User Agent de un Samsung Galaxy para reforzar la identidad
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    }
    
    # Si hay cookies, las usamos para saltar el bloqueo de IP de Render
    if cookie_file_path:
        opts['cookiefile'] = cookie_file_path
        print("INFO: Autenticación con Cookies activada.")
        
    return opts

def embed_thumbnail_manually(media_file, thumbnail_file, is_audio=True):
    try:
        ext = '.mp3' if is_audio else '.mp4'
        temp_output = media_file.replace(ext, f'_temp{ext}')
        
        cmd = [FFMPEG_PATH, '-i', media_file, '-i', thumbnail_file]
        
        if is_audio:
            cmd.extend(['-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3',
                        '-metadata:s:v', 'title=Album cover', '-metadata:s:v', 'comment=Cover (front)'])
        else:
            cmd.extend(['-map', '0', '-map', '1', '-c', 'copy', '-c:v:1', 'mjpeg',
                        '-disposition:v:1', 'attached_pic'])

        cmd.extend(['-y', temp_output])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_output):
            os.remove(media_file)
            os.rename(temp_output, media_file)
            return True
        return False
    except Exception as e:
        print(f"Error thumbnail: {e}")
        return False

def process_download(url, output_path, is_audio=False):
    # 1. GESTIÓN DE COOKIES (Crucial para Render)
    cookie_file = None
    cookies_content = os.environ.get('COOKIES_CONTENT')
    
    if cookies_content:
        try:
            cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
            cookie_file.write(cookies_content)
            cookie_file.close()
        except Exception as e:
            print(f"Error creando archivo de cookies: {e}")

    try:
        # 2. DESCARGA
        cookie_path = cookie_file.name if cookie_file else None
        options = get_common_options(output_path, cookie_path)
        options['writethumbnail'] = True
        
        if is_audio:
            options['format'] = 'bestaudio/best'
            options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            # Priorizamos formatos compatibles con móviles y windows (mp4 con h264)
            options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            options['merge_output_format'] = 'mp4'

        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            
            temp_filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(temp_filename)[0]
            final_file = base_name + ('.mp3' if is_audio else '.mp4')
            
            # Procesamiento de miniaturas (Tu lógica original)
            thumbnail_file = None
            for ext in ['.webp', '.jpg', '.png']:
                possible_thumb = base_name + ext
                if os.path.exists(possible_thumb):
                    thumbnail_file = possible_thumb
                    break
            
            if thumbnail_file and os.path.exists(final_file):
                if thumbnail_file.endswith('.webp'):
                    jpg_file = base_name + '.jpg'
                    subprocess.run([FFMPEG_PATH, '-i', thumbnail_file, '-y', jpg_file], capture_output=True)
                    if os.path.exists(jpg_file):
                        os.remove(thumbnail_file)
                        thumbnail_file = jpg_file
                
                embed_thumbnail_manually(final_file, thumbnail_file, is_audio)
                if os.path.exists(thumbnail_file):
                    os.remove(thumbnail_file)

            # Limpieza
            for ext in ['.webm', '.m4a', '.opus']:
                if os.path.exists(base_name + ext): os.remove(base_name + ext)

            return final_file, info.get('title', 'Video')

    finally:
        # 3. LIMPIEZA DE COOKIES
        if cookie_file and os.path.exists(cookie_file.name):
            try:
                os.remove(cookie_file.name)
            except:
                pass