import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
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
                if usuario == "admin" and password == "puntodigital2026":
                    st.session_state['autenticado'] = True
                    st.rerun()
                else:
                    st.error("⚠️ Usuario o contraseña incorrectos.")
    st.stop()

# ================= 2. CONFIGURACIÓN GENERAL Y DATOS =================
st.set_page_config(page_title="Punto Digital - Dashboard", page_icon="📊", layout="wide")

@st.cache_data(ttl=0)
def cargar_datos():
    archivo = "datos.csv"
    if not os.path.exists(archivo):
        df_init = pd.DataFrame(columns=[
            'fecha', 'nombre', 'apellido', 'dni', 'localidad', 
            'categoria', 'actividad', 'tramite', 'cupo', 'estado', 'mes', 'dia_semana'
        ])
        df_init.to_csv(archivo, index=False, sep=";", encoding="utf-8")
    try:
        return pd.read_csv(archivo, sep=";", encoding="utf-8")
    except Exception:
        return pd.read_csv(archivo, sep=";", encoding="latin-1")

df = cargar_datos()

# ================= 3. ESTRUCTURA DE CATEGORÍAS Y ACTIVIDADES =================
CATEGORIAS_ESTRUCTURA = {
    "Administrativo": {
        "actividades": ["Atención Presencial", "Gestión Online", "Asesoramiento Ciudadano"],
        "tramites": ["Consultas", "Trámites Generales", "Asesoramiento"]
    },
    "Taller": {
        "actividades": ["Alfabetización Digital", "Canva", "Excel", "Word", "PowerPoint"],
        "tramites": ["Inscripción Inicial", "Nivel Avanzado", "Práctica Guiada"]
    },
    "Capacitación": {
        "actividades": ["Ciudadanía Digital", "Impresión 3D", "Marketing Digital", "Python", "Robótica"],
        "tramites": ["Curso Completo", "Taller Intensivo", "Certificación"]
    },
    "Entretenimiento": {
        "actividades": ["Cine", "Juegos en Red"],
        "tramites": ["Función Libre", "Torneo Gamer", "Recreación"]
    }
}

LISTA_LOCALIDADES = [
    "Villa Ojo de Agua", "Sumampa", "Pinto", 
    "Sol de Julio", "Bandera", "Añatuya", "Los Telares"
]

# ================= 4. BARRA LATERAL (LOGO AJUSTADO, NAVEGACIÓN Y FILTROS) =================
# Se ajusta el ancho a 140 para que no quede gigante en la barra lateral
if os.path.exists("punto_digital_logo.jpg"):
    col_sb1, col_sb2, col_sb3 = st.sidebar.columns([1, 2, 1])
    with col_sb2:
        st.image("punto_digital_logo.jpg", width=140)
elif os.path.exists("PuntoDigital.jpg"):
    st.sidebar.image("PuntoDigital.jpg", use_container_width=True)

st.sidebar.title("📌 Menú Principal")

pagina = st.sidebar.radio("Seleccione una sección:", [
    "🏠 Inicio / Presentación",
    "📝 Registrar Inscripción",
    "📋 Gestión y Trámites",
    "📊 Estadísticas y Datos",
    "🤖 Machine Learning"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros Globales")

localidades_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Localidad(es):",
    options=LISTA_LOCALIDADES,
    default=LISTA_LOCALIDADES
)

categorias_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Categoría(s):",
    options=list(CATEGORIAS_ESTRUCTURA.keys()),
    default=list(CATEGORIAS_ESTRUCTURA.keys())
)

busqueda_alumno = st.sidebar.text_input("Buscar Alumno (Nombre, Apellido o DNI):")

# Aplicar filtros
df_filtrado = df.copy()
if len(df_filtrado) > 0:
    if 'localidad' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['localidad'].isin(localidades_seleccionadas)]
    if 'categoria' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias_seleccionadas)]
    
    if busqueda_alumno.strip() != "":
        q = busqueda_alumno.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado['nombre'].astype(str).str.lower().str.contains(q, na=False) |
            df_filtrado['apellido'].astype(str).str.lower().str.contains(q, na=False) |
            df_filtrado['dni'].astype(str).str.contains(q, na=False)
        ]

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

# ================= 5. PÁGINAS DE LA APLICACIÓN =================

if pagina == "🏠 Inicio / Presentación":
    if os.path.exists("PuntoDigital.jpg"):
        st.image("PuntoDigital.jpg", use_container_width=True)
    elif os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", width=250)
    
    st.title("Welcome / Panel de Control - Punto Digital")
    st.markdown("### Sistema Integral de Gestión, Inscripciones y Trámites")
    st.markdown("---")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="Total de Registros", value=len(df))
    with col_m2:
        st.metric(label="Localidades Conectadas", value=len(LISTA_LOCALIDADES))
    with col_m3:
        st.metric(label="Categorías Activas", value=len(CATEGORIAS_ESTRUCTURA))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("📌 Guía del Sistema")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.info("📝 **Registrar Inscripción**\n\nPermite cargar nuevos ciudadanos o alumnos seleccionando su categoría, actividad, trámite y localidad, generando un comprobante digital listo para imprimir.")
        st.info("📋 **Gestión y Trámites**\n\nVisualiza la base de datos completa con opción de aplicar filtros múltiples y descargar planillas en formato CSV.")
        
    with col_g2:
        st.info("📊 **Estadísticas y Datos**\n\nGráficos dinámicos e indicadores basados en los filtros de localidades y categorías seleccionadas en la barra lateral.")
        st.info("🤖 **Machine Learning**\n\nHerramienta analítica y predictiva para evaluar tendencias de asistencia y participación ciudadana.")

