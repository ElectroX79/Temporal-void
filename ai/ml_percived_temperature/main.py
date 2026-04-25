import pandas as pd
import numpy as np

def preprocess_weather_data(input_path, output_path="modifiedWeatherHistory.csv"):
    """
    Limpia el dataset de clima, extrae características temporales cíclicas
    y guarda el resultado en un nuevo CSV.
    """
    # 1. Cargar datos
    df = pd.read_csv(input_path)

    # 2. Eliminar columnas innecesarias (usamos errors='ignore' por si alguna no existe)
    cols_to_drop = [
        "Precip Type", "Wind Speed (km/h)", "Wind Bearing (degrees)", 
        "Visibility (km)", "Loud Cover", "Pressure (millibars)", 
        "Daily Summary"
    ]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    # 3. Formatear categorías
    if 'Summary' in df.columns:
        df['Summary'] = df['Summary'].astype('category')

    # 4. Procesamiento de fechas
    if 'Formatted Date' in df.columns:
        df['timestamp'] = pd.to_datetime(df['Formatted Date'], utc=True)
        
        # Extraer componentes básicos
        month = df['timestamp'].dt.month
        day = df['timestamp'].dt.day
        hour = df['timestamp'].dt.hour
        day_of_year = df['timestamp'].dt.dayofyear
        
        # Guardar 'day' (no cíclico según tu código original)
        df['day'] = day

        # 5. Codificación Cíclica (Sin/Cos)
        # Mes
        df['month_sin'] = np.sin(2 * np.pi * month / 12)
        df['month_cos'] = np.cos(2 * np.pi * month / 12)
        # Hora
        df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * hour / 24)
        # Día del año
        df['day_of_year_sin'] = np.sin(2 * np.pi * day_of_year / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * day_of_year / 365)

        # Eliminar columnas temporales intermedias
        df = df.drop(columns=["timestamp", "Formatted Date"], errors='ignore')

    # 6. Guardar y retornar
    df.to_csv(output_path, index=False)
    print(f"Procesamiento completado. Datos guardados en: {output_path}")
    
    return df

# --- Ejemplo de uso ---
# df_final = preprocess_weather_data('weatherHistory.csv')
# print(df_final.head())
# ESTO ES LO IMPORTANTE:
if __name__ == "__main__":
    # Este código solo corre si haces `python3 main.py`
    # No correrá cuando hagas `from main import ...`
    preprocess_weather_data('weatherHistory.csv')