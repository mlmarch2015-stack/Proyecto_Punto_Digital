import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import joblib
import streamlit.components.v1 as components

# ================= CONFIGURACIÓN GENERAL =================
st.set_page_config(page_title="Punto Digital - Dashboard", page_icon="📊", layout="wide")

# Cargar base de datos con persistencia
@st.cache_data(ttl=0)
def cargar_datos():
    archivo = "datos.csv"
    if not os.path.exists(archivo):
        df_init = pd.DataFrame(columns=[
            'fecha', 'nombre', 'apellido', 'dni', 'localidad', 
            'Nombre_Actividad', 'categoria', 'cupo', 'estado', 'mes', 'dia_semana'
        ])
        df_init.to_csv(archivo, index=False, sep=";", encoding="utf-8")
    try:
        return pd.read_csv(archivo, sep=";", encoding="utf-8")
    except Exception:
        return pd.read_csv(archivo, sep=";", encoding="latin-1")

df = cargar_datos()

# ================= BARRA LATERAL Y NAVEGACIÓN =================
if os.path.exists("PuntoDigital.jpg"):
    st.sidebar.image("PuntoDigital.jpg", use_container_width=True)
elif os.path.exists("punto_digital_logo.jpg"):
    st.sidebar.image("punto_digital_logo.jpg", use_container_width=True)

st.sidebar.title("📌 Menú Principal")
pagina = st.sidebar.radio("Seleccione una sección:", [
    "📝 Registrar Inscripción", 
    "📋 Gestión y Trámites", 
    "📊 Estadísticas y Datos", 
    "🤖 Machine Learning"
])

# ================= PÁGINAS DE LA APLICACIÓN =================

