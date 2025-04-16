import configparser# Leer archivo .ini
def leer_ini(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Obtener rutas
    CARPETA_IMAGENES = config.get('Paths', 'CARPETA_IMAGENES')
    CSV_FOLDER = config.get('Paths', 'CARPETA_CSV')
    CARPETA_PROCESADAS = config.get('Paths', 'CARPETA_PROCESADAS')
    return CARPETA_IMAGENES, CSV_FOLDER,CARPETA_PROCESADAS
    # Asegurar que las carpetas existan
