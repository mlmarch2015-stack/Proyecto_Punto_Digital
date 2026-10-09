import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

print("Cargando y preparando los datos...")
df = pd.read_csv('datos.csv', sep=';', encoding='latin-1')

df['fecha'] = pd.to_datetime(df['fecha'])
if 'mes' not in df.columns:
    df['mes'] = df['fecha'].dt.month
if 'dia_semana' not in df.columns:
    df['dia_semana'] = df['fecha'].dt.day_name()

columnas_agrupacion = ['fecha', 'Nombre_Actividad', 'categoria', 'mes', 'dia_semana', 'cupo']
df_agrupado = df.groupby(columnas_agrupacion).size().reset_index(name='asistencia_real')

df_agrupado['categoria'] = df_agrupado['categoria'].astype('category')

print("Datos agrupados para el modelo. Total de registros:", len(df_agrupado))

X = pd.get_dummies(df_agrupado[['Nombre_Actividad', 'categoria', 'mes', 'dia_semana', 'cupo']], drop_first=True)
y = df_agrupado['asistencia_real']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
print(f"Modelo entrenado con éxito. Error Absoluto Medio (MAE): {mae:.4f}")

joblib.dump(model, 'modelo_punto_digital.pkl')
joblib.dump(X.columns.tolist(), 'columnas_modelo.pkl')
print("Modelo guardado como 'modelo_punto_digital.pkl'")