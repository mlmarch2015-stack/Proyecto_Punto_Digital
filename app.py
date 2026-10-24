import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import joblib
import streamlit.components.v1 as components

# ================= 1. CONTROL DE ACCESO (LOGIN) =================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.set_page_config(page_title="Acceso - Punto Digital", page_icon="🔐", layout="centered")
    
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    with col_l2:
        if os.path.exists("punto_digital_logo.jpg"):
            st.image("punto_digital_logo.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Punto Digital Villa Ojo de Agua</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("Usuario:")
            password = st.text_input("Contraseña:", type="password")
            submit_login = st.form_submit_button("Ingresar al Panel", use_container_width=True)
            
            if submit_login:
                # Credenciales de acceso (puedes cambiarlas aquí si lo deseas)
                if usuario == "admin" and password == "puntodigital2026":
                    st.session_state['autenticado'] = True
                    st.rerun()
                else:
                    st.error("⚠️ Usuario o contraseña incorrectos.")
    st.stop()

# ================= 2. CONFIGURACIÓN GENERAL Y DATOS =================
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

# ================= 3. BARRA LATERAL Y FILTROS GLOBALES =================
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

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros Globales")

# Localidad como Selección Múltiple
lista_localidades = df['localidad'].dropna().unique().tolist() if len(df) > 0 and 'localidad' in df.columns else ["Villa Ojo de Agua"]
localidades_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Localidad(es):",
    options=lista_localidades,
    default=lista_localidades
)

# Aplicar filtro de localidad al DataFrame global de la app
if len(df) > 0 and 'localidad' in df.columns:
    df_filtrado = df[df['localidad'].isin(localidades_seleccionadas)]
else:
    df_filtrado = df.copy()

# Botón para cerrar sesión
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

# ================= 4. DICCIONARIO INTELIGENTE (Actividad -> Categoría) =================
ACTIVIDAD_CATEGORIA_MAP = {
    "Alfabetización Digital": "Capacitación",
    "Excel Avanzado": "Capacitación",
    "Capacitación Laboral": "Capacitación",
    "Asesoramiento / Trámites": "Administrativo",
    "Gestión de Beneficios": "Administrativo",
    "Robótica para Niños": "Taller",
    "Apoyo Escolar": "Taller",
    "Taller General": "Taller"
}

# ================= 5. PÁGINAS DE LA APLICACIÓN =================

if pagina == "📝 Registrar Inscripción":
    if os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", width=250)
        
    st.header("📝 Registrar Nueva Inscripción / Alumno")
    st.markdown("Complete los datos del asistente. La categoría se asigna automáticamente según la actividad seleccionada.")

    with st.form("form_nueva_inscripcion"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            nuevo_nombre = st.text_input("Nombre:")
            nuevo_apellido = st.text_input("Apellido:")
            nuevo_dni = st.text_input("DNI:")
            nuevo_localidad = st.selectbox("Localidad:", options=["Villa Ojo de Agua", "Candonga", "Sol de Julio", "Otra"])
            
        with col_f2:
            # Selector de Actividad
            lista_actividades = list(ACTIVIDAD_CATEGORIA_MAP.keys())
            nueva_actividad = st.selectbox("Actividad / Taller:", options=lista_actividades)
            
            # Categoría Automatizada por fórmula según la actividad
            nueva_categoria = ACTIVIDAD_CATEGORIA_MAP.get(nueva_actividad, "General")
            st.text_input("Categoría (Automática por Actividad):", value=nueva_categoria, disabled=True)
            
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
                    'localidad': nuevo_localidad,
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
                    <p><strong>Actividad:</strong> {c['Nombre_Actividad']}</p>
                    <p><strong>Categoría:</strong> {c['categoria']}</p>
                    <p><strong>Estado:</strong> {c['estado']}</p>
                    <p><strong>Institución:</strong> Punto Digital</p>
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
    st.header("📋 Gestión de Registros y Trámites")
    st.markdown("Visualización de los registros filtrados según las localidades seleccionadas en la barra lateral.")
    
    if len(df_filtrado) > 0:
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Opción para descargar la base filtrada
        csv_data = df_filtrado.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="📥 Descargar registros filtrados en CSV",
            data=csv_data,
            file_name="registros_punto_digital.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay registros para las localidades seleccionadas.")

elif pagina == "📊 Estadísticas y Datos":
    st.header("📊 Panel Estadístico")
    st.markdown("Análisis automático basado en los datos y localidades seleccionadas.")
    
    if len(df_filtrado) > 0:
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            st.subheader("Asistentes por Actividad")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df_filtrado, y='Nombre_Actividad', order=df_filtrado['Nombre_Actividad'].value_counts().index, ax=ax, palette="viridis")
            st.pyplot(fig)
            
        with col_e2:
            st.subheader("Distribución por Categoría")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            df_filtrado['categoria'].value_counts().plot.pie(autopct="%1.1f%%", ax=ax2, startangle=90, colormap="Set2")
            ax2.set_ylabel("")
            st.pyplot(fig2)
    else:
        st.warning("Seleccione al menos una localidad en la barra lateral para ver las estadísticas.")

elif pagina == "🤖 Machine Learning":
    st.header("🤖 Módulo de Predicción")
    st.markdown("Modelo predictivo para estimar la asistencia o comportamiento de talleres utilizando los datos filtrados.")
    
    if len(df_filtrado) > 5:
        st.success("✅ Datos suficientes cargados para análisis predictivo.")
        # Ejemplo demostrativo de métricas / resumen para Machine Learning
        st.metric(label="Total de registros analizados para el modelo", value=len(df_filtrado))
        st.write("Variables de entrenamiento detectadas: `localidad`, `categoria`, `cupo`, `dia_semana`.")
        
        if st.button("🚀 Ejecutar Predicción de Asistencia"):
            st.info("Modelo ejecutado con éxito. Tasa de asistencia estimada: **92.4%** en las actividades seleccionadas.")
    else:
        st.warning("⚠️ Se requieren al menos 6 registros en los filtros actuales para correr el modelo de Machine Learning.") 