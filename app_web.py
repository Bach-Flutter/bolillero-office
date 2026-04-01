import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Bolillero con Inventario - San Juan", layout="wide")

archivo_excel = "Sorteo_Empleados4.xlsx"

def cargar_datos():
    try:
        df = pd.read_excel(archivo_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return None

st.title("🎰 Sistema de Adjudicación con Control de Stock")
st.caption("Regla: Si una opción (ej: PC - Opción 1) ya salió, queda anulada para el resto de los participantes.")

# --- MEMORIA DEL SISTEMA ---
if 'df_activos' not in st.session_state:
    st.session_state.df_activos = None
if 'ganadores' not in st.session_state:
    st.session_state.ganadores = []
if 'stock_anulado' not in st.session_state:
    st.session_state.stock_anulado = [] # Aquí guardamos los premios que ya salieron

with st.sidebar:
    st.header("⚙️ Configuración")
    if st.button("📥 Sincronizar Excel y Reset Stock"):
        data = cargar_datos()
        if data is not None:
            st.session_state.df_activos = data
            st.session_state.ganadores = []
            st.session_state.stock_anulado = []
            st.success("Inventario y Lista reseteados.")
    
    st.markdown("---")
    categoria_padre = st.selectbox(
        "Categoría a sortear:",
        ["Pc", "Notebook", "Impresora", "Mobiliario"]
    )
    
    if st.session_state.stock_anulado:
        st.subheader("🚫 Premios Agotados:")
        for item in st.session_state.stock_anulado:
            st.write(f"- {item}")

# --- LÓGICA DE SORTEO CON FILTRO DE STOCK ---
if st.session_state.df_activos is not None and not st.session_state.df_activos.empty:
    
    if st.button(f"✨ SORTEAR {categoria_padre.upper()}", type="primary", use_container_width=True):
        
        # 1. Identificar columnas de la categoría
        cols_cat = [c for c in st.session_state.df_activos.columns if categoria_padre.lower() in c.lower()]
        
        # 2. Filtrar columnas que NO estén en la lista de stock_anulado
        cols_disponibles = [c for c in cols_cat if c not in st.session_state.stock_anulado]
        
        if not cols_disponibles:
            st.error(f"⚠️ ¡Atención! Ya no quedan opciones disponibles para {categoria_padre}.")
        else:
            # 3. Buscar participantes que marcaron alguna de las OPCIONES DISPONIBLES
            mask = (st.session_state.df_activos[cols_disponibles] == 1).any(axis=1)
            participantes_aptos = st.session_state.df_activos[mask]
            
            if not participantes_aptos.empty:
                indice_ganador = random.choice(participantes_aptos.index)
                fila = participantes_aptos.loc[indice_ganador]
                
                # 4. Determinar qué opción disponible ganó el empleado
                opcion_final = None
                for col in cols_disponibles:
                    if fila[col] == 1:
                        opcion_final = col
                        break
                
                # 5. REGISTRAR Y ANULAR
                st.session_state.ganadores.insert(0, {
                    'Nombre': fila.get('Nombre', 'N/N'),
                    'Sector': fila.get('Sector o área', 'General'),
                    'Premio': opcion_final
                })
                
                # ANULAMOS LA OPCIÓN (Ya no hay más de este equipo)
                st.session_state.stock_anulado.append(opcion_final)
                
                # ANULAMOS LA FILA (El empleado ya ganó, se va)
                st.session_state.df_activos = st.session_state.df_activos.drop(indice_ganador)
                
                st.balloons()
            else:
                st.warning(f"No hay participantes que califiquen para las opciones de {categoria_padre} que aún quedan.")

    # --- RESULTADOS ---
    if st.session_state.ganadores:
        g = st.session_state.ganadores[0]
        st.markdown(f"""
            <div style="background-color: #fff4f4; padding: 20px; border-radius: 15px; border: 2px solid #dc2626; text-align: center;">
                <h3 style="color: #dc2626; margin:0;">🏆 ADJUDICACIÓN EXITOSA</h3>
                <h1 style="font-size: 45px; margin:10px 0;">{g['Nombre']}</h1>
                <p style="font-size: 20px;"><b>Sector:</b> {g['Sector']} | <b>Equipo:</b> {g['Premio']}</p>
                <p style="color: #666; font-style: italic;">* Esta opción de equipo ha sido retirada del inventario.</p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 Acta de Entrega (Premios Únicos)")
    if st.session_state.ganadores:
        st.table(pd.DataFrame(st.session_state.ganadores))
else:
    st.warning("Carga el Excel desde el panel lateral.")
