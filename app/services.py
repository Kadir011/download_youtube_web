import os
import subprocess
from yt_dlp import YoutubeDL

# Configuración de FFmpeg
if os.name == 'nt':  # Windows
    FFMPEG_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
    if os.path.exists(FFMPEG_PATH):
        os.environ['FFMPEG_BINARY'] = FFMPEG_PATH
else:  # Linux/Mac (Render usa Linux)
    FFMPEG_PATH = 'ffmpeg'

def get_common_options(output_path):
    """Opciones base para yt-dlp con configuración anti-bloqueo"""
    return {
        'restrictfilenames': True,
        'outtmpl': f"{output_path}/%(title)s.%(ext)s",
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'noplaylist': True,
        'geo_bypass': True,
        'prefer_ffmpeg': True,
        'ffmpeg_location': FFMPEG_PATH,
        
        # Configuración anti-bot mejorada
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        
        # User agent actualizado
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        
        # Headers HTTP mejorados
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        },
        
        # Configuración adicional para evitar bloqueos
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'sleep_interval_requests': 1,
        'age_limit': None,
        'extract_flat': False,
    }

def embed_thumbnail_manually(media_file, thumbnail_file, is_audio=True):
    """
    Incrusta la miniatura usando FFmpeg.
    Funciona tanto para MP3 como para MP4 ajustando los parámetros.
    """
    try:
        ext = '.mp3' if is_audio else '.mp4'
        temp_output = media_file.replace(ext, f'_temp{ext}')
        
        cmd = [FFMPEG_PATH, '-i', media_file, '-i', thumbnail_file]
        
        if is_audio:
            # Configuración para MP3
            cmd.extend(['-map', '0:0', '-map', '1:0', '-c', 'copy', '-id3v2_version', '3',
                        '-metadata:s:v', 'title=Album cover', '-metadata:s:v', 'comment=Cover (front)'])
        else:
            # Configuración para MP4
            cmd.extend(['-map', '0', '-map', '1', '-c', 'copy', '-c:v:1', 'mjpeg',
                        '-disposition:v:1', 'attached_pic'])

        cmd.extend(['-y', temp_output])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_output):
            os.remove(media_file)
            os.rename(temp_output, media_file)
            print(f"Portada incrustada exitosamente en: {media_file}")
            return True
        else:
            print(f"Error FFmpeg: {result.stderr}")
            if os.path.exists(temp_output): os.remove(temp_output)
            return False
            
    except Exception as e:
        print(f"Excepción al incrustar portada: {e}")
        return False

def process_download(url, output_path, is_audio=False):
    """
    Función unificada para descargar y procesar video o audio.
    """
    options = get_common_options(output_path)
    options['writethumbnail'] = True
    
    if is_audio:
        options['format'] = 'bestaudio/best'
        options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    else:
        # Formato más permisivo para video
        options['format'] = 'best[ext=mp4]/best'
        options['merge_output_format'] = 'mp4'

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Título desconocido')
        
        # Usamos prepare_filename para obtener el nombre real y sanitizado
        temp_filename = ydl.prepare_filename(info)
        base_name = os.path.splitext(temp_filename)[0]
        
        final_file = base_name + ('.mp3' if is_audio else '.mp4')
        
        # Buscar miniatura
        thumbnail_file = None
        for ext in ['.webp', '.jpg', '.png']:
            possible_thumb = base_name + ext
            if os.path.exists(possible_thumb):
                thumbnail_file = possible_thumb
                break
        
        # Procesar miniatura si existe
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

        # Limpiar temporales extra
        for ext in ['.webm', '.m4a', '.opus']:
            temp = base_name + ext
            if os.path.exists(temp): os.remove(temp)

        return final_file, title