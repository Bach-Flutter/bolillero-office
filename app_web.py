import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Bolillero San Juan - Final", layout="wide")

# --- FUNCIONES DE APOYO ---
def cargar_datos():
    try:
        # Forzamos la lectura del archivo que subiste a GitHub
        df = pd.read_excel("Sorteo_Empleados4.xlsx")
        df.columns = df.columns.str.strip()
        # Convertimos todo a números (por si hay celdas vacías o con texto)
        # Esto asegura que el '1' sea detectado siempre
        for col in df.columns:
            if col not in ['Nombre', 'Sector o área']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

def limpiar_texto_premio(nombre_col):
    # Extraer solo el número para mostrarlo bonito
    numeros = re.findall(r'\d+', nombre_col)
    num_txt = f"N° {numeros[0]}" if numeros else ""
    
    if "Pc" in nombre_col: return f"Computadora - Opción {num_txt}"
    if "Notebook" in nombre_col: return f"Notebook - Opción {num_txt}"
    if "Impresora" in nombre_col: return f"Impresora - Opción {num_txt}"
    if "Mobiliario" in nombre_col: return f"Mobiliario - Opción {num_txt}"
    return nombre_col

# --- INICIALIZACIÓN DE MEMORIA (CRITICO) ---
if 'df_bolillero' not in st.session_state:
    st.session_state.df_bolillero = None
if 'lista_ganadores' not in st.session_state:
    st.session_state.lista_ganadores = []
if 'premios_entregados' not in st.session_state:
    st.session_state.premios_entregados = [] # Aquí van las columnas anuladas

st.title("🎰 Bolillero de Adjudicación Directa")
st.markdown("---")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Administración")
    if st.button("🔄 REINICIAR TODO (Cargar Excel)"):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_bolillero = data
            st.session_state.lista_ganadores = []
            st.session_state.premios_entregados = []
            st.success("Datos cargados correctamente.")

    st.markdown("---")
    categoria = st.selectbox("Categoría a sortear ahora:", ["Pc", "Notebook", "Impresora", "Mobiliario"])
    
    if st.session_state.df_bolillero is not None:
        st.metric("Personas disponibles", len(st.session_state.df_bolillero))
        st.write("**Premios ya entregados:**", len(st.session_state.premios_entregados))

# --- LÓGICA DEL SORTEO ---
if st.session_state.df_bolillero is not None:
    
    if st.button(f"🚀 SORTEAR {categoria.upper()}", type="primary", use_container_width=True):
        
        # 1. Identificar columnas de la categoría seleccionada
        todas_las_cols = st.session_state.df_bolillero.columns
        cols_de_categoria = [c for c in todas_las_cols if categoria.lower() in c.lower()]
        
        # 2. FILTRO DE PREMIOS: Quitar las columnas que ya fueron entregadas
        cols_disponibles = [c for c in cols_de_categoria if c not in st.session_state.premios_entregados]
        
        if not cols_disponibles:
            st.error(f"❌ Ya no quedan opciones físicas de {categoria} en el inventario.")
        else:
            # 3. FILTRO DE PERSONAS: Quiénes marcaron '1' en las opciones que QUEDAN
            # Usamos loc para asegurarnos de trabajar sobre los datos actuales
            df_actual = st.session_state.df_bolillero
            participantes_aptos = df_actual[(df_actual[cols_disponibles] == 1).any(axis=1)]
            
            if participantes_aptos.empty:
                st.warning(f"No hay participantes que hayan elegido las opciones de {categoria} que aún están disponibles.")
            else:
                # 4. ELEGIR GANADOR AL AZAR
                indice_ganador = random.choice(participantes_aptos.index)
                fila_ganador = participantes_aptos.loc[indice_ganador]
                
                # 5. DETERMINAR QUÉ OPCIÓN GANÓ (la primera que tenga un 1 de las disponibles)
                opcion_final_col = None
                for c in cols_disponibles:
                    if fila_ganador[c] == 1:
                        opcion_final_col = c
                        break
                
                # 6. EJECUTAR ANULACIONES (Doble seguridad)
                # Anulamos el premio para que no vuelva a salir
                st.session_state.premios_entregados.append(opcion_final_col)
                # Anulamos a la persona (borramos la fila)
                st.session_state.df_bolillero = st.session_state.df_bolillero.drop(indice_ganador)
                
                # 7. REGISTRAR RESULTADO
                resultado = {
                    "Ganador": fila_ganador.get('Nombre', 'N/N'),
                    "Sector": fila_ganador.get('Sector o área', 'General'),
                    "Equipo Adjudicado": limpiar_texto_premio(opcion_final_col)
                }
                st.session_state.lista_ganadores.insert(0, resultado)
                st.balloons()

    # --- MOSTRAR ÚLTIMO RESULTADO ---
    if st.session_state.lista_ganadores:
        res = st.session_state.lista_ganadores[0]
        st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 25px; border-radius: 15px; border: 3px solid #22c55e; text-align: center;">
                <h1 style="color: #166534; margin:0;">{res['Ganador']}</h1>
                <h2 style="color: #15803d; margin:10px 0;">{res['Equipo Adjudicado']}</h2>
                <p style="font-size: 20px;">Sector: {res['Sector']}</p>
                <p style="color: #dc2626; font-weight: bold;">⚠️ PREMIO Y GANADOR RETIRADOS DEL SISTEMA</p>
            </div>
        """, unsafe_allow_html=True)

    # --- HISTORIAL ---
    st.subheader("📜 Acta de Resultados (Historial)")
    if st.session_state.lista_ganadores:
        st.table(pd.DataFrame(st.session_state.lista_ganadores))

else:
    st.warning("👈 Por favor, hacé clic en el botón de la izquierda para cargar los datos del Excel.")
