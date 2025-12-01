from app import create_app

app = create_app()

if __name__ == '__main__':
    # Usamos host y port de la configuración, o defaults
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    app.run(host=host, port=port, debug=debug)