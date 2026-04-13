import streamlit as st
import pandas as pd
import random
import re
import requests

st.set_page_config(page_title="Bolillero Oficial - San Juan", layout="wide")

# --- CONFIGURACIÓN ---
URL_POWER_AUTOMATE = "https://default8ecf46185ee64756b55c11a72cc776.8b.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2dd9539e05fb48bda99496fa07c81148/triggers/manual/paths/invoke?api-version=1"

def enviar_a_microsoft(nombre, sector, premio):
    payload = {"nombre": nombre, "sector": sector, "premio": premio}
    try:
        requests.post(URL_POWER_AUTOMATE, json=payload, timeout=10)
    except:
        pass

def cargar_datos():
    try:
        # Cargamos el archivo (Asegurate que el nombre sea exacto al de GitHub)
        df = pd.read_excel("Sorteo_Empleados.xlsx")
        # Limpiamos nombres de columnas (quita espacios invisibles)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Convertimos las opciones a números 1 o 0
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
    if "pc" in nombre_col.lower(): return f"PC - Opción {num_txt}"
    if "notebook" in nombre_col.lower(): return f"Notebook - Opción {num_txt}"
    if "impresora" in nombre_col.lower(): return f"Impresora - Opción {num_txt}"
    if "mobiliario" in nombre_col.lower(): return f"Mobiliario - Opción {num_txt}"
    return nombre_col

# --- INICIALIZACIÓN ---
if 'df_bolillero' not in st.session_state:
    st.session_state.df_bolillero = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'agotados' not in st.session_state:
    st.session_state.agotados = []

st.title("🎰 Sistema de Adjudicación")

with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("🔄 Cargar / Resetear Excel", use_container_width=True):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_bolillero = data
            st.session_state.ganadores = []
            st.session_state.agotados = []
            st.success("¡Datos cargados!")
    
    st.markdown("---")
    # Este nombre debe coincidir con el inicio de tus columnas en Excel
    categoria = st.selectbox("Categoría a sortear:", ["Pc", "Notebook", "Impresora", "Mobiliario"])

# --- LÓGICA DE SORTEO ---
if st.session_state.df_bolillero is not None:
    if st.button(f"🚀 SORTEAR {categoria.upper()}", type="primary", use_container_width=True):
        
        # BÚSQUEDA FLEXIBLE: Busca columnas que CONTENGAN la palabra de la categoría
        cols_cat = [c for c in st.session_state.df_bolillero.columns if categoria.lower() in c.lower()]
        
        # Filtramos las que ya salieron
        cols_disp = [c for c in cols_cat if c not in st.session_state.agotados]
        
        if not cols_disp:
            st.error(f"No se encontraron columnas disponibles para: {categoria}. Revisá que en el Excel digan '{categoria} - opción...'")
        else:
            # Buscamos participantes con un '1' en las columnas que quedan
            df_actual = st.session_state.df_bolillero
            mask = (df_actual[cols_disp] == 1).any(axis=1)
            aptos = df_actual[mask]
            
            if not aptos.empty:
                idx = random.choice(aptos.index)
                fila = aptos.loc[idx]
                
                # Identificamos qué columna ganó
                col_ganada = next(c for c in cols_disp if fila[c] == 1)
                
                # Datos para enviar
                nom = fila.get('Nombre', 'N/N')
                sec = fila.get('Sector o área', 'General')
                pre = limpiar_texto_premio(col_ganada)
                
                # Registro y Anulación
                st.session_state.agotados.append(col_ganada)
                st.session_state.df_bolillero = st.session_state.df_bolillero.drop(idx)
                st.session_state.ganadores.insert(0, {"Nombre": nom, "Sector": sec, "Premio": pre})
                
                # Envío a Power Automate
                enviar_a_microsoft(nom, sec, pre)
                st.balloons()
            else:
                st.warning(f"No hay más personas que hayan pedido {categoria} entre las opciones que quedan.")

    # Mostrar resultados
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.success(f"🏆 Ganador: {g['Nombre']} - Premio: {g['Premio']}")
        st.table(pd.DataFrame(st.session_state.ganadores))
