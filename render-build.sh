#!/bin/bash

# Script de build para Render
# Instala FFmpeg y dependencias de Python

echo "=== Instalando FFmpeg ==="
apt-get update
apt-get install -y ffmpeg

echo "=== Verificando instalación de FFmpeg ==="
ffmpeg -version

echo "=== Instalando dependencias de Python ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Build completado exitosamente ==="