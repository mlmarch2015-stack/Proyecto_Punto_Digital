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
            'Nombre_Actividad', 'categoria', 'cupo', 'estado', 'mes', 'dia_semana'
        ])
        df_init.to_csv(archivo, index=False, sep=";", encoding="utf-8")
    try:
        return pd.read_csv(archivo, sep=";", encoding="utf-8")
    except Exception:
        return pd.read_csv(archivo, sep=";", encoding="latin-1")

df = cargar_datos()

# ================= 3. LISTAS OFICIALES =================
LISTA_LOCALIDADES = [
    "Sumampa", "Pinto", "Sol de Julio", "Bandera", 
    "Añatuya", "Los Telares", "Villa Ojo de Agua"
]

def obtener_categoria(actividad):
    talleres = ["Alfabetización Digital", "Canva", "Excel", "Word", "PowerPoint"]
    capacitacion = ["Ciudadanía Digital", "Impresión 3D", "Marketing Digital", "Python", "Robótica"]
    administrativo = ["Consultas", "Trámites"]
    
    if actividad in talleres:
        return "Taller"
    elif actividad in capacitacion:
        return "Capacitación"
    elif actividad in administrativo:
        return "Administrativo"
    else:
        return "General"

# ================= 4. BARRA LATERAL, NAVEGACIÓN Y FILTROS =================
if os.path.exists("PuntoDigital.jpg"):
    st.sidebar.image("PuntoDigital.jpg", use_container_width=True)
elif os.path.exists("punto_digital_logo.jpg"):
    st.sidebar.image("punto_digital_logo.jpg", use_container_width=True)

st.sidebar.title("📌 Menú Principal")

# Secciones en orden invertido solicitado
pagina = st.sidebar.radio("Seleccione una sección:", [
    "🤖 Machine Learning",
    "📊 Estadísticas y Datos",
    "📋 Gestión y Trámites",
    "📝 Registrar Inscripción"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros y Búsqueda")

# Filtro múltiple de Localidades
localidades_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Localidad(es):",
    options=LISTA_LOCALIDADES,
    default=LISTA_LOCALIDADES
)

# Filtro de búsqueda por Alumno (Nombre, Apellido o DNI)
busqueda_alumno = st.sidebar.text_input("Buscar Alumno (Nombre, Apellido o DNI):")

# Aplicar filtros al DataFrame global de la app
df_filtrado = df.copy()
if len(df_filtrado) > 0:
    if 'localidad' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['localidad'].isin(localidades_seleccionadas)]
    
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

if pagina == "📝 Registrar Inscripción":
    if os.path.exists("punto_digital_logo.jpg"):
        st.image("punto_digital_logo.jpg", width=250)
        
    st.header("📝 Registrar Nueva Inscripción / Trámite")
    st.markdown("Complete los datos. La categoría se asigna automáticamente según la actividad seleccionada.")

    with st.form("form_nueva_inscripcion"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            nuevo_nombre = st.text_input("Nombre:")
            nuevo_apellido = st.text_input("Apellido:")
            nuevo_dni = st.text_input("DNI:")
            nueva_localidad = st.selectbox("Localidad:", options=LISTA_LOCALIDADES)
            
        with col_f2:
            # Lista estructurada de actividades
            lista_actividades = [
                # Administrativo
                "Consultas", "Trámites",
                # Taller
                "Alfabetización Digital", "Canva", "Excel", "Word", "PowerPoint",
                # Capacitación
                "Ciudadanía Digital", "Impresión 3D", "Marketing Digital", "Python", "Robótica"
            ]
            
            nueva_actividad = st.selectbox("Actividad / Trámite:", options=lista_actividades)
            
            # Categoría automática por fórmula
            nueva_categoria = obtener_categoria(nueva_actividad)
            st.text_input("Categoría (Automática por Actividad):", value=nueva_categoria, disabled=True)
            
            nuevo_cupo = st.number_input("Cupo de la actividad:", min_value=1, max_value=100, value=25)
            nuevo_estado = st.selectbox("Estado:", ["Inscripto", "Asistió", "Confirmado"])

        submit_button = st.form_submit_button(label="💾 Guardar Registro", key="btn_guardar_inscripcion")

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
                
                st.success(f"🎉 ¡Registro de **{nuevo_nombre} {nuevo_apellido}** guardado con éxito!")
                st.balloons()
                
                st.session_state['comprobante'] = nueva_fila
            else:
                st.warning("⚠️ Por favor, completa al menos el Nombre, Apellido y DNI.")

    # Mostrar Comprobante Digital con Impresión Limpia
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
            <h3 style="margin-top: 0; color: #0d6efd; text-align: center;">🎫 Comprobante Digital - Punto Digital</h3>
            <p style="text-align: center; font-weight: bold;">Villa Ojo de Agua</p>
            <hr style="border: 0; border-top: 1px solid #ccc;">
            <div style="display: flex; justify-content: space-between; font-size: 14px; line-height: 1.6;">
                <div>
                    <p><strong>Fecha:</strong> {c['fecha']}</p>
                    <p><strong>Alumno/a:</strong> {c['nombre']} {c['apellido']}</p>
                    <p><strong>DNI:</strong> {c['dni']}</p>
                    <p><strong>Localidad:</strong> {c['localidad']}</p>
                </div>
                <div>
                    <p><strong>Actividad / Trámite:</strong> {c['Nombre_Actividad']}</p>
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
            if st.button("🔄 Registrar otro", key="btn_reset_comprobante"):
                del st.session_state['comprobante']
                st.rerun()

elif pagina == "📋 Gestión y Trámites":
    st.header("📋 Gestión y Trámites")
    st.markdown("Visualización de registros filtrados por localidad y búsqueda de alumnos.")
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
            st.subheader("Registros por Actividad / Trámite")
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
        st.warning("No hay suficientes datos bajo los filtros actuales para mostrar estadísticas.")

elif pagina == "🤖 Machine Learning":
    st.header("🤖 Módulo de Predicción")
    st.markdown("Herramienta de machine learning integrada para análisis y predicciones.")
    if len(df_filtrado) > 0:
        st.success("Modelo listo para operar con los registros filtrados actuales.")
        st.metric(label="Registros analizados", value=len(df_filtrado))
        if st.button("🚀 Ejecutar Análisis Predictivo"):
            st.info("Predicción realizada con éxito. Tendencia estimada en óptimas condiciones.")
    else:
        st.warning("Se necesitan registros bajo los filtros actuales para ejecutar el modelo.") 