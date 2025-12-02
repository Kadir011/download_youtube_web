import os
import subprocess
import tempfile
from yt_dlp import YoutubeDL

# --- CONFIGURACIÓN DE FFMPEG ---
# Detectar si estamos en Render (Linux) o Local (Windows)
if os.name == 'nt':  # Windows Local
    FFMPEG_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
else:  # Render / Linux
    # Buscamos en la carpeta local donde lo descargó render-build.sh
    base_dir = os.getcwd()
    local_ffmpeg = os.path.join(base_dir, 'ffmpeg_bin', 'ffmpeg')
    
    if os.path.exists(local_ffmpeg):
        FFMPEG_PATH = local_ffmpeg
    else:
        # Fallback al sistema global (por si acaso)
        FFMPEG_PATH = 'ffmpeg'

# Asegurar permisos de ejecución en Linux
if os.name != 'nt' and os.path.exists(FFMPEG_PATH):
    try:
        os.chmod(FFMPEG_PATH, 0o755)
    except:
        pass

def get_common_options(output_path, cookie_file_path=None):
    """Opciones base para yt-dlp"""
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
        
        # Estrategia de Cliente (iOS es robusto)
        'extractor_args': {
            'youtube': {
                'player_client': ['ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
    }
    
    # Si tenemos cookies, las inyectamos
    if cookie_file_path:
        opts['cookiefile'] = cookie_file_path
        
    return opts

def embed_thumbnail_manually(media_file, thumbnail_file, is_audio=True):
    """Incrusta la miniatura usando FFmpeg"""
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
    """Función principal de descarga"""
    
    # 1. GESTIÓN DE COOKIES (Bypass antibot)
    cookie_file = None
    cookies_content = os.environ.get('COOKIES_CONTENT')
    
    if cookies_content:
        # Crear archivo temporal con las cookies
        cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
        cookie_file.write(cookies_content)
        cookie_file.close()
        print("INFO: Cookies cargadas correctamente.")

    try:
        # 2. Configurar opciones
        cookie_path = cookie_file.name if cookie_file else None
        options = get_common_options(output_path, cookie_path)
        options['writethumbnail'] = True
        
        if is_audio:
            options['format'] = 'bestaudio/best'
            options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        else:
            options['format'] = 'best[ext=mp4]/best'
            options['merge_output_format'] = 'mp4'

        # 3. Descargar
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Obtener nombres de archivo
            temp_filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(temp_filename)[0]
            final_file = base_name + ('.mp3' if is_audio else '.mp4')
            
            # Procesar miniatura
            thumbnail_file = None
            for ext in ['.webp', '.jpg', '.png']:
                possible_thumb = base_name + ext
                if os.path.exists(possible_thumb):
                    thumbnail_file = possible_thumb
                    break
            
            if thumbnail_file and os.path.exists(final_file):
                # Convertir webp a jpg si es necesario
                if thumbnail_file.endswith('.webp'):
                    jpg_file = base_name + '.jpg'
                    subprocess.run([FFMPEG_PATH, '-i', thumbnail_file, '-y', jpg_file], capture_output=True)
                    if os.path.exists(jpg_file):
                        os.remove(thumbnail_file)
                        thumbnail_file = jpg_file
                
                embed_thumbnail_manually(final_file, thumbnail_file, is_audio)
                if os.path.exists(thumbnail_file):
                    os.remove(thumbnail_file)

            # Limpieza extra
            for ext in ['.webm', '.m4a', '.opus']:
                if os.path.exists(base_name + ext): os.remove(base_name + ext)

            return final_file, info.get('title', 'Video')

    finally:
        # 4. Limpiar archivo de cookies
        if cookie_file and os.path.exists(cookie_file.name):
            try:
                os.remove(cookie_file.name)
            except:
                pass