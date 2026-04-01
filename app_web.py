import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Bolillero de Equipamiento", layout="wide")

# Nombre del archivo en tu GitHub
archivo_excel = "Sorteo_Empleados2.xlsx"

def cargar_todo_el_excel():
    try:
        # Leemos el Excel completo
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip() # Limpiar espacios en encabezados
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Sistema de Sorteo y Adjudicación")
st.markdown("---")

# --- INICIALIZACIÓN ---
if 'df_empleados' not in st.session_state:
    st.session_state.df_empleados = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    if st.button("📥 Sincronizar Excel de GitHub"):
        data = cargar_todo_el_excel()
        if data is not None:
            st.session_state.df_empleados = data
            st.success(f"Cargados {len(data)} registros correctamente.")

# --- CUERPO PRINCIPAL ---
if st.session_state.df_empleados is not None and not st.session_state.df_empleados.empty:
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Realizar Sorteo")
        if st.button("✨ ¡SORTEAR AHORA!", type="primary", use_container_width=True):
            # Elegimos una fila al azar de los que quedan
            indice_ganador = random.choice(st.session_state.df_empleados.index)
            fila = st.session_state.df_empleados.loc[indice_ganador]
            
            # Guardamos los datos del ganador
            st.session_state.ganadores.insert(0, fila)
            
            # Eliminamos al ganador para que no salga dos veces
            st.session_state.df_empleados = st.session_state.df_empleados.drop(indice_ganador)
            
            st.balloons()

    # Mostrar el último ganador con sus detalles
    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        
        with col1:
            st.markdown(f"""
                <div style="background-color: #f0f7ff; padding: 25px; border-radius: 15px; border-left: 10px solid #0078d4; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #0078d4; margin-top: 0;">🏆 GANADOR: {ultimo['Nombre']}</h2>
                    <p><b>📍 Sector:</b> {ultimo.get('Sector', 'No especificado')}</p>
                    <hr>
                    <p><b>🖥️ Opción PC:</b> {ultimo.get('PC', 'N/A')}</p>
                    <p><b>💻 Opción Notebook:</b> {ultimo.get('Notebook', 'N/A')}</p>
                    <p><b>🖨️ Opción Impresora:</b> {ultimo.get('Impresoras', 'N/A')}</p>
                    <p><b>🪑 Opción Mobiliario:</b> {ultimo.get('Mobiliario', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("📜 Historial de Adjudicaciones")
        if st.session_state.ganadores:
            # Convertimos la lista de ganadores de nuevo a un DataFrame para mostrar una tabla linda
            historial_df = pd.DataFrame(st.session_state.ganadores)
            st.dataframe(historial_df, use_container_width=True)
            st.write(f"Quedan **{len(st.session_state.df_empleados)}** personas en el bolillero.")
else:
    st.warning("👈 Por favor, hacé clic en 'Sincronizar Excel' para comenzar.")
