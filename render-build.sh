#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Instalando dependencias de Python ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Descargando FFmpeg estático ==="
# Crear directorio si no existe
mkdir -p ffmpeg_bin

# Descargar build estática
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Descomprimir
tar xvf ffmpeg-release-amd64-static.tar.xz -C ffmpeg_bin --strip-components=1

# Limpiar
rm ffmpeg-release-amd64-static.tar.xz

echo "=== Dando permisos de ejecución ==="
chmod +x ffmpeg_bin/ffmpeg
chmod +x ffmpeg_bin/ffprobe

echo "=== Build completado ==="