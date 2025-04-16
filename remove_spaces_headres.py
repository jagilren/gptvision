import pandas as pd
from datetime import datetime
# Ruta del archivo CSV original
def remove_spces_headers(archivo_csv):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_csv)

    # Obtener el año actual
    ano_actual = datetime.now().year

    # Procesar y sobrescribir columna "Date"
    df["Date"] = df["Date"].astype(str).apply(lambda x: f"{x.split('/')[0].zfill(2)}/{x.split('/')[1].zfill(2)}/{ano_actual}")

    # Guardar el CSV actualizado (sobrescribe el mismo archivo si lo deseas)
    df.to_csv(archivo_csv, index=False)