# Youtube Downloader

Una aplicación web moderna y eficiente para descargar videos de YouTube en formatos MP4 y MP3. Interfaz limpia, rápida y fácil de usar.

## Características principales

- **Descarga de videos en MP4**: Obtén videos en alta calidad con un solo clic
- **Extracción de audio en MP3**: Convierte videos a formato de audio MP3 (192 kbps)
- **Miniaturas incrustadas**: Los archivos descargados incluyen la portada del video original
- **Interfaz multilenguaje**: Soporte para español e inglés
- **Tema claro/oscuro**: Cambia entre modos de visualización según tu preferencia
- **Diseño responsivo**: Funciona perfectamente en computadoras, tablets y móviles
- **Sistema de seguridad**: Captcha matemático simple para prevenir abusos
- **Limpieza automática**: Los archivos temporales se eliminan automáticamente del servidor

## Requisitos previos

- Python 3.8 o superior
- FFmpeg instalado en tu sistema
- Conexión a internet estable

### Instalación de FFmpeg

**Windows:**
1. Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extrae el archivo y añade la carpeta `bin` al PATH del sistema
3. O ajusta la ruta en `app/services.py` (línea 7)

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Kadir011/download_youtube_web.git
cd download_youtube_web
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:
```bash
python run.py
```

5. Abre tu navegador y accede a:
```
http://localhost:5000
```

## Uso

1. **Página principal**: Selecciona si deseas descargar video o audio
2. **Ingresa la URL**: Pega el enlace del video de YouTube
3. **Completa el captcha**: Resuelve la suma matemática simple
4. **Descarga**: Haz clic en el botón y espera a que se procese
5. **Obtén tu archivo**: La descarga comenzará automáticamente

### Notas importantes

- Solo se procesan videos individuales (no playlists)
- Los archivos se eliminan del servidor después de 30 segundos
- La aplicación limpia automáticamente los enlaces de playlists
- Tiempo de procesamiento varía según la duración del video

## Estructura del proyecto

```
download_youtube_web/
│
├── app/
│   ├── __init__.py          # Inicialización de Flask
│   ├── routes.py            # Rutas y endpoints
│   ├── services.py          # Lógica de descarga y procesamiento
│   ├── utils.py             # Funciones auxiliares (captcha, limpieza)
│   ├── storage.py           # Almacenamiento temporal en memoria
│   ├── static/
│   │   ├── css/style.css    # Estilos personalizados
│   │   └── js/script.js     # Funcionalidad del cliente
│   └── templates/
│       ├── base.html        # Plantilla base
│       ├── index.html       # Página principal
│       ├── download_mp4.html
│       └── download_mp3.html
│
├── config.py                # Configuración de la aplicación
├── run.py                   # Punto de entrada
├── requirements.txt         # Dependencias
└── README.md
```

## Tecnologías utilizadas

### Backend
- **Flask 3.1.2**: Framework web minimalista y flexible
- **yt-dlp**: Herramienta robusta para descargar contenido de YouTube
- **FFmpeg**: Procesamiento de audio y video

### Frontend
- **Bootstrap 5.3**: Framework CSS moderno
- **Bootstrap Icons**: Iconografía vectorial
- **JavaScript vanilla**: Sin dependencias adicionales

## Configuración avanzada

### Variables de entorno (.env)
Puedes crear un archivo `.env` para configuraciones personalizadas:
```
FLASK_SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

### Ajustar calidad de audio
Modifica el parámetro `preferredquality` en `app/services.py` (línea 67):
```python
'preferredquality': '320'  # Para calidad máxima
```

## Solución de problemas comunes

**Error: FFmpeg no encontrado**
- Verifica que FFmpeg esté instalado correctamente
- Ajusta la ruta en `app/services.py` si es necesario

**Error al descargar videos**
- Asegúrate de que el enlace sea válido
- Algunos videos pueden tener restricciones regionales
- Verifica tu conexión a internet

**Archivos con caracteres extraños**
- La aplicación usa `restrictfilenames=True` para evitar problemas
- Los nombres se sanitizan automáticamente

## Contribuciones

Las contribuciones son bienvenidas y apreciadas. Si deseas mejorar este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/mejora`)
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`)
4. Sube tus cambios (`git push origin feature/mejora`)
5. Abre un Pull Request

### Ideas para contribuir
- Agregar más formatos de descarga
- Soporte para otros servicios de video
- Mejorar la interfaz de usuario
- Optimizar el rendimiento
- Agregar tests unitarios

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

## Descargo de responsabilidad

Esta herramienta está diseñada únicamente para uso personal y educativo. Los usuarios son responsables de cumplir con los términos de servicio de YouTube y las leyes de derechos de autor aplicables en su jurisdicción. No nos hacemos responsables del uso indebido de esta aplicación.

## Autor

**Kadir Barquet**  
Desarrollador Python especializado en aplicaciones web

- GitHub: [@Kadir011](https://github.com/Kadir011)
- Proyecto: [download_youtube_web](https://github.com/Kadir011/download_youtube_web)

## Agradecimientos

- A la comunidad de código abierto por las herramientas utilizadas
- A los contribuidores que ayudan a mejorar este proyecto
- A yt-dlp por su excelente biblioteca de descarga

---

Si encuentras útil este proyecto, considera darle una estrella en GitHub. Tu apoyo es muy apreciado.