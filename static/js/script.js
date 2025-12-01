// Diccionario de Traducciones
const translations = {
    es: {
        "download-mp4": "Video MP4",
        "download-mp3": "Audio MP3",
        "welcome-title": "Descargas Rápidas",
        "welcome-desc": "La mejor herramienta para guardar tus videos y canciones favoritas de YouTube sin límites.",
        "btn-video": "Descargar Video",
        "btn-audio": "Descargar Audio",
        "download-mp4-title": "Descargar Video MP4",
        "download-mp3-title": "Descargar Audio MP3",
        "label-url": "Enlace del Video",
        "label-captcha": "Seguridad (Resuelve la suma)",
        "btn-download": "Comenzar Descarga",
        "footer-text": "Desarrollado con pasión"
    },
    en: {
        "download-mp4": "Video MP4",
        "download-mp3": "Audio MP3",
        "welcome-title": "Fast Downloads",
        "welcome-desc": "The best tool to save your favorite YouTube videos and songs without limits.",
        "btn-video": "Download Video",
        "btn-audio": "Download Audio",
        "download-mp4-title": "Download Video MP4",
        "download-mp3-title": "Download Audio MP3",
        "label-url": "Video Link",
        "label-captcha": "Security (Solve Math)",
        "btn-download": "Start Download",
        "footer-text": "Developed with passion"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Manejo del Idioma
    const langSelect = document.getElementById('langSelect');
    const savedLang = localStorage.getItem('selectedLang') || 'es';
    
    // Establecer valor inicial
    langSelect.value = savedLang;
    applyLanguage(savedLang);

    // Evento al cambiar idioma
    langSelect.addEventListener('change', (e) => {
        const lang = e.target.value;
        localStorage.setItem('selectedLang', lang);
        applyLanguage(lang);
    });

    // 2. Manejo del Tema (Oscuro/Claro)
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;
    
    // Recuperar tema guardado o default light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Cambiar icono
        if (theme === 'dark') {
            themeIcon.classList.remove('bi-moon-stars-fill');
            themeIcon.classList.add('bi-sun-fill');
        } else {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-stars-fill');
        }
    }
});

function applyLanguage(lang) {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });
}