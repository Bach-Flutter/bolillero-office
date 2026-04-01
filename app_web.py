import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero de Equipamiento Pro", layout="wide")

archivo_excel = "Sorteo_Empleados2.xlsx"

def cargar_todo_el_excel():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return None

st.title("🎰 Bolillero de Adjudicación Única")
st.info("Regla: Cada empleado puede ganar solo una categoría por sorteo.")

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
    # Selector de qué estamos sorteando ahora
    categoria_actual = st.selectbox(
        "¿Qué estamos sorteando ahora?",
        ["PC", "Notebook", "Impresoras", "Mobiliario"]
    )

if st.session_state.df_empleados is not None and not st.session_state.df_empleados.empty:
    
    st.subheader(f"Sorteando ahora: {categoria_actual}")
    
    if st.button(f"✨ SORTEAR {categoria_actual}", type="primary", use_container_width=True):
        # 1. Filtramos solo los que aplicaron a esa categoría (que no tengan la celda vacía)
        # Buscamos la columna que coincida con la categoría seleccionada
        col_buscada = next((c for c in st.session_state.df_empleados.columns if categoria_actual.lower() in c.lower()), None)
        
        if col_buscada:
            # Solo participan los que tienen algo escrito en esa columna
            participantes_validos = st.session_state.df_empleados[st.session_state.df_empleados[col_buscada].notna()]
            
            if not participantes_validos.empty:
                indice_ganador = random.choice(participantes_validos.index)
                fila = participantes_validos.loc[indice_ganador].copy()
                
                # Guardamos qué ganó específicamente
                fila['Premio_Asignado'] = f"{categoria_actual}: {fila[col_buscada]}"
                st.session_state.ganadores.insert(0, fila)
                
                # ELIMINACIÓN: Lo sacamos del DataFrame principal para que NO pueda ganar otra cosa
                st.session_state.df_empleados = st.session_state.df_empleados.drop(indice_ganador)
                st.balloons()
            else:
                st.warning(f"No hay más participantes que hayan aplicado a la categoría {categoria_actual}.")
        else:
            st.error(f"No se encontró la columna '{categoria_actual}' en el Excel.")

    # --- MOSTRAR GANADOR ---
    if st.session_state.ganadores:
        ultimo = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 25px; border-radius: 15px; border: 2px solid #22c55e; text-align: center;">
                <h2 style="color: #166534;">🎉 ¡GANADOR DE {categoria_actual.upper()}!</h2>
                <h1 style="font-size: 50px;">{ultimo['Nombre']}</h1>
                <p style="font-size: 20px;"><b>Asignado:</b> {ultimo['Premio_Asignado']}</p>
                <p><b>Sector:</b> {ultimo.get('Sector', 'General')}</p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 Acta de Ganadores (Un premio por persona)")
    if st.session_state.ganadores:
        # Mostramos solo columnas relevantes en el historial
        columnas_ver = ['Nombre', 'Sector', 'Premio_Asignado']
        st.table(pd.DataFrame(st.session_state.ganadores)[columnas_ver])
else:
    st.warning("👈 Cargá la lista en el panel lateral para empezar.")
