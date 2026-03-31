import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero Rivulis 2026", layout="centered")

st.title("🎰 Sorteo de Equipos")

# --- FUNCIÓN PARA LEER EL EXCEL ---
def cargar_datos():
    try:
        # Cargamos el archivo
        df = pd.read_excel("Sorteo_Empleados.xlsx")
        
        # PASO 1: Limpiamos espacios en blanco en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        # PASO 2: Mostramos en la web qué columnas detectó (solo para debug)
        # st.write(f"Columnas detectadas: {list(df.columns)}") 

        # PASO 3: Buscamos la columna 'Nombre' (sin importar mayúsculas/minúsculas)
        columna_objetivo = None
        for col in df.columns:
            if col.lower() == "nombre":
                columna_objetivo = col
                break
        
        if columna_objetivo:
            # Retornamos la lista sin valores vacíos
            return df[columna_objetivo].dropna().astype(str).tolist()
        else:
            st.error(f"No encontré 'Nombre'. Columnas detectadas: {list(df.columns)}")
            return []

    except Exception as e:
        st.error(f"Error técnico: {e}")
        return []

# --- INICIALIZACIÓN DE SESIÓN ---
if 'lista_empleados' not in st.session_state:
    st.session_state.lista_empleados = []
if 'historial_ganadores' not in st.session_state:
    st.session_state.historial_ganadores = []

# --- INTERFAZ ---
with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("Cargar Lista desde Excel"):
        nombres = cargar_datos()
        if nombres:
            st.session_state.lista_empleados = nombres
            st.session_state.historial_ganadores = []
            st.success(f"¡{len(nombres)} empleados cargados!")

# Sección Principal
if st.session_state.lista_empleados:
    st.info(f"Participantes restantes en el bolillero: {len(st.session_state.lista_empleados)}")
    
    if st.button("✨ SORTEAR GANADOR", type="primary", use_container_width=True):
        ganador = random.choice(st.session_state.lista_empleados)
        st.session_state.lista_empleados.remove(ganador)
        st.session_state.historial_ganadores.insert(0, ganador)
        
        # Efecto visual del ganador
        st.balloons()
        st.markdown(f"""
            <div style="background-color: #1e3a8a; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #3b82f6;">
                <h2 style="color: white; margin: 0;">¡EL GANADOR ES!</h2>
                <h1 style="color: #fbbf24; font-size: 50px; margin: 10px;">{ganador}</h1>
            </div>
        """, unsafe_allow_html=True)

    # Historial
    if st.session_state.historial_ganadores:
        st.subheader("📜 Ganadores de hoy:")
        for i, g in enumerate(st.session_state.historial_ganadores):
            st.write(f"{len(st.session_state.historial_ganadores)-i}. **{g}**")
else:
    st.warning("⚠️ Primero hacé clic en 'Cargar Lista desde Excel' en el menú de la izquierda.")