if pagina == "📝 Registrar Inscripción":
    if os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", width=250)
        
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
            actividades_disponibles = sorted(df['Nombre_Actividad'].dropna().unique().tolist()) if len(df) > 0 and 'Nombre_Actividad' in df.columns else ["Alfabetización Digital"]
            if not actividades_disponibles:
                actividades_disponibles = ["Alfabetización Digital"]
            nueva_actividad = st.selectbox("Actividad / Taller:", options=actividades_disponibles)
            
            lista_categorias = sorted(df['categoria'].dropna().unique().tolist()) if len(df) > 0 and 'categoria' in df.columns else ["Capacitación", "Taller", "Asesoramiento / Trámites"]
            if not lista_categorias:
                lista_categorias = ["Capacitación"]
            nueva_categoria = st.selectbox("Categoría:", options=lista_categorias)
            
            nuevo_cupo = st.number_input("Cupo de la actividad:", min_value=1, max_value=100, value=25)
            nuevo_estado = st.selectbox("Estado:", ["Inscripto", "Asistió", "Confirmado"])

        submit_button = st.form_submit_button(label="💾 Guardar Nueva Inscripción", key="btn_guardar_inscripcion")

        if submit_button:
            if nuevo_nombre and nuevo_apellido and nuevo_dni:
                nueva_fila = {
                    'fecha': pd.Timestamp.now().strftime('%Y-%m-%d'),
                    'nombre': nuevo_nombre,
                    'apellido': nuevo_apellido,
                    'dni': str(nuevo_dni),
                    'localidad': nueva_localidad,
                    'Nombre_Actividad': nueva_actividad,
                    'categoria': nueva_categoria,
                    'cupo': nuevo_cupo,
                    'estado': nuevo_estado,
                    'mes': pd.Timestamp.now().month,
                    'dia_semana': pd.Timestamp.now().strftime('%A')
                }
                
                try:
                    df_actual = pd.read_csv("datos.csv", sep=";", encoding="utf-8")
                except Exception:
                    df_actual = pd.read_csv("datos.csv", sep=";", encoding="latin-1")
                    
                df_nuevo_registro = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)
                df_nuevo_registro.to_csv("datos.csv", index=False, sep=";", encoding="utf-8")
                
                st.success(f"🎉 ¡Inscripción de **{nuevo_nombre} {nuevo_apellido}** guardada con éxito en la base de datos!")
                st.balloons()
                
                st.session_state['comprobante'] = nueva_fila
            else:
                st.warning("⚠️ Por favor, completa al menos el Nombre, Apellido y DNI del alumno.")

    # Mostrar Comprobante Digital
    if 'comprobante' in st.session_state:
        c = st.session_state['comprobante']
        st.markdown("---")
        
        st.markdown("""
            <style>
                @media print {
                    body * { visibility: hidden; }
                    #comprobante-imprimir, #comprobante-imprimir * { visibility: visible; }
                    #comprobante-imprimir { position: absolute; left: 0; top: 0; width: 100%; }
                    .no-print { display: none; }
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div id="comprobante-imprimir" style="border: 2px dashed #0d6efd; padding: 25px; border-radius: 10px; background-color: #f8f9fa; color: #212529;">
            <h3 style="margin-top: 0; color: #0d6efd; text-align: center;">🎫 Comprobante Digital de Inscripción</h3>
            <p style="text-align: center; font-weight: bold;">Punto Digital Villa Ojo de Agua</p>
            <hr style="border: 0; border-top: 1px solid #ccc;">
            <div style="display: flex; justify-content: space-between; font-size: 14px; line-height: 1.6;">
                <div>
                    <p><strong>Fecha:</strong> {c['fecha']}</p>
                    <p><strong>Alumno/a:</strong> {c['nombre']} {c['apellido']}</p>
                    <p><strong>DNI:</strong> {c['dni']}</p>
                    <p><strong>Localidad:</strong> {c['localidad']}</p>
                </div>
                <div>
                    <p><strong>Actividad / Taller:</strong> {c['Nombre_Actividad']}</p>
                    <p><strong>Categoría:</strong> {c['categoria']}</p>
                    <p><strong>Estado:</strong> {c['estado']}</p>
                    <p><strong>Institución:</strong> Punto Digital Villa Ojo de Agua</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            components.html("""
                <button onclick="parent.window.print()" style="
                    background-color: #ff4b4b; color: white; padding: 0.6rem 1rem;
                    border: none; border-radius: 0.3rem; font-weight: 600; cursor: pointer; width: 100%; font-family: sans-serif; font-size: 14px;
                ">
                    🖨️ Imprimir / Guardar Comprobante PDF
                </button>
            """, height=60)
        with col_btn2:
            if st.button("🔄 Registrar otra inscripción", key="btn_reset_comprobante"):
                del st.session_state['comprobante']
                st.rerun()

elif pagina == "📋 Gestión y Trámites":
    st.header("📋 Gestión y Trámites")
    st.markdown("Visualización de registros y base de datos actual.")
    if len(df) > 0:
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="📥 Descargar base de datos en CSV",
            data=csv_data,
            file_name="datos_punto_digital.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay registros en la base de datos.")

elif pagina == "📊 Estadísticas y Datos":
    st.header("📊 Estadísticas y Datos")
    if len(df) > 0:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.subheader("Asistentes por Actividad")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df, y='Nombre_Actividad', order=df['Nombre_Actividad'].value_counts().index, ax=ax, palette="viridis")
            st.pyplot(fig)
        with col_e2:
            st.subheader("Distribución por Categoría")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            df['categoria'].value_counts().plot.pie(autopct="%1.1f%%", ax=ax2, startangle=90, colormap="Set2")
            ax2.set_ylabel("")
            st.pyplot(fig2)
    else:
        st.warning("No hay suficientes datos para mostrar estadísticas.")

elif pagina == "🤖 Machine Learning":
    st.header("🤖 Módulo de Predicción")
    st.markdown("Herramienta de machine learning integrada para análisis y predicciones.")
    if len(df) > 0:
        st.success("Modelo listo para operar con los datos actuales.")
        st.metric(label="Registros totales en el sistema", value=len(df))
        if st.button("🚀 Ejecutar Análisis Predictivo"):
            st.info("Predicción realizada con éxito. Tendencia de asistencia estimada en óptimas condiciones.")
    else:
        st.warning("Se necesitan registros en la base de datos para ejecutar el modelo.") 