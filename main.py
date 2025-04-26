import os
import base64
import shutil
import leer_ini
import insertar_ano

from datetime import datetime
import time
from openai import OpenAI
from dotenv import load_dotenv

# Carga variables de entorno, como tu API KEY
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

CARPETA_IMAGENES,CARPETA_CSV,CARPETA_PROCESADAS,CARPETA_ERROR= leer_ini.leer_folders("SETTINGS.INI")


# Crea carpetas si no existen
os.makedirs(CARPETA_IMAGENES, exist_ok=True)
os.makedirs(CARPETA_CSV, exist_ok=True)
os.makedirs(CARPETA_PROCESADAS, exist_ok=True)

# Prompt personalizado en español
PROMPT = (
    "Extrae únicamente los datos tabulares de esta imagen, en formato CSV plano. "
    "Los encabezados deben ser exactamente: Date, Time, Value, pH, Abs., SFR.\n"
    "Evita incluir cualquier texto, comentario o bloque de código como ```csv o ```.\n"
    "Devuelve solo los datos."
)

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

# Procesamiento principal
def procesar_imagenes():
    archivos = [
        f for f in os.listdir(CARPETA_IMAGENES)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not archivos:
        print("✅ No hay imágenes nuevas para procesar.")
        return

    for archivo in archivos:
        ruta = os.path.join(CARPETA_IMAGENES, archivo)
        print(f"🧠 Procesando: {archivo}")
        imagen_codificada = codificar_base64(ruta)

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
                nueva_ruta = mover_imagen(ruta, archivo,ruta_imagen_error)
                return

            csv_content= asegurar_encabezados_csv(csv_content)

            ruta_csv = generar_nombre_csv()
            with open(ruta_csv, "w", encoding="utf-8") as f:
                f.write(csv_content)
            insertar_ano.insertar_ano(ruta_csv)
            print(f"📄 CSV guardado como: {ruta_csv}")

            nueva_ruta = mover_imagen(ruta, archivo,CARPETA_PROCESADAS)
            print(f"📦 Imagen movida a: {nueva_ruta}")

        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")

if __name__ == "__main__":
    while True:
        procesar_imagenes()
        print(f"Ciclo terminado {datetime.now()}")
        time.sleep(20)


