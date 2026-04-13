import streamlit as st
import pandas as pd
import random
import re
import requests # <-- Crucial para conectar con Power Automate

st.set_page_config(page_title="Bolillero Oficial Rivulis", layout="wide")

# --- CONFIGURACIÓN DE CONEXIÓN ---
# PEGA AQUÍ LA URL LARGA QUE COPIASTE DE POWER AUTOMATE
URL_POWER_AUTOMATE = "https://default8ecf46185ee64756b55c11a72cc776.8b.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2dd9539e05fb48bda99496fa07c81148/triggers/manual/paths/invoke?api-version=1"

def enviar_a_microsoft(nombre, sector, premio):
    payload = {
        "nombre": nombre,
        "sector": sector,
        "premio": premio
    }
    try:
        # Enviamos los datos a la nube
        requests.post(URL_POWER_AUTOMATE, json=payload, timeout=10)
    except Exception as e:
        st.error(f"Error de conexión con Microsoft 365: {e}")

# --- CARGA DE DATOS ---
def cargar_datos():
    try:
        df = pd.read_excel("Sorteo_Empleados.xlsx")
        df.columns = df.columns.str.strip()
        for col in df.columns:
            if col not in ['Nombre', 'Sector o área']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

def limpiar_texto_premio(nombre_col):
    numeros = re.findall(r'\d+', nombre_col)
    num_txt = f"N° {numeros[0]}" if numeros else ""
    if "Pc" in nombre_col: return f"Computadora - Opción {num_txt}"
    if "Notebook" in nombre_col: return f"Notebook - Opción {num_txt}"
    if "Impresora" in nombre_col: return f"Impresora - Opción {num_txt}"
    if "Mobiliario" in nombre_col: return f"Mobiliario - Opción {num_txt}"
    return nombre_col

# --- INICIALIZACIÓN DE MEMORIA ---
if 'df_bolillero' not in st.session_state:
    st.session_state.df_bolillero = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'agotados' not in st.session_state:
    st.session_state.agotados = []

st.title("🎰 Sistema de Adjudicación Rivulis")
st.markdown("---")

# --- CONTROLES ---
with st.sidebar:
    st.header("⚙️ Administración")
    if st.button("🔄 Sincronizar / Reset", use_container_width=True):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_bolillero = data
            st.session_state.ganadores = []
            st.session_state.agotados = []
            st.success("Sistema Listo.")
    
    st.markdown("---")
    categoria = st.selectbox("Categoría:", ["Pc", "Notebook", "Impresora", "Mobiliario"])
    
    if st.session_state.df_bolillero is not None:
        st.metric("Restantes", len(st.session_state.df_bolillero))

# --- LÓGICA DEL SORTEO ---
if st.session_state.df_bolillero is not None:
    if st.button(f"🚀 SORTEAR {categoria.upper()}", type="primary", use_container_width=True):
        cols_cat = [c for c in st.session_state.df_bolillero.columns if categoria.lower() in c.lower()]
        cols_disp = [c for c in cols_cat if c not in st.session_state.agotados]
        
        if not cols_disp:
            st.error(f"Sin stock de {categoria}")
        else:
            aptos = st.session_state.df_bolillero[(st.session_state.df_bolillero[cols_disp] == 1).any(axis=1)]
            
            if not aptos.empty:
                idx = random.choice(aptos.index)
                fila = aptos.loc[idx]
                col_ganada = next(c for c in cols_disp if fila[c] == 1)
                
                # Formatear datos
                nombre_g = fila.get('Nombre', 'N/N')
                sector_g = fila.get('Sector o área', 'General')
                premio_g = limpiar_texto_premio(col_ganada)
                
                # 1. ANULACIÓN
                st.session_state.agotados.append(col_ganada)
                st.session_state.df_bolillero = st.session_state.df_bolillero.drop(idx)
                
                # 2. REGISTRO LOCAL
                st.session_state.ganadores.insert(0, {"Nombre": nombre_g, "Sector": sector_g, "Premio": premio_g})
                
                # 3. ENVÍO A MICROSOFT POWER AUTOMATE (La R de Registro)
                enviar_a_microsoft(nombre_g, sector_g, premio_g)
                
                st.balloons()
            else:
                st.warning("No hay participantes para las opciones restantes.")

    # --- RESULTADO VISUAL ---
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 15px; border: 2px solid #22c55e; text-align: center;">
                <h1 style="color: #166534;">{g['Nombre']}</h1>
                <h2 style="color: #15803d;">{g['Premio']}</h2>
                <p>Registrado automáticamente en Microsoft 365</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Carga el Excel para empezar.")
