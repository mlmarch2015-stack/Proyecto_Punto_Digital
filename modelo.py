import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("Cargando y preparando los datos...")

# 1. Cargar el archivo de datos unificados o generar el dataset consolidado
df = pd.read_csv('datos.csv', sep=';', encoding='latin-1')

# Si el CSV básico falta columnas, podemos reconstruir o asegurar que existan:
# Vamos a verificar y normalizar las columnas necesarias para el modelo de Machine Learning.
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'])
    if 'mes' not in df.columns:
        df['mes'] = df['fecha'].dt.month
    if 'dia_semana' not in df.columns:
        df['dia_semana'] = df['fecha'].dt.day_name()

# Si faltan nombre_actividad o categoria, rellenamos o mapeamos valores por defecto seguros
if 'nombre_actividad' not in df.columns:
    df['nombre_actividad'] = 'Capacitación General'
if 'categoria' not in df.columns:
    df['categoria'] = 'General'

# Agrupar asistencias para predecir volumen/asistencia
# (Ajusta los nombres según las columnas reales del DataFrame)
columnas_agrupacion = [col for col in ['fecha', 'nombre_actividad', 'categoria', 'mes', 'dia_semana'] if col in df.columns]

if len(columnas_agrupacion) > 0:
    df_agrupado = df.groupby(columnas_agrupacion).size().reset_index(name='asistencia_real')
else:
    df_agrupado = df.copy()
    df_agrupado['asistencia_real'] = 1

print("Datos preparados con éxito. Filas procesadas:", len(df_agrupado))
print(df_agrupado.head())