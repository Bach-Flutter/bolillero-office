import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero Final - San Juan", layout="wide")

archivo_excel = "Sorteo_Empleados3.xlsx"

def cargar_todo_el_excel():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Sistema de Adjudicación con Anulación de Fila")
st.caption("Regla de Oro: El ganador es eliminado automáticamente de todas las categorías restantes.")

# --- ESTADO DE LA SESIÓN (La memoria del programa) ---
if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None 
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

# --- PANEL DE CONTROL LATERAL ---
with st.sidebar:
    st.header("⚙️ Administración")
    if st.button("📥 Cargar Lista Nueva (Reset)"):
        data = cargar_todo_el_excel()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.success("Lista sincronizada y lista para el sorteo.")
    
    st.markdown("---")
    categoria_actual = st.selectbox(
        "¿Qué categoría sorteamos ahora?",
        ["PC", "Notebook", "Impresoras", "Mobiliario"]
    )
    
    if st.session_state.df_activos is not None:
        st.metric("Total Participantes en Bolillero", len(st.session_state.df_activos))

# --- LÓGICA DEL SORTEO ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_actual.upper()}", type="primary", use_container_width=True):
        # 1. Buscar la columna correcta (sin importar mayúsculas)
        col_buscada = next((c for c in st.session_state.df_activos.columns if categoria_actual.lower() in c.lower()), None)
        
        if col_buscada:
            # 2. Solo participan los que tengan algo anotado en esa columna Y sigan activos
            participantes_validos = st.session_state.df_activos[st.session_state.df_activos[col_buscada].notna()]
            
            if not participantes_validos.empty:
                # 3. SORTEO: Elegimos el índice de la fila
                indice_ganador = random.choice(participantes_validos.index)
                
                # 4. CAPTURAMOS LOS DATOS antes de borrar la fila
                info = participantes_validos.loc[indice_ganador].to_dict()
                
                registro_final = {
                    'Nombre': info.get('Nombre', 'N/D'),
                    'Sector': info.get('Sector', info.get('SECTOR', 'General')),
                    'Premio': f"{categoria_actual}: {info[col_buscada]}"
                }
                
                # 5. ANULACIÓN DE FILA: Se elimina del bolillero permanentemente
                st.session_state.df_activos = st.session_state.df_activos.drop(indice_ganador)
                
                # Guardamos en el acta
                st.session_state.ganadores.insert(0, registro_final)
                st.balloons()
            else:
                st.warning(f"No hay más personas que hayan aplicado para la categoría: {categoria_actual}")
        else:
            st.error(f"No encontré la columna '{categoria_actual}' en el archivo Excel.")

    # --- PRESENTACIÓN DEL GANADOR ---
    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 25px; border-radius: 15px; border: 3px solid #22c55e; text-align: center; margin-bottom: 20px;">
                <h1 style="color: #166534; font-size: 55px; margin-bottom: 10px;">{ultimo['Nombre']}</h1>
                <h2 style="color: #15803d; margin: 0;">{ultimo['Premio']}</h2>
                <p style="font-size: 18px; color: #166534; margin-top: 10px;">Sector: {ultimo['Sector']}</p>
                <p style="color: #dc2626; font-weight: bold;">⚠️ Fila anulada para el resto del sorteo</p>
            </div>
        """, unsafe_allow_html=True)

    # --- ACTA DE RESULTADOS ---
    st.subheader("📋 Acta de Ganadores (Registros Inamovibles)")
    if st.session_state.ganadores:
        st.table(pd.DataFrame(st.session_state.ganadores))
else:
    st.warning("👈 Por favor, carga la lista de empleados para comenzar.")
