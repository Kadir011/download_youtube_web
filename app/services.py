import os
import subprocess
from yt_dlp import YoutubeDL

# --- CONFIGURACIÓN DE FFMPEG ---
def get_ffmpeg_path():
    """Detecta la ruta de FFmpeg dependiendo del entorno"""
    # 1. Entorno Local (Windows)
    if os.name == 'nt':
        return r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
    
    # 2. Entorno Render (Linux)
    # En Render, el script de build creó la carpeta en la raíz del proyecto
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    local_ffmpeg = os.path.join(base_dir, 'ffmpeg_bin', 'ffmpeg')
    
    if os.path.exists(local_ffmpeg):
        # Asegurar permisos de ejecución (importante en Linux)
        try:
            os.chmod(local_ffmpeg, 0o755)
        except:
            pass
        return local_ffmpeg
        
    # 3. Fallback (por si acaso)
    return 'ffmpeg'

FFMPEG_PATH = get_ffmpeg_path()

def get_common_options(output_path):
    """Opciones base para yt-dlp"""
    return {
        'restrictfilenames': True,
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'noplaylist': True,
        'geo_bypass': True,
        'ffmpeg_location': FFMPEG_PATH,
        
        # --- ESTRATEGIA: CLIENTE ANDROID ---
        # Android suele ser más permisivo en servidores Cloud que iOS o Web.
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        # User Agent genérico de Android para reforzar la máscara
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }

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
    
    options = get_common_options(output_path)
    options['writethumbnail'] = True
    
    if is_audio:
        options['format'] = 'bestaudio/best'
        options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    else:
        options['format'] = 'best[ext=mp4]/best'
        options['merge_output_format'] = 'mp4'

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        
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
            if thumbnail_file.endswith('.webp'):
                jpg_file = base_name + '.jpg'
                subprocess.run([FFMPEG_PATH, '-i', thumbnail_file, '-y', jpg_file], capture_output=True)
                if os.path.exists(jpg_file):
                    os.remove(thumbnail_file)
                    thumbnail_file = jpg_file
            
            embed_thumbnail_manually(final_file, thumbnail_file, is_audio)
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)

        # Limpieza de archivos temporales de yt-dlp
        for ext in ['.webm', '.m4a', '.opus']:
            if os.path.exists(base_name + ext): os.remove(base_name + ext)

        return final_file, info.get('title', 'Video')