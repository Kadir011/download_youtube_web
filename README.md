# Youtube Downloader

Una aplicación web moderna y eficiente para descargar videos de YouTube en formatos MP4 y MP3. Interfaz limpia, rápida y fácil de usar, desplegada en la nube y accesible desde cualquier dispositivo.

## Características principales

- **Descarga de videos en MP4**: Obtén videos en alta calidad con un solo clic
- **Extracción de audio en MP3**: Convierte videos a formato de audio MP3 (192 kbps)
- **Miniaturas incrustadas**: Los archivos descargados incluyen la portada del video original
- **Interfaz multilenguaje**: Soporte para español e inglés
- **Tema claro/oscuro**: Cambia entre modos de visualización según tu preferencia
- **Diseño responsivo**: Funciona perfectamente en computadoras, tablets y móviles
- **Sistema de seguridad**: Captcha matemático simple para prevenir abusos
- **Limpieza automática**: Los archivos temporales se eliminan automáticamente del servidor
- **Sin instalación**: Accede desde cualquier navegador, sin necesidad de descargar software

## Demo en Vivo

La aplicación está desplegada y disponible en:

**[https://download-youtube-web-ulks.onrender.com](https://download-youtube-web-ulks.onrender.com)**

> **Nota:** Si la app tarda en cargar la primera vez, es normal. El servidor se activa automáticamente después de estar inactivo (plan gratuito de Render).

## Cómo usar

1. **Accede a la aplicación** desde cualquier dispositivo con conexión a internet
2. **Selecciona el formato** que deseas (Video MP4 o Audio MP3)
3. **Pega la URL** del video de YouTube
4. **Resuelve el captcha** matemático simple
5. **Haz clic en descargar** y espera el procesamiento
6. **El archivo se descargará automáticamente** a la carpeta de descargas de tu dispositivo

### Compatibilidad

- Chrome, Firefox, Safari, Edge (todos los navegadores modernos)
- Windows, macOS, Linux
- Android, iOS (dispositivos móviles)
- Tablets y cualquier dispositivo con navegador web

### Notas importantes

- Solo se procesan videos individuales (no playlists)
- Los archivos se eliminan del servidor después de 30 segundos por seguridad y privacidad
- Las descargas van directamente a la carpeta de "Descargas" de tu dispositivo
- Tiempo de procesamiento varía según la duración del video (generalmente 10-60 segundos)

## Instalación Local (Desarrollo)

Si deseas ejecutar la aplicación en tu computadora local:

### Requisitos previos

- Python 3.10 o superior
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

### Pasos de instalación

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

## Despliegue en Producción

La aplicación está configurada para desplegarse fácilmente en [Render](https://render.com) con configuración automática.

### Despliegue en Render (Recomendado)

1. **Fork o clona** este repositorio a tu cuenta de GitHub

2. **Crea una cuenta** en [Render](https://render.com) (gratis)

3. **Crea un nuevo Web Service**:
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente el archivo `render.yaml`
   - Haz clic en **"Apply"** para usar la configuración automática

4. **Espera 5-10 minutos** mientras Render construye y despliega tu aplicación

5. **¡Listo!** Tu app estará disponible en una URL como:
   ```
   https://tu-nombre-app.onrender.com
   ```

### Variables de entorno

Las siguientes variables se configuran automáticamente vía `render.yaml`:

```yaml
PYTHON_VERSION: 3.10.11
SECRET_KEY: (generado automáticamente por Render)
FLASK_ENV: production
```

### Dominio personalizado

Render permite conectar dominios personalizados de forma gratuita:

1. En tu servicio de Render, ve a **Settings → Custom Domain**
2. Añade tu dominio (ejemplo: `tudominio.com`)
3. Configura los registros DNS según las instrucciones de Render
4. Espera 15-30 minutos para la propagación DNS

**Opciones de dominio gratuito:**
- Freenom: Dominios `.tk`, `.ml`, `.ga` (gratis)
- is-a.dev: Subdominios `.is-a.dev` (gratis para proyectos)

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
├── requirements.txt         # Dependencias de Python
├── render.yaml             # Configuración de despliegue en Render
├── render-build.sh         # Script de construcción (instala FFmpeg)
└── README.md
```

## Tecnologías utilizadas

### Backend
- **Flask 3.1.2**: Framework web minimalista y flexible
- **yt-dlp**: Herramienta robusta para descargar contenido de YouTube
- **FFmpeg**: Procesamiento de audio y video
- **Gunicorn**: Servidor WSGI para producción

### Frontend
- **Bootstrap 5.3**: Framework CSS moderno
- **Bootstrap Icons**: Iconografía vectorial
- **JavaScript vanilla**: Sin dependencias adicionales

### Infraestructura
- **Render**: Plataforma de hosting cloud
- **GitHub**: Control de versiones y CI/CD

## Configuración avanzada

### Ajustar calidad de audio

Modifica el parámetro `preferredquality` en `app/services.py` (línea 88):

```python
'preferredquality': '320'  # Para calidad máxima MP3
```

### Cambiar tiempo de limpieza de archivos

Modifica el parámetro `delay` en `app/routes.py` (línea 54):

```python
cleanup_file_delayed(file_path, download_id, delay=60)  # 60 segundos
```

## Solución de problemas comunes

### La app tarda en cargar

**Causa:** El plan gratuito de Render duerme la aplicación después de 15 minutos de inactividad.

**Solución:** La primera carga puede tardar 30-60 segundos. Es completamente normal.

### Error al descargar videos

**Posibles causas:**
- El video tiene restricciones de edad o región
- El enlace no es válido
- El video es privado o fue eliminado

**Solución:** Verifica que el enlace sea público y accesible.

### Descargas lentas

**Causa:** Depende de la duración del video y la calidad.

**Solución:** Videos largos (más de 30 minutos) pueden tardar 1-2 minutos en procesarse.

## Limitaciones del plan gratuito

- **Render Free Plan:**
  - 750 horas/mes de uso
  - La app se duerme después de 15 minutos sin actividad
  - Primera carga después de dormir: 30-60 segundos
  - Límite de CPU y RAM

- **Upgrades disponibles:**
  - Plan Starter: $7/mes (sin sleep, más recursos)

## Seguridad y privacidad

- Los archivos se procesan temporalmente y se eliminan después de 30 segundos
- No se almacenan historiales de descargas
- No se requiere registro de usuarios
- Conexión HTTPS segura (SSL automático en Render)
- Captcha para prevenir abuso automatizado

## Contribuciones

Las contribuciones son bienvenidas y apreciadas. Si deseas mejorar este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/mejora`)
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`)
4. Sube tus cambios (`git push origin feature/mejora`)
5. Abre un Pull Request

### Ideas para contribuir

- Agregar más formatos de descarga (WebM, OGG, etc.)
- Soporte para otros servicios de video (Vimeo, Dailymotion)
- Mejorar la interfaz de usuario
- Optimizar el rendimiento
- Agregar tests unitarios
- Sistema de cola para múltiples descargas
- Previsualización antes de descargar

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

## Descargo de responsabilidad

Esta herramienta está diseñada únicamente para **uso personal y educativo**. Los usuarios son responsables de cumplir con:

- Los términos de servicio de YouTube
- Las leyes de derechos de autor aplicables en su jurisdicción
- Las regulaciones de propiedad intelectual

**No nos hacemos responsables del uso indebido de esta aplicación.** Solo descarga contenido del cual tengas derecho o que sea de dominio público.

## Autor

**Kadir Barquet**  
Desarrollador Python especializado en aplicaciones web

- GitHub: [@Kadir011](https://github.com/Kadir011)
- Proyecto: [download_youtube_web](https://github.com/Kadir011/download_youtube_web)

## Agradecimientos

- A la comunidad de código abierto por las herramientas utilizadas
- A los contribuidores que ayudan a mejorar este proyecto
- Al equipo de yt-dlp por su excelente biblioteca
- A Render por ofrecer hosting gratuito para proyectos

## Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa la sección de **Solución de problemas** arriba
2. Busca en los [Issues](https://github.com/Kadir011/download_youtube_web/issues) existentes
3. Si no encuentras solución, abre un nuevo Issue
4. Describe el problema con el máximo detalle posible

---

**Si este proyecto te resulta útil, considera darle una estrella en GitHub. Tu apoyo es muy apreciado.**

---

## Capturas de pantalla

### Página principal
![Página principal](https://via.placeholder.com/800x400?text=Agregar+captura+de+pantalla)

### Descarga de MP4
![Descarga MP4](https://via.placeholder.com/800x400?text=Agregar+captura+de+pantalla)

### Descarga de MP3
![Descarga MP3](https://via.placeholder.com/800x400?text=Agregar+captura+de+pantalla)

### Tema oscuro
![Tema oscuro](https://via.placeholder.com/800x400?text=Agregar+captura+de+pantalla)

---

## Roadmap

Características planeadas para futuras versiones:

- [ ] Soporte para playlists completas
- [ ] Historial de descargas (opcional, local)
- [ ] Descarga de subtítulos
- [ ] Selector de resolución de video
- [ ] API REST para integraciones
- [ ] Descarga de miniaturas por separado
- [ ] Conversión entre formatos
- [ ] Cola de descargas múltiples
- [ ] PWA (Progressive Web App)
- [ ] Modo offline básico

---

**Última actualización:** Diciembre 2024  
**Versión:** 1.0.0