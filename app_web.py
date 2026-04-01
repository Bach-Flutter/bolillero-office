import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Bolillero Oficial - San Juan", layout="wide")

archivo_excel = "Sorteo_Empleados4.xlsx"

def cargar_datos():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

def limpiar_nombre_opcion(nombre_col):
    # Busca el primer número que aparezca en el título de la columna
    match = re.search(r'\d+', nombre_col)
    if match:
        num = match.group()
        # Detectamos la categoría para ponerla bonita
        for cat in ["Pc", "Notebook", "Impresora", "Mobiliario"]:
            if cat.lower() in nombre_col.lower():
                return f"{cat} - Opción N° {num}"
    return nombre_col

st.title("🎰 Sistema de Adjudicación Final")
st.markdown("---")

# --- ESTADO DE MEMORIA ---
if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'opciones_agotadas' not in st.session_state:
    st.session_state.opciones_agotadas = [] # Lista de columnas ya sorteadas

with st.sidebar:
    st.header("⚙️ Administración")
    if st.button("🔄 Sincronizar Excel y Reset Total"):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.session_state.opciones_agotadas = []
            st.success("Sistema reiniciado.")
    
    st.markdown("---")
    categoria_fija = st.selectbox(
        "Categoría a sortear:",
        ["Pc", "Notebook", "Impresora", "Mobiliario"]
    )
    
    if st.session_state.df_activos is not None:
        st.metric("Restantes en Bolillero", len(st.session_state.df_activos))

# --- LÓGICA DE EXCLUSIÓN ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_fija.upper()}", type="primary", use_container_width=True):
        
        # 1. Identificar columnas de la categoría (ej. todas las de Impresora)
        cols_categoria = [c for c in st.session_state.df_activos.columns if c.lower().startswith(categoria_fija.lower())]
        
        # 2. FILTRAR: Solo columnas que NO hayan salido antes (Stock disponible)
        cols_libres = [c for c in cols_categoria if c not in st.session_state.opciones_agotadas]
        
        if not cols_libres:
            st.error(f"⚠️ Ya no quedan opciones de {categoria_fija} disponibles.")
        else:
            # 3. Filtrar empleados que marcaron '1' en alguna de las columnas libres
            mask = (st.session_state.df_activos[cols_libres] == 1).any(axis=1)
            aptos = st.session_state.df_activos[mask]
            
            if not aptos.empty:
                idx = random.choice(aptos.index)
                fila = aptos.loc[idx]
                
                # 4. Determinar cuál de las columnas libres ganó el usuario (la primera que tenga un 1)
                col_ganada = None
                for c in cols_libres:
                    if fila[c] == 1:
                        col_ganada = c
                        break
                
                # 5. REGISTRO Y ANULACIÓN DOBLE
                # A) Anulamos la opción de equipo para siempre
                st.session_state.opciones_agotadas.append(col_ganada)
                
                # B) Anulamos a la persona del bolillero general
                st.session_state.df_activos = st.session_state.df_activos.drop(idx)
                
                # C) Guardamos en el acta
                st.session_state.ganadores.insert(0, {
                    'Nombre': fila.get('Nombre', 'N/N'),
                    'Sector': fila.get('Sector o área', 'General'),
                    'Premio': limpiar_nombre_opcion(col_ganada)
                })
                st.balloons()
            else:
                st.warning(f"No hay más interesados en las opciones de {categoria_fija} que quedan en stock.")

    # --- RESULTADOS ---
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center;">
                <h3 style="color: #ef4444; margin:0;">🏆 ADJUDICACIÓN ÚNICA</h3>
                <h1 style="font-size: 50px; margin:10px 0;">{g['Nombre']}</h1>
                <p style="font-size: 20px;"><b>{g['Sector']}</b> | <b>{g['Premio']}</b></p>
                <p style="color: #666; font-size: 14px;">(Esta opción ha sido retirada del inventario)</p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 Acta de Adjudicaciones (Sin repetición de equipos)")
    if st.session_state.ganadores:
        st.dataframe(pd.DataFrame(st.session_state.ganadores), use_container_width=True)
else:
    st.warning("Carga el archivo Excel para comenzar.")
