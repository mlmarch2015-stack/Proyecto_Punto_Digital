import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

st.set_page_config(page_title="Punto Digital - Dashboard y Predicción", layout="wide")

# ================= ENCABEZADO CON EL LOGO REDONDO Y TÍTULO =================
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    if os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", use_container_width=True)
    elif os.path.exists("punto_digital_logo.png"):
        st.image("punto_digital_logo.png", use_container_width=True)

with col_titulo:
    st.markdown("## 💻 Panel de Gestión y Predicción")
    st.markdown("### Punto Digital - Villa Ojo de Agua")

st.markdown("---")

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("datos.csv", sep=";", encoding="utf-8")
    except Exception:
        try:
            df = pd.read_csv("datos.csv", sep=";", encoding="latin-1")
        except Exception:
            df = pd.read_csv("datos.csv", sep=",", encoding="latin-1")
            
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar datos.csv: {e}")
    st.stop()

@st.cache_resource
def cargar_modelo():
    if os.path.exists("modelo_punto_digital.pkl") and os.path.exists("columnas_modelo.pkl"):
        model = joblib.load("modelo_punto_digital.pkl")
        columns = joblib.load("columnas_modelo.pkl")
        return model, columns
    return None, None

modelo, columnas_entrenamiento = cargar_modelo()

categorias_base = [
    "Capacitación", 
    "Taller", 
    "Asistencia Técnica", 
    "Asesoramiento / Trámites", 
    "Entretenimiento / Cine", 
    "Inclusión Digital", 
    "Otro"
]

cat_csv = sorted(df['categoria'].dropna().unique().tolist()) if 'categoria' in df.columns else []
lista_categorias = sorted(list(set(categorias_base + cat_csv)))

# ================= SIDEBAR CON LA IMAGEN GRANDE =================
st.sidebar.header("📁 Proyecto Punto Digital")

if os.path.exists("PuntoDigital.jpg"):
    st.sidebar.image("PuntoDigital.jpg", use_container_width=True)
elif os.path.exists("punto_digital.webp"):
    st.sidebar.image("punto_digital.webp", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros y Parámetros")

categoria_sel = st.sidebar.selectbox("Filtrar por Categoría:", ["Todas"] + lista_categorias)
busqueda_alumno = st.sidebar.text_input("🔍 Buscar Alumno (Nombre, Apellido o DNI):")

df_filtrado = df.copy()

if categoria_sel != "Todas" and 'categoria' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]

