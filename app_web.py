import streamlit as st
import pandas as pd
import random
import re
import io

st.set_page_config(page_title="Bolillero de Adjudicación Oficial", layout="wide")

archivo_excel = "Listado_ Definitivo_Sorteo_Empleados.xlsx"

def cargar_datos():
    try:
        # Leemos el excel
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

def formatear_nombre_premio(nombre_columna):
    """
    Mantiene el nombre de la columna tal cual está en el Excel 
    para diferenciar entre PC-1, PC-2, etc.
    """
    return nombre_columna

st.title("🎰 Sistema de Adjudicación de Equipos y Mobiliarios")
st.markdown("---")

# --- MEMORIA DEL SISTEMA ---
if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'premios_agotados' not in st.session_state:
    st.session_state.premios_agotados = []

with st.sidebar:
    st.header("⚙️ Panel")
    if st.button("📥 Cargar Excel o Resetear"):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.session_state.premios_agotados = []
            st.success("Sistema reiniciado con éxito.")
    
    st.markdown("---")
    # Selector de Categoría
    categoria_padre = st.selectbox(
        "Seleccione categoría a sortear:",
        ["Pc", "Notebook", "Impresora", "Mobiliario"]
    )
    
    if st.session_state.df_activos is not None:
        st.metric("Personas en bolillero", len(st.session_state.df_activos))
    
    if st.session_state.premios_agotados:
        st.subheader("🚫 Opciones Agotadas:")
        for p in st.session_state.premios_agotados:
            st.write(f"• {p}")

    # --- BOTÓN DE DESCARGA ---
    if st.session_state.ganadores:
        st.markdown("---")
        df_final = pd.DataFrame(st.session_state.ganadores)
        # Ordenamos por nombre para que el Excel sea prolijo
        df_final = df_final.sort_values(by='Nombre')
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Ganadores')
        
        st.download_button(
            label="💾 Descargar Acta (Excel)",
            data=output.getvalue(),
            file_name="Acta_Final_Sorteo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- LÓGICA DE SORTEO ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_padre.upper()}", type="primary", use_container_width=True):
        
        # 1. Filtrar columnas por categoría (Ej: Todas las que empiezan con "Pc")
        cols_exactas = [c for c in st.session_state.df_activos.columns if c.lower().startswith(categoria_padre.lower())]
        
        # 2. Quitar las que ya salieron
        cols_disponibles = [c for c in cols_exactas if c not in st.session_state.premios_agotados]
        
        if not cols_disponibles:
            st.error(f"No quedan más opciones disponibles para {categoria_padre}.")
        else:
            # 3. Buscar quiénes marcaron '1' en las opciones disponibles
            mask = (st.session_state.df_activos[cols_disponibles] == 1).any(axis=1)
            aptos = st.session_state.df_activos[mask]
            
            if not aptos.empty:
                idx = random.choice(aptos.index)
                fila = aptos.loc[idx]
                
                # 4. Ver qué opción específica ganó (la primera que tenga un 1)
                col_ganadora_original = None
                for col in cols_disponibles:
                    if fila[col] == 1:
                        col_ganadora_original = col
                        break
                
                # 5. Registro del ganador
                st.session_state.ganadores.insert(0, {
                    'Nombre': fila.get('Nombre', 'N/N'),
                    'Sector o área': fila.get('Sector o área', 'General'),
                    'Premio Adjudicado': col_ganadora_original
                })
                
                # 6. Eliminar el premio y al ganador de la tómbola
                st.session_state.premios_agotados.append(col_ganadora_original)
                st.session_state.df_activos = st.session_state.df_activos.drop(idx)
                st.balloons()
            else:
                st.warning(f"Ningún participante restante ha solicitado {categoria_padre}.")

    # --- VISUALIZACIÓN DEL ÚLTIMO GANADOR ---
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 25px; border-radius: 20px; border: 2px solid #0078d4; text-align: center;">
                <h2 style="color: #0078d4; margin:0;">🎊 ADJUDICACIÓN CONFIRMADA 🎊</h2>
                <h1 style="font-size: 55px; margin:15px 0; color: #1e293b;">{g['Nombre']}</h1>
                <p style="font-size: 22px;"><b>Área:</b> {g['Sector o área']} | <b>Equipo:</b> <span style="color: #e11d48;">{g['Premio Adjudicado']}</span></p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 Acta de Ganadores")
    if st.session_state.ganadores:
        st.dataframe(pd.DataFrame(st.session_state.ganadores), use_container_width=True)
else:
    st.info("Carga el archivo Excel desde el panel lateral para comenzar.")
