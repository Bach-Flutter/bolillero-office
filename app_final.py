import streamlit as st
import pandas as pd
import random
import re
import requests

st.set_page_config(page_title="Bolillero Final - Rivulis", layout="wide")

# --- CONFIGURACIÓN ---
URL_POWER_AUTOMATE = "https://default8ecf46185ee64756b55c11a72cc776.8b.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2dd9539e05fb48bda99496fa07c81148/triggers/manual/paths/invoke?api-version=1"

def enviar_a_microsoft(nombre, sector, premio):
    payload = {"nombre": nombre, "sector": sector, "premio": premio}
    try:
        requests.post(URL_POWER_AUTOMATE, json=payload, timeout=5)
    except:
        pass

def cargar_datos():
    try:
        # 1. Leer el archivo
        df = pd.read_excel("Sorteo_Empleados.xlsx")
        # 2. Limpiar nombres de columnas: quitamos espacios y pasamos a minúsculas para comparar
        df.columns = [str(c).strip() for c in df.columns]
        
        # 3. Asegurar que los datos de opciones sean números
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
    return f"{nombre_col.split('-')[0].strip()} - Opción {num_txt}"

# --- MEMORIA ---
if 'df_bolillero' not in st.session_state:
    st.session_state.df_bolillero = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'agotados' not in st.session_state:
    st.session_state.agotados = []

st.title("🎰 Sistema de Adjudicación")

with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("🔄 CARGAR EXCEL", use_container_width=True):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_bolillero = data
            st.session_state.ganadores = []
            st.session_state.agotados = []
            st.success("¡Datos cargados!")

    st.markdown("---")
    categoria = st.selectbox("Elegí qué sortear:", ["Pc", "Notebook", "Impresora", "Mobiliario"])

# --- LÓGICA ---
if st.session_state.df_bolillero is not None:
    # --- AYUDA VISUAL (Solo para vos mientras probás) ---
    all_cols = st.session_state.df_bolillero.columns.tolist()
    
    if st.button(f"🚀 SORTEAR {categoria.upper()}", type="primary", use_container_width=True):
        
        # BUSQUEDA ULTRA-FLEXIBLE: 
        # Buscamos cualquier columna que tenga la palabra (ej: 'pc') dentro de su nombre
        cols_encontradas = [c for c in all_cols if categoria.lower() in c.lower()]
        
        # Quitamos las que ya salieron
        cols_disp = [c for c in cols_encontradas if c not in st.session_state.agotados]
        
        if not cols_disp:
            st.error(f"No hay stock para '{categoria}'.")
            with st.expander("Ver por qué (Columnas detectadas)"):
                st.write("El sistema buscó la palabra:", categoria.lower())
                st.write("Columnas disponibles en tu Excel:", all_cols)
        else:
            df_actual = st.session_state.df_bolillero
            # Buscamos a los que marcaron con 1 alguna de esas columnas
            aptos = df_actual[(df_actual[cols_disp] == 1).any(axis=1)]
            
            if not aptos.empty:
                idx = random.choice(aptos.index)
                fila = aptos.loc[idx]
                
                # Cuál de las opciones ganó
                col_ganada = next(c for c in cols_disp if fila[c] == 1)
                
                nom = fila.get('Nombre', 'N/N')
                sec = fila.get('Sector o área', 'General')
                pre = limpiar_texto_premio(col_ganada)
                
                # Actualizar estados
                st.session_state.agotados.append(col_ganada)
                st.session_state.df_bolillero = st.session_state.df_bolillero.drop(idx)
                st.session_state.ganadores.insert(0, {"Nombre": nom, "Sector": sec, "Premio": pre})
                
                # Enviar a Microsoft
                enviar_a_microsoft(nom, sec, pre)
                st.balloons()
            else:
                st.warning(f"Ningún participante restante ha solicitado {categoria}.")

    if st.session_state.ganadores:
        st.subheader("Último Ganador:")
        g = st.session_state.ganadores[0]
        st.info(f"🎉 {g['Nombre']} - {g['Premio']}")
        st.dataframe(pd.DataFrame(st.session_state.ganadores))
