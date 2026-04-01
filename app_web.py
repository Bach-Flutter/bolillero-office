import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero Pro - Exclusión Real", layout="wide")

archivo_excel = "Sorteo_Empleados3.xlsx"

def cargar_todo_el_excel():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Bolillero de Adjudicación Única")
st.caption("Nota: Una vez que un empleado gana, es eliminado del bolillero para el resto del evento.")

# --- ESTADO DE LA SESIÓN ---
if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None # Aquí guardamos los que NO han ganado
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("⚙️ Control del Sorteo")
    if st.button("📥 Cargar/Reiniciar Lista"):
        data = cargar_todo_el_excel()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.success("Lista cargada desde GitHub.")
    
    st.markdown("---")
    categoria_actual = st.selectbox(
        "¿Qué categoría sorteamos?",
        ["PC", "Notebook", "Impresoras", "Mobiliario"]
    )
    
    if st.session_state.df_activos is not None:
        st.metric("Participantes Restantes", len(st.session_state.df_activos))

# --- LÓGICA PRINCIPAL ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_actual.upper()}", type="primary", use_container_width=True):
        # 1. Identificar columna (flexible con mayúsculas/minúsculas)
        col_buscada = next((c for c in st.session_state.df_activos.columns if categoria_actual.lower() in c.lower()), None)
        
        if col_buscada:
            # 2. Filtrar solo los que aplicaron a este premio y siguen ACTIVOS
            participantes_validos = st.session_state.df_activos[st.session_state.df_activos[col_buscada].notna()]
            
            if not participantes_validos.empty:
                # 3. Elegir ganador
                indice_ganador = random.choice(participantes_validos.index)
                ganador_info = participantes_validos.loc[indice_ganador].to_dict()
                
                # 4. Crear registro para el acta
                registro = {
                    'Nombre': ganador_info.get('Nombre', 'N/D'),
                    'Sector': ganador_info.get('Sector', ganador_info.get('SECTOR', 'General')),
                    'Premio': f"{categoria_actual}: {ganador_info[col_buscada]}"
                }
                
                st.session_state.ganadores.insert(0, registro)
                
                # 5. ELIMINACIÓN PERMANENTE: Lo quitamos de los activos
                st.session_state.df_activos = st.session_state.df_activos.drop(indice_ganador)
                st.balloons()
            else:
                st.warning(f"No hay más personas disponibles que hayan aplicado para {categoria_actual}.")
        else:
            st.error(f"No se encontró la columna '{categoria_actual}' en tu Excel.")

    # --- VISUALIZACIÓN DEL GANADOR ---
    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 25px; border-radius: 15px; border: 3px solid #22c55e; text-align: center; margin-bottom: 20px;">
                <h2 style="color: #166534; margin: 0;">¡NUEVO GANADOR!</h2>
                <h1 style="font-size: 50px; margin: 10px 0;">{ultimo['Nombre']}</h1>
                <p style="font-size: 20px;"><b>Sector:</b> {ultimo['Sector']} | <b>Premio:</b> {ultimo['Premio']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- ACTA DE GANADORES ---
    st.subheader("📜 Acta Oficial de Ganadores")
    if st.session_state.ganadores:
        st.dataframe(pd.DataFrame(st.session_state.ganadores), use_container_width=True)
else:
    st.warning("Carga la lista de empleados para empezar el sorteo.")
