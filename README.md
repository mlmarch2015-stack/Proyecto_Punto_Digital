# 📊 Sistema Predictivo de Demanda - Punto Digital Villa Ojo de Agua

Herramienta de inteligencia artificial y análisis de datos diseñada para optimizar la planificación operativa y la asignación de recursos en el **Punto Digital Villa Ojo de Agua**, reemplazando los cupos fijos tradicionales por un modelo basado en la demanda real.

---

## 🚀 Descripción del Proyecto
Tradicionalmente, la gestión de talleres se basaba en cupos teóricos estáticos que no reflejaban la asistencia efectiva. Este proyecto transforma los registros históricos (`datos.csv`) en un modelo predictivo capaz de anticipar con precisión el volumen de asistentes (`asistencia_real`) por actividad, facilitando una gestión basada en evidencia empírica.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.14
* **Manipulación de Datos:** Pandas
* **Machine Learning:** Scikit-Learn (`Random Forest Regressor`)
* **Interfaz Gráfica:** Streamlit

## ⚙️ Estructura y Funcionamiento Técnico
1. **Carga y Normalización:** Lectura del archivo de datos con codificación `latin-1`, traducción automática de etiquetas de meses y días del inglés al español, y agrupación por fecha, actividad y categoría.
2. **Ingeniería de Características (*Feature Engineering*):** Codificación de variables categóricas a numéricas para su procesamiento por el algoritmo de Machine Learning.
3. **Modelado Predictivo:** Entrenamiento mediante un bosque aleatorio (*Random Forest*), alcanzando un **Error Absoluto Medio (MAE) de ~0.87**, lo que garantiza alta precisión para grupos pequeños.
4. **Interfaz de Usuario:** Aplicación web interactiva local con menús desplegables para consultas instantáneas.

---

## 📥 Guía de Instalación y Ejecución

1. **Clonar o abrir la carpeta del proyecto** en tu terminal.
2. **Instalar las dependencias necesarias:**
   ```bash
   pip install pandas scikit-learn streamlit
   