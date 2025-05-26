import os
import base64
import shutil
import leer_ini
import insertar_ano
import CN_WAD_IN


from PIL import Image
import hashlib

from pathlib import Path
from datetime import datetime
import time
from openai import OpenAI
from dotenv import load_dotenv


#Genera HASH para hacer comparaciones binarias de imagenes exactas
def hash_imagen(ruta_imagen):
    """Devuelve un hash MD5 de los datos en bruto de la imagen."""
    with Image.open(ruta_imagen) as img:
        return hashlib.md5(img.tobytes()).hexdigest()

#Rutina de comparación de imagenes exactas
def comparar_imagen_con_folder(hash_imagen_actual,  CARPETA_PROCESADAS):
    '''Compara la imagen dada contra todas las imágenes en el folder.'''

    folder_object_proc = Path(CARPETA_PROCESADAS)
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    #Trae todas la imagenes,  y las ordena por fecha de modificación a la inversa
    pict_files = [f for f in folder_object_proc.iterdir() if f.suffix.lower() in image_exts and f.is_file()]
    pict_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    imagenes_iguales = []

    for archivo in pict_files: #os.listdir(CARPETA_PROCESADAS)
        ruta_completa = os.path.join(CARPETA_PROCESADAS, archivo)
        if os.path.isfile(ruta_completa):
            hash_imagen_compare = hash_imagen(ruta_completa)
            try:
                if hash_imagen_compare == hash_imagen_actual:
                    imagenes_iguales.append(archivo)
                    break
            except Exception as e:
                print(f"Error al procesar '{archivo}': {e}")

    return imagenes_iguales



# Codifica imagen a Base64
def codificar_base64(ruta):
    with open(ruta, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


# Genera nombre de archivo CSV sin sobrescribir
def generar_nombre_csv():
    i = 1
    while True:
        nombre = f"resultado_{i}.csv"
        ruta = os.path.join(CARPETA_CSV, nombre)
        if not os.path.exists(ruta):
            return ruta
        i += 1

#Se asegura que la primera linea sea la de los encabezados de los campos
def asegurar_encabezados_csv(contenido_csv: str) -> str:
    encabezados_correctos = "Date,Time,Value,pH,Abs.,SFR"

    # Separar líneas y limpiar espacios
    lineas = [line.strip() for line in contenido_csv.replace(" ", "").strip().splitlines() if line.strip()]

    if not lineas:
        # CSV vacío, solo poner encabezado
        return encabezados_correctos + "\n"

    primera_linea = lineas[0].replace(" ", "").lower()
    encabezado_referencia = encabezados_correctos.replace(" ", "").lower()

    if primera_linea != encabezado_referencia:
        lineas.insert(0, encabezados_correctos)

    return "\n".join(lineas) + "\n"


# Mueve imagen procesada evitando sobrescribir
def mover_imagen(ruta_origen, nombre_archivo,ruta_destino):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre, ext = os.path.splitext(nombre_archivo)
    nuevo_nombre = f"{nombre}_{timestamp}{ext}"
    destino = os.path.join(ruta_destino, nuevo_nombre)
    shutil.move(ruta_origen, destino)
    return destino


def conseguir_rutas(INIFILE):
    CARPETA_IMAGENES, CARPETA_CSV, CARPETA_PROCESADAS, CARPETA_ERROR = leer_ini.leer_folders(INIFILE)
    PROMPT = leer_ini.leer_prompt(INIFILE)
    # Crea carpetas si no existen
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)
    os.makedirs(CARPETA_CSV, exist_ok=True)
    os.makedirs(CARPETA_PROCESADAS, exist_ok=True)
    return CARPETA_IMAGENES, CARPETA_CSV, CARPETA_PROCESADAS, CARPETA_ERROR
    # Prompt personalizado en español

def conseguir_prompt(INIFILE):
    return   leer_ini.leer_prompt(INIFILE)
    pass


