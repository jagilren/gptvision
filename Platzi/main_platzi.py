import base64
import os
import csv
from openai import OpenAI

# Inicializar cliente con la API Key (usa variables de entorno por seguridad)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ruta de carpetas
IMAGEN_PATH = "imagenes/tu_imagen.png"
CSV_OUTPUT_FOLDER = "CSV"
CSV_FILENAME = "resultado.csv"

# Asegura que la carpeta CSV exista
os.makedirs(CSV_OUTPUT_FOLDER, exist_ok=True)

# Función para convertir imagen a base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Convertir imagen
base64_image = encode_image_to_base64(IMAGEN_PATH)

# Enviar solicitud a la API de OpenAI
response = client.chat.completions.create(
    model="gpt-4o",  # también puede usarse 'gpt-4-turbo' o similar
    temperature=0.2,
    messages=[
        {
            "role": "system",
            "content": "Extrae y convierte el contenido tabular de la imagen en formato CSV, separado por comas. Devuélvelo como texto plano, sin explicaciones."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

# Obtener texto del CSV de la respuesta
csv_text = response.choices[0].message.content.strip()

# Guardar como archivo CSV
csv_path = os.path.join(CSV_OUTPUT_FOLDER, CSV_FILENAME)
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_text)

print(f"✅ Archivo CSV generado: {csv_path}")
