# ejemplo_razonamiento.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Inicializamos el cliente (reemplaza "TU_API_KEY_AQUI" con tu API Key real)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# Llamada al modelo de razonamiento "o4-mini"
response = client.responses.create(
    model="o4-mini-2025-04-16",
    input='''Calcula la tasa de sólidos de un DAF, dissolved Air floculation, si el IML es 13.5 KgSS/M3 y la Tasa de flotacion del DAF es 7.5 \n
    Recuerda que los valores aceptables para Tasa de flotación están entre 80 KgSS/m2/d y 240 KgSS/m2/d
    El caudal que maneja la planta de tratamiento actualmente es de 40 m3/h
    Actualmente se recircula un 30% del Agua Residual en el DAF
    Tdos los demás parámetros, como relación A/S, Presión, solubilidad del aire en el agua, etc están en valores correctos, acorde a los estandares de la industria de fabricantes de DAF
    '''

)

print(response.output_text)