# Procesamiento principal
def csv_WAD_OUT(respuesta, csv_content,ruta_mover,archivo_imagen):

    csv_content = asegurar_encabezados_csv(csv_content)

    ruta_csv = generar_nombre_csv()
    with open(ruta_csv, "w", encoding="utf-8") as f:
        f.write(csv_content)
    insertar_ano.insertar_ano(ruta_csv)
    print(f"📄 CSV guardado como: {ruta_csv}")

    nueva_ruta = mover_imagen(ruta_mover, archivo_imagen, CARPETA_PROCESADAS)
    print(f"📦 Imagen movida a: {nueva_ruta}")


def procesar_imagenes_wad_out(CARPETA_IMAGENES, CARPETA_CSV, CARPETA_PROCESADAS, CARPETA_ERROR,PROMPT):
    archivos = [
        f for f in os.listdir(CARPETA_IMAGENES)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not archivos:
        print("✅ No hay imágenes nuevas para procesar.")
        return
    #Evita cargar imágenes repetidas
    for archivo_imagen in archivos:
        ruta_mover = os.path.join(CARPETA_IMAGENES, archivo_imagen)
        imagen_hasheada = hash_imagen(ruta_mover)
        if comparar_imagen_con_folder(imagen_hasheada,CARPETA_PROCESADAS):
            nueva_ruta = mover_imagen(ruta_mover, archivo_imagen, CARPETA_PROCESADAS)
            return

    # Covierte las imágenes en BAES64
    for archivo_imagen in archivos:
        ruta_mover = os.path.join(CARPETA_IMAGENES, archivo_imagen)
        imagen_codificada = codificar_base64(ruta_mover)
        print(f"🧠 Procesando: {archivo_imagen}")


        try:
            respuesta = client.chat.completions.create(
                model="gpt-4o",
                # model='gpt-4-vision-preview'
                # model = 'GPT-4o Mini'
                # model ='GPT-4.1'
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "text", "text": PROMPT },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{imagen_codificada}"
                                }
                            }
                        ]
                    }
                ]
            )

            csv_content = respuesta.choices[0].message.content.strip()
            #Verificamos si GPT Vision  nos devolvio un mensaje de error al analizar la imagem
            if csv_content[0:2].upper()== 'LO':
                #Debemos trasladar la imagen al folder de imagenes no procesadas
                ruta_imagen_error = CARPETA_ERROR
                nueva_ruta = mover_imagen(ruta_mover, archivo_imagen, ruta_imagen_error)
                return

            proceso_CSV_WAD_OUT = csv_WAD_OUT(respuesta,csv_content,ruta_mover,archivo_imagen)

            '''trozo de codigo duplicado'''
            '''csv_content= asegurar_encabezados_csv(csv_content)
            ruta_csv = generar_nombre_csv()
            with open(ruta_csv, "w", encoding="utf-8") as f:
                f.write(csv_content)
            insertar_ano.insertar_ano(ruta_csv)
            print(f"📄 CSV guardado como: {ruta_csv}")

            nueva_ruta = mover_imagen(ruta_mover, archivo_imagen, CARPETA_PROCESADAS)
            print(f"📦 Imagen movida a: {nueva_ruta}")
            '''
        except Exception as e:
            print(f"❌ Error procesando {archivo_imagen}: {e}")


# Carga variables de entorno, como tu API KEY
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

'''PROMPT = (
    "Extrae únicamente los datos tabulares de esta imagen, en formato CSV plano. "
    "Los encabezados deben ser exactamente: Date, Time, Value, pH, Abs., SFR.\n"
    "Evita incluir cualquier texto, comentario o bloque de código como ```csv o ```.\n"
    "Devuelve solo los datos."
)
'''



if __name__ == "__main__":
    while True:
        '''Bloque para Cianura WAT OUT'''
        # Rutas para adquirir y disponer imágenes

        CARPETA_IMAGENES, CARPETA_CSV, CARPETA_PROCESADAS, CARPETA_ERROR=conseguir_rutas("SETTINGS.INI")
        PROMPT = conseguir_prompt("SETTINGS.INI")
        procesar_imagenes_wad_out(CARPETA_IMAGENES, CARPETA_CSV, CARPETA_PROCESADAS, CARPETA_ERROR,PROMPT)
        time.sleep(3)

        '''Bloque para Cianuro WAD IN'''
        print(f"Ciclo terminado {datetime.now()}")
        #CN_WAD_IN.extraer_tabla_desde_imagen("ruta_imagen")
        #time.sleep(3)