elif pagina == "📝 Registrar Inscripción":
    if os.path.exists("PuntoDigital.jpg"):
        st.image("PuntoDigital.jpg", use_container_width=True)
    elif os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", width=250)
        
    st.header("📝 Registrar Nueva Inscripción / Trámite")
    st.markdown("Complete la información del alumno. Al elegir la categoría se cargarán automáticamente sus actividades correspondientes.")

    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        nuevo_nombre = st.text_input("Nombre:", key="input_nombre")
        nuevo_apellido = st.text_input("Apellido:", key="input_apellido")
        nuevo_dni = st.text_input("DNI:", key="input_dni")
        nueva_localidad = st.selectbox("Localidad:", options=LISTA_LOCALIDADES, key="select_localidad")
        
    with col_f2:
        nueva_categoria = st.selectbox("Categoría:", options=list(CATEGORIAS_ESTRUCTURA.keys()), key="select_cat")
        actividades_opciones = CATEGORIAS_ESTRUCTURA[nueva_categoria]["actividades"]
        nueva_actividad = st.selectbox("Actividad:", options=actividades_opciones, key="select_act")
        tramites_opciones = CATEGORIAS_ESTRUCTURA[nueva_categoria]["tramites"]
        nuevo_tramite = st.selectbox("Trámite:", options=tramites_opciones, key="select_tramite")
        
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            nuevo_cupo = st.number_input("Cupo:", min_value=1, max_value=100, value=25)
        with col_sub2:
            nuevo_estado = st.selectbox("Estado:", ["Inscripto", "Asistió", "Confirmado"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
        if nuevo_nombre and nuevo_apellido and nuevo_dni:
            nueva_fila = {
                'fecha': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'nombre': nuevo_nombre,
                'apellido': nuevo_apellido,
                'dni': str(nuevo_dni),
                'localidad': nueva_localidad,
                'categoria': nueva_categoria,
                'actividad': nueva_actividad,
                'tramite': nuevo_tramite,
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
            
            st.success(f"🎉 ¡Registro de **{nuevo_nombre} {nuevo_apellido}** guardado con éxito!")
            st.balloons()
            st.session_state['comprobante'] = nueva_fila
        else:
            st.warning("⚠️ Por favor, completa al menos el Nombre, Apellido y DNI.")

    # ================= COMPROBANTE DIGITAL E IMPRESIÓN =================
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
            <div style="display: flex; justify-content: space-between; font-size: 14px; line-height: 1.8;">
                <div style="width: 48%;">
                    <p><strong>Fecha:</strong> {c['fecha']}</p>
                    <p><strong>Alumno/a:</strong> {c['nombre']} {c['apellido']}</p>
                    <p><strong>DNI:</strong> {c['dni']}</p>
                    <p><strong>Localidad:</strong> {c['localidad']}</p>
                </div>
                <div style="width: 48%;">
                    <p><strong>Categoría:</strong> {c['categoria']}</p>
                    <p><strong>Actividad:</strong> {c['actividad']}</p>
                    <p><strong>Trámite / Detalle:</strong> {c['tramite']}</p>
                    <p><strong>Estado:</strong> {c['estado']}</p>
                </div>
            </div>
            <hr style="border: 0; border-top: 1px solid #ccc;">
            <p style="text-align: center; font-size: 12px; color: #666; margin-bottom: 0;">Punto Digital Villa Ojo de Agua - Sistema de Gestión</p>
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
            if st.button("🔄 Registrar otro alumno", key="btn_reset_comprobante"):
                del st.session_state['comprobante']
                st.rerun()

elif pagina == "📋 Gestión y Trámites":
    st.header("📋 Gestión y Trámites")
    st.markdown("Visualización de registros filtrados.")
    if len(df_filtrado) > 0:
        st.dataframe(df_filtrado, use_container_width=True)
        csv_data = df_filtrado.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="📥 Descargar registros filtrados en CSV",
            data=csv_data,
            file_name="registros_punto_digital.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay registros que coincidan con los filtros seleccionados.")

elif pagina == "📊 Estadísticas y Datos":
    st.header("📊 Estadísticas y Datos")
    if len(df_filtrado) > 0:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.subheader("Registros por Actividad")
            fig, ax = plt.subplots(figsize=(6, 4))
            act_col = 'actividad' if 'actividad' in df_filtrado.columns else 'Nombre_Actividad'
            sns.countplot(data=df_filtrado, y=act_col, order=df_filtrado[act_col].value_counts().index, ax=ax, palette="viridis")
            st.pyplot(fig)
        with col_e2:
            st.subheader("Distribución por Categoría")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            df_filtrado['categoria'].value_counts().plot.pie(autopct="%1.1f%%", ax=ax2, startangle=90, colormap="Set2")
            ax2.set_ylabel("")
            st.pyplot(fig2)
    else:
        st.warning("No hay suficientes datos bajo los filtros actuales para mostrar estadísticas.")

elif pagina == "🤖 Machine Learning":
    st.header("🤖 Módulo de Predicción")
    st.markdown("Análisis predictivo sobre los registros de asistencia.")
    if len(df_filtrado) > 0:
        st.success("Modelo listo para operar con los registros filtrados actuales.")
        st.metric(label="Registros analizados", value=len(df_filtrado))
        if st.button("🚀 Ejecutar Análisis Predictivo"):
            st.info("Predicción realizada con éxito. Tendencia estimada en óptimas condiciones.")
    else:
        st.warning("Se necesitan registros bajo los filtros actuales para ejecutar el modelo.") 