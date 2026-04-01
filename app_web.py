import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero Pro Chimbas", layout="wide")

archivo_excel = "Sorteo_Empleados3.xlsx"

def cargar_todo_el_excel():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip() # Limpia espacios
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Bolillero de Adjudicación Única")

if 'df_empleados' not in st.session_state:
    st.session_state.df_empleados = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []

with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("📥 Sincronizar Excel de GitHub"):
        data = cargar_todo_el_excel()
        if data is not None:
            st.session_state.df_empleados = data
            st.success(f"Cargados {len(data)} empleados.")
    
    st.markdown("---")
    categoria_actual = st.selectbox(
        "¿Qué estamos sorteando ahora?",
        ["PC", "Notebook", "Impresoras", "Mobiliario"]
    )

if st.session_state.df_empleados is not None and not st.session_state.df_empleados.empty:
    
    if st.button(f"✨ SORTEAR {categoria_actual}", type="primary", use_container_width=True):
        # Buscamos la columna de forma flexible (no importa mayúsculas)
        col_buscada = next((c for c in st.session_state.df_empleados.columns if categoria_actual.lower() in c.lower()), None)
        
        if col_buscada:
            participantes_validos = st.session_state.df_empleados[st.session_state.df_empleados[col_buscada].notna()]
            
            if not participantes_validos.empty:
                indice_ganador = random.choice(participantes_validos.index)
                # Usamos .to_dict() para que sea más fácil de manejar después
                ganador_dict = participantes_validos.loc[indice_ganador].to_dict()
                
                # Normalizamos nombres para el acta
                ganador_dict['Nombre_Ganador'] = ganador_dict.get('Nombre', 'Sin Nombre')
                ganador_dict['Sector_Ganador'] = ganador_dict.get('Sector', ganador_dict.get('SECTOR', 'General'))
                ganador_dict['Premio_Ganado'] = f"{categoria_actual}: {ganador_dict[col_buscada]}"
                
                st.session_state.ganadores.insert(0, ganador_dict)
                st.session_state.df_empleados = st.session_state.df_empleados.drop(indice_ganador)
                st.balloons()
            else:
                st.warning(f"No hay participantes para {categoria_actual}.")
        else:
            st.error(f"No se encontró la columna '{categoria_actual}' en el Excel.")

    # --- MOSTRAR GANADOR ---
    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 15px; border: 2px solid #22c55e; text-align: center;">
                <h2 style="color: #166534;">🎉 GANADOR DE {categoria_actual.upper()}</h2>
                <h1 style="font-size: 45px;">{ultimo['Nombre_Ganador']}</h1>
                <p style="font-size: 18px;"><b>Adjudicado:</b> {ultimo['Premio_Ganado']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- ACTA DE GANADORES (LA PARTE DEL ERROR) ---
    st.subheader("📋 Acta de Ganadores")
    if st.session_state.ganadores:
        # Creamos el DataFrame solo con las columnas fijas que acabamos de inventar
        df_acta = pd.DataFrame(st.session_state.ganadores)
        
        # Filtramos solo las columnas que SIEMPRE van a estar porque las creamos arriba
        columnas_seguras = ['Nombre_Ganador', 'Sector_Ganador', 'Premio_Ganado']
        st.dataframe(df_acta[columnas_seguras], use_container_width=True)
else:
    st.warning("👈 Cargá la lista en el panel lateral.")
