import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero de Adjudicación - San Juan", layout="wide")

archivo_excel = "Sorteo_Empleados4.xlsx"

def cargar_datos():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

st.title("🎰 Sistema de Adjudicación por Opciones")

if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("📥 Sincronizar Excel de GitHub"):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.success("Lista sincronizada.")
    
    st.markdown("---")
    # Filtro por Categoría General
    categoria_padre = st.selectbox(
        "Categoría a sortear:",
        ["Pc", "Notebook", "Impresora", "Mobiliario"]
    )
    
    if st.session_state.df_activos is not None:
        st.metric("Personas en bolillero", len(st.session_state.df_activos))

# --- LÓGICA DE SORTEO ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_padre.upper()}", type="primary", use_container_width=True):
        
        # 1. Identificar todas las columnas que pertenecen a esa categoría (ej: Pc - opción 1, Pc - opción 2...)
        cols_categoria = [c for c in st.session_state.df_activos.columns if categoria_padre.lower() in c.lower()]
        
        # 2. Filtrar empleados que tengan al menos un "1" en alguna de esas columnas
        # El .any(axis=1) verifica si hay algún '1' en la fila para esas columnas
        mask = (st.session_state.df_activos[cols_categoria] == 1).any(axis=1)
        participantes_validos = st.session_state.df_activos[mask]
        
        if not participantes_validos.empty:
            indice_ganador = random.choice(participantes_validos.index)
            fila = participantes_validos.loc[indice_ganador]
            
            # 3. Identificar EXACTAMENTE qué opción ganó (la primera que tenga un 1)
            opcion_ganada = "Opción General"
            for col in cols_categoria:
                if fila[col] == 1:
                    opcion_ganada = col
                    break
            
            # 4. Registrar ganador
            registro = {
                'Nombre': fila.get('Nombre', 'N/N'),
                'Sector': fila.get('Sector o área', 'General'),
                'Adjudicado': opcion_ganada
            }
            
            st.session_state.ganadores.insert(0, registro)
            
            # 5. ANULACIÓN DE FILA (Se va del bolillero)
            st.session_state.df_activos = st.session_state.df_activos.drop(indice_ganador)
            st.balloons()
        else:
            st.warning(f"No hay participantes registrados para ninguna opción de {categoria_padre}.")

    # --- MOSTRAR RESULTADO ---
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 2px solid #0078d4; text-align: center;">
                <h3 style="color: #0078d4; margin:0;">🏆 GANADOR ADJUDICADO</h3>
                <h1 style="font-size: 50px; margin:10px 0;">{g['Nombre']}</h1>
                <p style="font-size: 20px;"><b>Sector:</b> {g['Sector']} | <b>Premio:</b> {g['Adjudicado']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- TABLA DE HISTORIAL ---
    st.subheader("📋 Acta de Adjudicaciones Realizadas")
    if st.session_state.ganadores:
        st.table(pd.DataFrame(st.session_state.ganadores))
else:
    st.warning("Carga el Excel desde el panel lateral para iniciar.")