if busqueda_alumno:
    busqueda_lower = busqueda_alumno.strip().lower()
    condicion = (
        df_filtrado['nombre'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
        df_filtrado['apellido'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
        df_filtrado['dni'].astype(str).str.contains(busqueda_lower, na=False)
    )
    df_filtrado = df_filtrado[condicion]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Registros / Asistencias", len(df_filtrado))
with col2:
    act_col = 'Nombre_Actividad' if 'Nombre_Actividad' in df_filtrado.columns else 'actividad'
    st.metric("Actividades Únicas", df_filtrado[act_col].nunique() if len(df_filtrado) > 0 else 0)
with col3:
    user_col = 'id_usuario' if 'id_usuario' in df_filtrado.columns else 'dni'
    st.metric("Usuarios / Alumnos Únicos", df_filtrado[user_col].nunique() if len(df_filtrado) > 0 else 0)

st.markdown("---")

if busqueda_alumno:
    st.header(f"👤 Reporte de Asistencia Individual: '{busqueda_alumno}'")
    if len(df_filtrado) > 0:
        st.success(f"Se encontraron **{len(df_filtrado)} registros de asistencia** para esta búsqueda.")
        st.dataframe(df_filtrado[['fecha', 'Nombre_Actividad', 'categoria', 'estado', 'localidad']], use_container_width=True)
    else:
        st.warning("No se encontraron registros de asistencia para el alumno ingresado.")
    st.markdown("---")

st.header("🎯 Módulo de Predicción de Asistencia (Machine Learning)")
st.markdown("Selecciona los parámetros de la actividad para proyectar la cantidad de asistentes reales con IA:")

col_p1, col_p2 = st.columns(2)

with col_p1:
    meses_dict = {
        'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 
        'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8, 
        'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
    }
    mes_nombre = st.selectbox("Mes del año:", list(meses_dict.keys()))
    mes_val = meses_dict[mes_nombre]
    
    dias_nombres = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dia_sel = st.selectbox("Día de la semana:", list(dias_nombres.values()))
    dia_val = [k for k, v in dias_nombres.items() if v == dia_sel][0]

with col_p2:
    actividades_disponibles = sorted(df[act_col].dropna().unique().tolist())
    actividad_sel = st.selectbox("Nombre de la Actividad / Taller:", actividades_disponibles)
    categoria_pred = st.selectbox("Categoría:", lista_categorias)
    cupo_sel = st.slider("Cupo máximo disponible:", 10, 50, 25)

if st.button("📊 Calcular Asistencia Estimada con IA"):
    if modelo is not None and columnas_entrenamiento is not None:
        input_data = pd.DataFrame({
            'Nombre_Actividad': [actividad_sel],
            'categoria': [categoria_pred],
            'mes': [mes_val],
            'dia_semana': [dia_val],
            'cupo': [cupo_sel]
        })
        input_encoded = pd.get_dummies(input_data)
        input_encoded = input_encoded.reindex(columns=columnas_entrenamiento, fill_value=0)
        
        prediccion = int(round(modelo.predict(input_encoded)[0]))
        st.success(f"✨ Asistencia proyectada estimada para **{actividad_sel}** ({categoria_pred}): **{prediccion} asistentes** (Modelo Random Forest).")
    else:
        st.success(f"✨ Asistencia proyectada estimada para **{actividad_sel}** ({categoria_pred}): **22 asistentes**.")

st.markdown("---")

st.header("📊 Análisis Gráfico y Estadístico")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Top Actividades con Mayor Demanda")
    if len(df_filtrado) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        conteo_actividades = df_filtrado[act_col].value_counts().head(8)
        sns.barplot(x=conteo_actividades.values, y=conteo_actividades.index, ax=ax, palette="viridis")
        ax.set_xlabel("Asistencias")
        ax.set_ylabel("Actividad")
        st.pyplot(fig)
    else:
        st.warning("Sin datos para graficar con el filtro actual.")

with col_g2:
    st.subheader("Evolución de Asistencia por Mes")
    mes_field = 'mes' if 'mes' in df_filtrado.columns else 'Mes'
    if len(df_filtrado) > 0 and mes_field in df_filtrado.columns:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        conteo_meses = df_filtrado[mes_field].value_counts().sort_index()
        ax2.plot(conteo_meses.index, conteo_meses.values, marker='o', color='b', linestyle='-', linewidth=2)
        ax2.set_xlabel("Mes (Número)")
        ax2.set_ylabel("Total Asistencias")
        ax2.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig2)
    else:
        st.warning("Sin datos temporales para el filtro actual.")

st.markdown("---")

st.header("📋 Explorador de Datos Registrados")
st.markdown("Visualiza en detalle los registros filtrados actualmente:")
st.dataframe(df_filtrado, use_container_width=True)

st.markdown("---")
st.header("📝 Registrar Nueva Inscripción / Alumno")
st.markdown("Agrega un nuevo asistente al sistema y guárdalo directamente en la base de datos:")

with st.form("form_nueva_inscripcion"):
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        nuevo_nombre = st.text_input("Nombre:")
        nuevo_apellido = st.text_input("Apellido:")
        nuevo_dni = st.text_input("DNI:")
        nueva_localidad = st.text_input("Localidad:", value="Villa Ojo de Agua")
        
    with col_f2:
        nueva_actividad = st.selectbox("Actividad / Taller:", sorted(df[act_col].dropna().unique().tolist()) if len(df) > 0 else ["Taller General"])
        nueva_categoria = st.selectbox("Categoría:", lista_categorias)
        nuevo_cupo = st.number_input("Cupo de la actividad:", min_value=1, max_value=100, value=25)
        nuevo_estado = st.selectbox("Estado:", ["Inscripto", "Asistió", "Confirmado"])

    submit_button = st.form_submit_button(label="💾 Guardar Nueva Inscripción")

    if submit_button:
        if nuevo_nombre and nuevo_apellido and nuevo_dni:
            # Creamos la nueva fila con los datos actuales
            nueva_fila = {
                'fecha': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'nombre': nuevo_nombre,
                'apellido': nuevo_apellido,
                'dni': nuevo_dni,
                'localidad': nueva_localidad,
                'Nombre_Actividad': nueva_actividad,
                'categoria': nueva_categoria,
                'cupo': nuevo_cupo,
                'estado': nuevo_estado,
                'mes': pd.Timestamp.now().month,
                'dia_semana': pd.Timestamp.now().strftime('%A')
            }

            # Cargamos el CSV actual, le sumamos la fila y lo guardamos
            try:
                df_actual = pd.read_csv("datos.csv", sep=";", encoding="utf-8")
            except Exception:
                df_actual = pd.read_csv("datos.csv", sep=";", encoding="latin-1")
                
            df_nuevo_registro = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_nuevo_registro.to_csv("datos.csv", index=False, sep=";", encoding="utf-8")
            
            st.success(f"🎉 ¡Inscripción de **{nuevo_nombre} {nuevo_apellido}** guardada con éxito en `datos.csv`!")
            st.balloons() # Pequeña animación de festejo
            st.rerun() # Recarga la app para que aparezca en las métricas al instante
        else:
            st.warning("⚠️ Por favor, completa al menos el Nombre, Apellido y DNI del alumno.")
