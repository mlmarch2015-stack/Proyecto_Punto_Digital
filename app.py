import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Punto Digital - Villa Ojo de Agua", layout="wide")

# Título principal del proyecto
st.title("💻 Panel de Gestión y Predicción - Punto Digital - Villa Ojo de Agua")
st.markdown("---")

# Cargar datos de manera segura
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("datos.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("datos.csv", encoding="latin1")
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# Limpiar espacios en los nombres de las columnas
df.columns = df.columns.str.strip()

# Crear nombre completo de forma segura según las columnas disponibles
if 'nombre' in df.columns and 'apellido' in df.columns:
    df['Alumno'] = df['nombre'].astype(str) + " " + df['apellido'].astype(str)
elif 'nombre' in df.columns:
    df['Alumno'] = df['nombre'].astype(str)
elif 'id_usuario' in df.columns:
    df['Alumno'] = "Usuario " + df['id_usuario'].astype(str)
else:
    df['Alumno'] = "Estudiante"

# Barra lateral con el título pedido
st.sidebar.header("📁 Proyecto Punto Digital")
st.sidebar.markdown("### Filtros y Parámetros")

# 1. Filtro por Categoría
if 'categoria' in df.columns:
    categorias_disponibles = sorted(df['categoria'].dropna().unique().tolist())
    categoria_sel = st.sidebar.selectbox("Filtrar por Categoría:", ["Todas"] + categorias_disponibles)
    if categoria_sel != "Todas":
        df_filtrado = df[df['categoria'] == categoria_sel]
    else:
        df_filtrado = df
else:
    df_filtrado = df

# 2. Cuadro de búsqueda individual por alumno
alumnos_disponibles = sorted(df_filtrado['Alumno'].dropna().unique().tolist())
alumno_sel = st.sidebar.selectbox("🔍 Buscar Alumno Individual:", ["Todos"] + alumnos_disponibles)

if alumno_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Alumno'] == alumno_sel]

# Métricas principales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Asistencias Registradas", len(df_filtrado))
with col2:
    col_act = 'nombre_actividad' if 'nombre_actividad' in df.columns else ('actividad' if 'actividad' in df.columns else None)
    st.metric("Actividades Únicas", df_filtrado[col_act].nunique() if col_act and col_act in df_filtrado.columns else 0)
with col3:
    st.metric("Usuarios Únicos", df_filtrado['id_usuario'].nunique() if 'id_usuario' in df.columns else 0)

st.markdown("---")

# Módulo de Predicción
st.header("🎯 Módulo de Predicción de Asistencia")
st.markdown("Selecciona los parámetros de la actividad para proyectar la cantidad de asistentes:")

col_p1, col_p2 = st.columns(2)

with col_p1:
    meses_dict = {
        'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 
        'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8, 
        'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
    }
    mes_nombre = st.selectbox("Mes del año:", list(meses_dict.keys()))
    
    dias_nombres = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    dia_sel = st.selectbox("Día de la semana:", list(dias_nombres.values()))

with col_p2:
    actividades_disponibles = sorted(df[col_act].dropna().unique().tolist()) if col_act and col_act in df.columns else []
    actividad_sel = st.selectbox("Nombre de la Actividad / Taller:", actividades_disponibles)
    
    cat_pred = sorted(df['categoria'].dropna().unique().tolist()) if 'categoria' in df.columns else []
    categoria_pred = st.selectbox("Categoría:", cat_pred)

if st.button("📊 Calcular Asistencia Estimada"):
    if col_act and 'categoria' in df.columns:
        subset = df[(df[col_act] == actividad_sel) & (df['categoria'] == categoria_pred)]
    else:
        subset = df
    
    prediccion = int(len(subset) / max(subset['mes'].nunique() if 'mes' in subset.columns else 1, 1) * 1.05) if len(subset) > 0 else 20
    prediccion = max(prediccion, 5)
    st.success(f"✨ Asistencia proyectada estimada para **{actividad_sel}**: **{prediccion} asistentes**.")

st.markdown("---")

# Análisis Gráfico
st.header("📊 Análisis Gráfico y Estadístico")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Top Actividades con Mayor Demanda")
    if len(df_filtrado) > 0 and col_act and col_act in df_filtrado.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        conteo = df_filtrado[col_act].value_counts().head(8)
        sns.barplot(x=conteo.values, y=conteo.index, ax=ax, palette="viridis")
        ax.set_xlabel("Asistencias")
        ax.set_ylabel("Actividad")
        st.pyplot(fig)
    else:
        st.warning("Sin datos.")

with col_g2:
    st.subheader("Evolución de Asistencia por Mes")
    if len(df_filtrado) > 0 and 'mes' in df_filtrado.columns:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        conteo_meses = df_filtrado['mes'].value_counts().sort_index()
        ax2.plot(conteo_meses.index, conteo_meses.values, marker='o', color='b', linestyle='-', linewidth=2)
        ax2.set_xlabel("Mes")
        ax2.set_ylabel("Total Asistencias")
        ax2.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig2)
    else:
        st.warning("Sin datos temporales.")

st.markdown("---")

# Explorador de Datos Registrados
st.header("📋 Explorador de Datos Registrados")
st.markdown("Visualiza en detalle los registros filtrados (con nombres y apellidos de los estudiantes):")
st.dataframe(df_filtrado, use_container_width=True)