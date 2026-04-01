import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero de Equipamiento", layout="wide")

archivo_excel = "Sorteo_Empleados2.xlsx"

def cargar_todo_el_excel():
    try:
        df = pd.read_excel(archivo_excel)
        # Limpiamos espacios rebeldes en los nombres de las columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Sistema de Sorteo y Adjudicación")
st.markdown("---")

if 'df_empleados' not in st.session_state:
    st.session_state.df_empleados = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

with st.sidebar:
    st.header("⚙️ Panel de Control")
    if st.button("📥 Sincronizar Excel de GitHub"):
        data = cargar_todo_el_excel()
        if data is not None:
            st.session_state.df_empleados = data
            st.success(f"Cargados {len(data)} registros.")

if st.session_state.df_empleados is not None and not st.session_state.df_empleados.empty:
    
    if st.button("✨ ¡SORTEAR AHORA!", type="primary", use_container_width=True):
        indice_ganador = random.choice(st.session_state.df_empleados.index)
        fila = st.session_state.df_empleados.loc[indice_ganador]
        st.session_state.ganadores.insert(0, fila)
        st.session_state.df_empleados = st.session_state.df_empleados.drop(indice_ganador)
        st.balloons()

    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        
        # Función interna para buscar datos sin errores de mayúsculas
        def obtener_valor(fila, posibles_nombres):
            for nombre in posibles_nombres:
                if nombre in fila.index:
                    val = fila[nombre]
                    return val if pd.notna(val) else "Sin opción"
            return "No encontrado"

        # Mostramos los resultados con un diseño limpio
        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 30px; border-radius: 20px; border: 2px solid #0078d4; text-align: center;">
                <h1 style="color: #0078d4; margin-bottom: 20px;">🏆 GANADOR: {ultimo['Nombre']}</h1>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: left; max-width: 800px; margin: auto;">
                    <div style="font-size: 18px;"><b>📍 Sector / Área:</b> {obtener_valor(ultimo, ['Sector', 'SECTOR', 'Area', 'AREA'])}</div>
                    <div style="font-size: 18px;"><b>🖥️ PC:</b> {obtener_valor(ultimo, ['PC', 'Pc', 'pc'])}</div>
                    <div style="font-size: 18px;"><b>💻 Notebook:</b> {obtener_valor(ultimo, ['Notebook', 'NOTEBOOK', 'notebook'])}</div>
                    <div style="font-size: 18px;"><b>🖨️ Impresora:</b> {obtener_valor(ultimo, ['Impresoras', 'Impresora', 'IMPRESORAS'])}</div>
                    <div style="font-size: 18px;"><b>🪑 Mobiliario:</b> {obtener_valor(ultimo, ['Mobiliario', 'MOBILIARIO', 'mobiliario'])}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("📜 Historial reciente")
        st.dataframe(pd.DataFrame(st.session_state.ganadores), use_container_width=True)
else:
    st.warning("👈 Por favor, sincronizá el Excel desde el panel lateral.")
