import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Calculadora 3D Pro Chile", layout="wide", page_icon="⚙️")

# Estilo personalizado para mejorar la interfaz
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Calculadora 3D Pro (CLP / USD)")
st.subheader("Control de costos, margen de utilidad y registro histórico")

# --- Inicializar base de datos en la sesión ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        "Fecha", "Proyecto", "Costo Material", "Costo Energía", 
        "Depreciación", "Mano Obra", "Extras", "Descripción Extras",
        "Costo Total CLP", "Costo Total USD", "Precio Venta CLP"
    ])

# --- Sidebar: Configuración General ---
with st.sidebar:
    st.header("⚙️ Configuración Base")
    tasa_dolar = st.number_input("Valor Dólar hoy (CLP)", value=950, step=1)
    valor_kwh = st.number_input("Costo kWh Chile (CLP)", value=150, help="Revisa tu boleta de Enel o CGE")
    margen_ganancia = st.slider("Margen de Utilidad (%)", 0, 300, 100, help="Porcentaje de ganancia sobre el costo total")
    st.info("Nota: Los cálculos de energía y depreciación se basan en el tiempo real de uso.")

# --- Formulario de Entrada ---
with st.form("calculadora_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📦 Material y Tiempo")
        nombre_proyecto = st.text_input("Nombre del Trabajo", placeholder="Ej: Engranaje Prototipo")
        precio_bobina = st.number_input("Precio Bobina 1kg (CLP)", value=22000, step=500)
        gramos_usados = st.number_input("Gramos usados (según Slicer)", value=0.0, step=1.0)
        tiempo_horas = st.number_input("Horas de impresión", value=0.0, step=0.1)

    with col2:
        st.markdown("### 🛠️ Máquina y Diseño")
        watts_maquina = st.number_input("Consumo Máquina (Watts)", value=120, step=5)
        precio_maquina = st.number_input("Precio Compra Máquina (CLP)", value=350000, step=1000)
        vida_util = st.number_input("Vida Útil Máquina (Horas)", value=5000, step=500)
        obra_mano_diseno = st.number_input("Mano de Obra / Diseño (CLP)", value=0, step=1000)

    with col3:
        st.markdown("### ➕ Costos Extras")
        costo_extra = st.number_input("Monto Extra (CLP)", value=0, step=100)
        desc_extra = st.text_input("Descripción del extra", placeholder="Ej: Caja de envío, Lijas, Pintura...")
        st.caption("Usa este campo para imprevistos o post-procesado.")

    btn_calcular = st.form_submit_button("Calcular y Guardar en Registro")

# --- Lógica Matemática ---
# 1. Filamento
valor_gramo = precio_bobina / 1000
costo_material_total = valor_gramo * gramos_usados

# 2. Energía
valor_hora_kw = (watts_maquina / 1000) * valor_kwh
costo_energia_total = valor_hora_kw * tiempo_horas

# 3. Depreciación
valor_depreciacion_hora = precio_maquina / vida_util
costo_depreciacion_total = valor_depreciacion_hora * tiempo_horas

# 4. Totales
costo_total_clp = costo_material_total + costo_energia_total + costo_depreciacion_total + obra_mano_diseno + costo_extra
precio_venta_clp = costo_total_clp * (1 + margen_ganancia/100)
costo_total_usd = costo_total_clp / tasa_dolar

# --- Mostrar Resultados ---
if btn_calcular:
    if not nombre_proyecto:
        st.error("⚠️ Debes asignar un nombre al proyecto.")
    else:
        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("PRECIO VENTA (CLP)", f"${precio_venta_clp:,.0f}")
        m2.metric("COSTO TOTAL (CLP)", f"${costo_total_clp:,.0f}")
        m3.metric("COSTO TOTAL (USD)", f"${costo_total_usd:,.2f}")

        # Desglose detallado
        with st.expander("Ver desglose de costos detallado"):
            d1, d2 = st.columns(2)
            d1.write(f"**Filamento ({gramos_usados}g):** ${costo_material_total:,.0f}")
            d1.write(f"**Energía ({tiempo_horas}h):** ${costo_energia_total:,.0f}")
            d1.write(f"**Depreciación máquina:** ${costo_depreciacion_total:,.0f}")
            d2.write(f"**Mano de obra:** ${obra_mano_diseno:,.0f}")
            d2.write(f"**Extras ({desc_extra}):** ${costo_extra:,.0f}")
            d2.write(f"**Costo por gramo:** ${valor_gramo:,.2f}")

        # Guardar en el historial
        nuevo = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Proyecto": nombre_proyecto,
            "Costo Material": round(costo_material_total, 2),
            "Costo Energía": round(costo_energia_total, 2),
            "Depreciación": round(costo_depreciacion_total, 2),
            "Mano Obra": obra_mano_diseno,
            "Extras": costo_extra,
            "Descripción Extras": desc_extra,
            "Costo Total CLP": round(costo_total_clp, 0),
            "Costo Total USD": round(costo_total_usd, 2),
            "Precio Venta CLP": round(precio_venta_clp, 0)
        }
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([nuevo])], ignore_index=True)
        st.success("✅ Datos guardados en el registro.")

# --- Historial y Exportación ---
st.divider()
st.subheader("📋 Historial de Registros")

if not st.session_state.historico.empty:
    # Mostrar tabla
    st.dataframe(st.session_state.historico, use_container_width=True)
    
    # Preparar descarga
    csv = st.session_state.historico.to_csv(index=False).encode('utf-8-sig')
    
    st.download_button(
        label="📥 Descargar todo el historial (Excel / CSV)",
        data=csv,
        file_name=f"registros_3d_chile_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    if st.button("Limpiar Historial"):
        st.session_state.historico = pd.DataFrame(columns=st.session_state.historico.columns)
        st.rerun()
else:
    st.info("Aún no hay cálculos registrados.")
