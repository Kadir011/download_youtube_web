// Diccionarios con las traducciones
const translations = {
    es: {
        "navbar-home": "Youtube Downloader",
        "download-mp4": "Descargar Video",
        "download-mp3": "Descargar MP3",
        "change-language": "Cambiar",
        "download-content": "Descarga contenido de Youtube",
        "video-download": "Descargar Video",
        "video-url": "URL del Video",
        "download-video-button": "Descargar Video",
        "mp3-download": "Descargar MP3",
        "mp3-url": "URL del Video",
        "download-mp3-button": "Descargar MP3",
        "download-content-description": "Descarga contenido de Youtube de forma automática",
        "alert-success":"Descarga exitosa",
    },
    en: {
        "navbar-home": "Youtube Downloader",
        "download-mp4": "Download Video",
        "download-mp3": "Download MP3",
        "change-language": "Change",
        "download-content": "Download Youtube Content",
        "video-download": "Download Video",
        "video-url": "Video URL",
        "download-video-button": "Download Video",
        "mp3-download": "Download MP3",
        "mp3-url": "Video URL",
        "download-mp3-button": "Download MP3",
        "download-content-description": "Download Youtube content automatically",
        "alert-success":"Download Successful",
    }
};

// Función para cambiar el idioma
function changeLanguage(event) {
    const lang = event.target.value;
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            element.innerText = translations[lang][key];
        }
    });
}

// Función para persistir el idioma en localStorage
function persistLanguage() {
    const lang = document.querySelector('select[name="lang"]').value;
    localStorage.setItem('selectedLang', lang);
    location.reload(); // Recarga la página para reflejar el cambio
}

// Detectar el idioma al cargar la página
window.onload = () => {
    const lang = localStorage.getItem('selectedLang') || 'es'; // Español como predeterminado
    document.querySelector('select[name="lang"]').value = lang;
    changeLanguage({ target: { value: lang } });
};










