import configparser# Leer archivo .ini
def leer_folders(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Obtener rutas
    CARPETA_IMAGENES = config.get('Paths', 'CARPETA_IMAGENES')
    CSV_FOLDER = config.get('Paths', 'CARPETA_CSV')
    CARPETA_PROCESADAS = config.get('Paths', 'CARPETA_PROCESADAS')
    CARPETA_IMAGENES_ERROR = config.get('Paths', 'CARPETA_ERROR')
    return CARPETA_IMAGENES, CSV_FOLDER,CARPETA_PROCESADAS,CARPETA_IMAGENES_ERROR
    # Asegurar que las carpetas existan


def leer_prompt(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)
    # Obtener prompt
    PROMPT = config.get('Prompt', 'Prompt_gpt4o')
    return PROMPT