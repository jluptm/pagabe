import os
import pandas as pd
import streamlit as st
import datetime
import altair as alt

# -------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Informe Financiero: GABE - Barnabas Aid",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (AESTHETIC DE ALTO NIVEL)
# -------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.9);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 25px;
    }
    
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border-left: 5px solid #2a5298;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 15px;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 5px;
        margin-bottom: 0;
    }

    .kpi-subvalue {
        font-size: 0.8rem;
        margin-top: 4px;
        color: #94a3b8;
    }
    
    /* Separadores decorativos */
    .decor-line {
        height: 4px;
        width: 60px;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 2px;
        margin-bottom: 20px;
    }
    
    .intro-container {
        background: rgba(255, 255, 255, 0.9);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 25px;
        color: #334155;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# INICIALIZACIÓN DE ESTADOS DE SESIÓN (ESTADO DEL DIALOG)
# -------------------------------------------------------------------
if 'active_dialog_concept' not in st.session_state:
    st.session_state.active_dialog_concept = None

if 'active_dialog_concept_neg' not in st.session_state:
    st.session_state.active_dialog_concept_neg = None

@st.dialog("Detalle de Operaciones")
def show_details_dialog(concepto, df_concept):
    st.markdown(f"### Operaciones de **{concepto}**")
    st.write(f"Total: **{len(df_concept)}** transacciones de ingresos.")
    
    df_display_dialog = df_concept.copy()
    
    desc_col = 'Descripción' if 'Descripción' in df_display_dialog.columns else ('Descripcion' if 'Descripcion' in df_display_dialog.columns else None)
    
    # Seleccionar solo las columnas solicitadas
    keep_cols = []
    if 'Fecha' in df_display_dialog.columns:
        keep_cols.append('Fecha')
    if desc_col:
        keep_cols.append(desc_col)
    if 'Detalle' in df_display_dialog.columns:
        keep_cols.append('Detalle')
    if 'en $' in df_display_dialog.columns:
        keep_cols.append('en $')
        
    df_display_dialog = df_display_dialog[keep_cols]
    
    # Cortar la columna Descripción a 20 caracteres
    if desc_col:
        df_display_dialog[desc_col] = df_display_dialog[desc_col].astype(str).str.slice(0, 20)
        
    if 'Fecha' in df_display_dialog.columns:
        df_display_dialog['Fecha'] = df_display_dialog['Fecha'].apply(lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) and hasattr(x, 'strftime') else str(x))

    # Estilo de alto contraste (Verde para ingresos)
    def style_green(row):
        return ['background-color: #d1e7dd; color: #000000; font-weight: bold; border-bottom: 1px solid #b7d1c4;'] * len(row)
        
    styler_dialog = df_display_dialog.style.apply(style_green, axis=1)
    
    if 'en $' in df_display_dialog.columns:
        styler_dialog = styler_dialog.format({'en $': lambda x: f"{x:,.2f}" if (pd.notna(x) and isinstance(x, (int, float))) else ""})
        
    st.dataframe(styler_dialog, use_container_width=True, hide_index=True)
    st.caption("Nota: Haz clic fuera del popup o en la 'X' superior para cerrar.")


@st.dialog("Detalle de Egresos")
def show_details_dialog_neg(concepto, df_concept):
    st.markdown(f"### Egresos de **{concepto}**")
    st.write(f"Total: **{len(df_concept)}** transacciones de egresos.")
    
    df_display_dialog = df_concept.copy()
    
    desc_col = 'Descripción' if 'Descripción' in df_display_dialog.columns else ('Descripcion' if 'Descripcion' in df_display_dialog.columns else None)
    
    # Seleccionar solo las columnas solicitadas
    keep_cols = []
    if 'Fecha' in df_display_dialog.columns:
        keep_cols.append('Fecha')
    if desc_col:
        keep_cols.append(desc_col)
    if 'Detalle' in df_display_dialog.columns:
        keep_cols.append('Detalle')
    if 'en $' in df_display_dialog.columns:
        keep_cols.append('en $')
        
    df_display_dialog = df_display_dialog[keep_cols]
    
    # Cortar la columna Descripción a 20 caracteres
    if desc_col:
        df_display_dialog[desc_col] = df_display_dialog[desc_col].astype(str).str.slice(0, 20)
        
    if 'Fecha' in df_display_dialog.columns:
        df_display_dialog['Fecha'] = df_display_dialog['Fecha'].apply(lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) and hasattr(x, 'strftime') else str(x))

    # Estilo de alto contraste (Rojo para egresos)
    def style_red(row):
        return ['background-color: #f8d7da; color: #000000; font-weight: bold; border-bottom: 1px solid #f5c2c7;'] * len(row)
        
    styler_dialog = df_display_dialog.style.apply(style_red, axis=1)
    
    if 'en $' in df_display_dialog.columns:
        styler_dialog = styler_dialog.format({'en $': lambda x: f"{x:,.2f}" if (pd.notna(x) and isinstance(x, (int, float))) else ""})
        
    st.dataframe(styler_dialog, use_container_width=True, hide_index=True)
    st.caption("Nota: Haz clic fuera del popup o en la 'X' superior para cerrar.")


# -------------------------------------------------------------------
# CARGA Y LIMPIEZA DE DATOS
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "gabe", "GabeEF.xlsx")
SELECTED_SHEET = "Hoja 2"

def clean_spanish_number(series):
    """Limpia números con formato español (separador de miles '.' y decimal ',')"""
    s = series.astype(str).str.strip()
    s = s.replace(['nan', 'None', '<NA>', ''], '0')
    s = s.str.replace('.', '', regex=False)
    s = s.str.replace(',', '.', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0.0)

# -------------------------------------------------------------------
# CLASIFICACIÓN GLOBAL DE INGRESOS
# -------------------------------------------------------------------
def create_label_global(row, det_col, desc_col):
    """Clasifica una transacción de ingreso basándose en su detalle y descripción"""
    det = str(row.get(det_col) or "").strip() if det_col else ""
    desc = str(row.get(desc_col) or "").strip() if desc_col else ""
    label = det[:50] if (det and det.lower() not in ['nan', 'none', '']) else desc[:50]
    
    lbl_lower = label.lower()
    det_lower = det.lower()
    desc_lower = desc.lower()
    
    # Agrupar Gabriel
    if "gabriel" in lbl_lower:
        return "Gabriel"
        
    # Agrupar Sierra y las etiquetas específicas solicitadas
    if ("sierra" in lbl_lower or
        "gabe-prestamo" in lbl_lower or "gabe-prestamo" in det_lower or "gabe-prestamo" in desc_lower or
        "ingreso : 50 gabe" in lbl_lower or "ingreso : 50 gabe" in det_lower or "ingreso : 50 gabe" in desc_lower or
        "horeb" in lbl_lower or "horeb" in det_lower or "horeb" in desc_lower or
        "joel" in lbl_lower or "joel" in det_lower or "joel" in desc_lower or
        "gabe(100)" in lbl_lower or "gabe(100)" in det_lower or "gabe(100)" in desc_lower or
        "gabe-200" in lbl_lower or "gabe-200" in det_lower or "gabe-200" in desc_lower or
        "pmis-cierre" in lbl_lower or "pmis-cierre" in det_lower or "pmis-cierre" in desc_lower):
        return "Sierra"
        
    # Agrupar Betty / Betty Anselmi
    if "betty" in lbl_lower:
        return "Betty Anselmi"
        
    # Agrupar Tomas Manrique
    if "tomas" in lbl_lower or "tomás" in lbl_lower:
        return "Tomas Manrique"
        
    # Agrupar Carlos Niño
    if "niño" in lbl_lower or "nino" in lbl_lower:
        return "Carlos Niño"
        
    # Agrupar Josue Lobo
    if "lobo" in lbl_lower or "lobo" in det_lower or "lobo" in desc_lower:
        return "Josue Lobo"
        
    # Agrupar CarmenJulia
    if "ingreso-gabe-car" in lbl_lower or "ingreso-gabe-car" in det_lower or "ingreso-gabe-car" in desc_lower:
        return "CarmenJulia"
        
    # Agrupar Moriah-Elioenay
    if ("moriah" in lbl_lower or "moriah" in det_lower or "moriah" in desc_lower or
        "elioenay" in lbl_lower or "elioenay" in det_lower or "elioenay" in desc_lower or
        "gabe-ingreso-eli" in lbl_lower or "gabe-ingreso-eli" in det_lower or "gabe-ingreso-eli" in desc_lower):
        return "Moriah-Elioenay"
        
    # Agrupar Rafael Gonzalez
    if "rafael" in lbl_lower or "rafael" in det_lower or "rafael" in desc_lower:
        return "Rafael Gonzalez"
        
    # Agrupar El Shaddai
    if "gabe-ingreso-idl" in lbl_lower or "gabe-ingreso-idl" in det_lower or "gabe-ingreso-idl" in desc_lower or "idl" in lbl_lower or "idl" in det_lower or "idl" in desc_lower:
        return "El Shaddai"
        
    # Agrupar Gabe y ? o GABE-3$ -> ingreso desconocido
    if (("gabe" in lbl_lower and "?" in lbl_lower) or 
        ("gabe" in det_lower and "?" in det_lower) or 
        ("gabe" in desc_lower and "?" in desc_lower) or
        "gabe-3$" in lbl_lower or "gabe-3$" in det_lower or "gabe-3$" in desc_lower):
        return "ingreso desconocido"
        
    return label

# -------------------------------------------------------------------
# CLASIFICACIÓN GLOBAL DE EGRESOS
# -------------------------------------------------------------------
def classify_expense_global(row, det_col, desc_col):
    """Clasifica una transacción de egreso basándose en su detalle y descripción"""
    det = str(row.get(det_col) or "").strip() if det_col else ""
    desc = str(row.get(desc_col) or "").strip() if desc_col else ""
    label = det[:50] if (det and det.lower() not in ['nan', 'none', '']) else desc[:50]
    
    lbl_lower = label.lower()
    
    # Manu
    if "manu" in lbl_lower:
        return "Manu"
    # Roger
    if "roger" in lbl_lower:
        return "Roger"
    # VR or VictoR
    if "vr" in lbl_lower or "victor" in lbl_lower:
        return "VictoR"
    # Aceite
    if "aceite" in lbl_lower:
        return "Aceite"
    # Gasolina
    if "gasolina" in lbl_lower:
        return "Gasolina"
    # Juan
    if "juan" in lbl_lower:
        return "Juan"
    # Ronald
    if "ronald" in lbl_lower:
        return "Ronald"
    # Taxi
    if "taxi" in lbl_lower:
        return "Taxi"
    # Transporte (sin contener Manu o Roger, lo cual ya se garantiza al estar evaluado después)
    if "transporte" in lbl_lower:
        return "Transporte"
        
    return label


@st.cache_data(ttl=120)
def load_sheet_data(file_path, sheet_name):
    """Carga una hoja específica y aplica limpieza básica si es necesario"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Limpieza estándar si son las columnas financieras típicas
        if 'MontoBs' in df.columns:
            df['MontoBs_clean'] = clean_spanish_number(df['MontoBs'])
        if 'SaldoBs' in df.columns:
            df['SaldoBs_clean'] = clean_spanish_number(df['SaldoBs'])
        
        # Convertir Fecha a datetime si existe
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error al cargar la hoja '{sheet_name}': {e}")
        return pd.DataFrame()

# Verificar existencia del archivo
if not os.path.exists(EXCEL_PATH):
    st.error(f"⚠️ No se encontró el archivo Excel en la ruta: {EXCEL_PATH}")
    st.info("Por favor, asegúrese de que el archivo 'GabeEF.xlsx' existe dentro de la carpeta 'gabe'.")
    st.stop()

# Cargar datos de la "Hoja 2"
df_raw = load_sheet_data(EXCEL_PATH, SELECTED_SHEET)
df_filtered = df_raw.copy()

# Verificar si tiene las columnas típicas de transacciones
has_financial_cols = all(col in df_raw.columns for col in ['Fecha', 'Descripción', 'MontoBs', 'en $'])

# -------------------------------------------------------------------
# CABECERA DEL DASHBOARD
# -------------------------------------------------------------------
st.markdown(
    f"""
    <div class="header-container">
        <h1 class="main-title">Informe Financiero: GABE - Barnabas Aid</h1>
        <div class="decor-line"></div>
    </div>
    """, 
    unsafe_allow_html=True
)

# -------------------------------------------------------------------
# INTRODUCCIÓN Y CONTEXTO DEL REPORTE
# -------------------------------------------------------------------
with st.expander("📝 1. Introducción y Gestión Inicial de Fondos", expanded=True):
    st.markdown("""
<div class="intro-container">
<p>El presente reporte detalla el uso y la administración de los recursos otorgados por <strong>Barnabas Aid</strong> para el desarrollo operativo de la Granja Alas de Bendición y Esperanza (GABE).</p>
<p>Antes de la recepción formal de estos fondos, la granja ya se encontraba en funcionamiento. Para mantener la continuidad operativa, fue necesario utilizar temporalmente recursos en calidad de préstamo provenientes de otros proyectos de la organización, bajo el compromiso de restituirlos una vez se recibiera el financiamiento de Barnabas Aid.</p>
<p>Por lo tanto, tras recibir el desembolso inicial:</p>
<ul style="margin-bottom: 20px;">
<li><strong>USD 5,000</strong> se destinaron de inmediato a saldar dicho financiamiento puente.</li>
<li><strong>USD 10,000</strong> quedaron disponibles netos para la ejecución directa de las operaciones de la granja (tal como se ilustra en la primera imagen adjunta).</li>
</ul>
</div>
""", unsafe_allow_html=True)
    st.image(os.path.join("assets", "cheques.jpg"), caption="Cheques y Soporte Financiero Inicial - Barnabas Aid", use_container_width=True)

with st.expander("💱 2. Contexto Económico y Estrategia de Manejo Cambiario", expanded=False):
    st.markdown("""
<div class="intro-container">
<p>Operar en la economía venezolana representa un desafío financiero complejo. Aunque la mayoría de los bienes y servicios se pagan en Bolívares (VES), sus precios de referencia están anclados al Dólar (USD). La fluctuación diaria de la tasa de cambio genera una dinámica inflacionaria que dificulta la planificación financiera.</p>
<p>A esto se suma la coexistencia de múltiples tipos de cambio en el mercado nacional:</p>
<ol style="margin-bottom: 20px;">
<li><strong>Tasa Oficial (BCV)</strong>: Regulada por el Banco Central de Venezuela.</li>
<li><strong>Tasa Euro</strong>: Utilizada en ciertos sectores comerciales.</li>
<li><strong>Tasa Binance (P2P)</strong>: Generalmente la más alta del mercado y de carácter variable.</li>
</ol>
<p>En este contexto, obtener divisas en efectivo a tasas razonables para la operación regular de una granja avícola es prácticamente imposible, ya que el efectivo suele transarse bajo la tasa Binance, más orientada a la especulación.</p>

<h3 style="color: #2a5298; font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 600; margin-top: 15px;">Mecanismo de Ejecución Financiera</h3>
<p>Para mitigar estos riesgos y optimizar los recursos, se optó por movilizar los fondos desde una cuenta en USD bajo demanda, empleando dos metodologías de pago de acuerdo a la necesidad:</p>
<ul style="margin-bottom: 20px;">
<li><strong>Pagos Directos</strong>: Transferencias directas a proveedores de bienes y servicios mediante la plataforma Zelle.</li>
<li><strong>Conversión a Bolívares</strong>: Para los gastos locales que requerían moneda nacional, los fondos en USD se enviaban vía Zelle a dos operadores cambiarios de total confianza (identificados como Gabriel y Sierra). Estos operadores convertían las divisas a la tasa del día y transferían los Bolívares a la cuenta matriz de la Granja en el Banco Provincial. Se seleccionaron dos operadores para garantizar la disponibilidad inmediata de fondos y asegurar la continuidad operativa.</li>
</ul>
<p style="background-color: #f8fafc; padding: 12px; border-left: 4px solid #3b82f6; border-radius: 4px; font-style: italic; margin-top: 15px;">
<strong>Nota aclaratoria:</strong> Aunque este procedimiento administrativo pueda parecer complejo, demostró ser la vía más rápida, eficiente y segura para ejecutar los fondos dadas las restricciones del entorno económico venezolano.
</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 3. Estructura del Reporte Adjunto", expanded=False):
    st.markdown("""
<div class="intro-container">
<p>A continuación, el informe se desglosa en las siguientes secciones para su revisión:</p>
<ul>
<li><strong>Sección 1</strong>: Registro detallado de todas las transacciones de compra directa realizadas a proveedores vía Zelle.</li>
<li><strong>Sección 2</strong>: Gráficos financieros que muestran el flujo, manejo y destino de los fondos ejecutados en Bolívares desde la cuenta del Banco Provincial.</li>
<li><strong>Sección 3</strong>: Data administrativa completa en Bolívares, organizada en tres formatos para facilitar su análisis: Tabla general, Vista de Calendario y Cronograma de ejecución.</li>
</ul>
</div>
""", unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Enlace provisional de YouTube

with st.expander("💳 Sección 1: Transacciones de compra directa de bienes y servicios via Zelle", expanded=False):
    # Definir datos
    zelle_data = [
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "05-12-2025", "Monto USD": 560.00, "Descripción": "Compra directa", "Imagen_Path": os.path.join("assets", "edgar_rincon_1.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "05-12-2025", "Monto USD": 150.00, "Descripción": "Por limpieza de granja ASIGLEH", "Imagen_Path": os.path.join("assets", "edgar_rincon_2.jpg")},
        {"Proveedor": "Jose Zambrano", "Fecha": "08-12-2025", "Monto USD": 950.00, "Descripción": "Por cuatrimoto GABE", "Imagen_Path": os.path.join("assets", "jose_zambrano.jpg")},
        {"Proveedor": "Juan Quinonez", "Fecha": "20-12-2025", "Monto USD": 261.00, "Descripción": "Compra directa", "Imagen_Path": os.path.join("assets", "juan_quinonez.jpg")},
        {"Proveedor": "Vito Ingravallo Mendez", "Fecha": "22-01-2026", "Monto USD": 250.00, "Descripción": "Por reparación de camión de la granja", "Imagen_Path": os.path.join("assets", "vito_ingravallo.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "02-02-2026", "Monto USD": 500.00, "Descripción": "Por pollitos GABE", "Imagen_Path": os.path.join("assets", "edgar_rincon_3.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "11-02-2026", "Monto USD": 56.00, "Descripción": "Por comida de gallinas", "Imagen_Path": os.path.join("assets", "edgar_rincon_4.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "17-02-2026", "Monto USD": 56.00, "Descripción": "Por comida de gallinas", "Imagen_Path": os.path.join("assets", "edgar_rincon_5.jpg")},
        {"Proveedor": "Brayan Diaz Marquez", "Fecha": "19-02-2026", "Monto USD": 200.00, "Descripción": "Por trabajos en la granja", "Imagen_Path": os.path.join("assets", "brayan_diaz.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "24-02-2026", "Monto USD": 350.00, "Descripción": "Por matas de limones GABE", "Imagen_Path": os.path.join("assets", "edgar_rincon_6.jpg")},
        {"Proveedor": "Edgar Rincon Albarracin", "Fecha": "09-03-2026", "Monto USD": 108.00, "Descripción": "Por comida de gallinas", "Imagen_Path": os.path.join("assets", "edgar_rincon_7.jpg")}
    ]
    
    df_zelle = pd.DataFrame(zelle_data)
    
    # Agregar columna con base64 si existe, de lo contrario None
    def load_image_base64(path):
        if os.path.exists(path):
            try:
                import base64
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                ext = os.path.splitext(path)[1].lower().replace(".", "")
                mime = f"image/{ext}" if ext in ["png", "jpg", "jpeg", "gif", "webp"] else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
            except Exception:
                return None
        return None

    df_zelle["Soporte (Imagen)"] = df_zelle["Imagen_Path"].apply(load_image_base64)
    
    # Omitimos la columna Imagen_Path en la vista
    df_zelle_display = df_zelle.drop(columns=["Imagen_Path"])
    
    st.dataframe(
        df_zelle_display,
        column_config={
            "Soporte (Imagen)": st.column_config.ImageColumn("Soporte", help="Soporte digital de la transacción"),
            "Monto USD": st.column_config.NumberColumn("Monto USD", format="$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("#### Resumen por Proveedor (Compras Directas)")
    
    # Crear gráfico de barras horizontales
    df_prov = df_zelle.groupby("Proveedor").agg(
        Monto_Total=("Monto USD", "sum"),
        Operaciones=("Monto USD", "count")
    ).reset_index()
    
    # Gráfico de barras horizontales usando Altair
    prov_chart = alt.Chart(df_prov).mark_bar().encode(
        x=alt.X('Monto_Total:Q', title='Monto Total ($ USD)'),
        y=alt.Y('Proveedor:N', sort='-x', title='Proveedor'),
        color=alt.value('#1e3c72'),  # Azul institucional
        tooltip=[
            alt.Tooltip('Proveedor:N', title='Proveedor'),
            alt.Tooltip('Monto_Total:Q', title='Monto Total ($ USD)', format=',.2f'),
            alt.Tooltip('Operaciones:Q', title='Nº Transacciones')
        ]
    ).properties(height=250)
    
    st.altair_chart(prov_chart, use_container_width=True)
    
    # Calcular totales para el Card
    total_monto_directo = df_zelle["Monto USD"].sum()
    total_ops_directo = len(df_zelle)
    
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color: #1e3c72; max-width: 350px; margin-top: 15px;">
            <div class="kpi-label">Total Operaciones Directas</div>
            <div class="kpi-value" style="color: #1e3c72;">${total_monto_directo:,.2f}</div>
            <div class="kpi-subvalue">{total_ops_directo} operaciones registradas</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------------------------
# SECCIÓN 2: FLUJO EN BS
# -------------------------------------------------------------------
with st.expander("📊 Sección 2: Flujo de operaciones a través de la cuenta administrativa en Bs", expanded=False):
    # -------------------------------------------------------------------
    # SECCIÓN DE MÉTRICAS (KPIs) - SIN CARD "SALDO DE CAJA"
    # -------------------------------------------------------------------
    if not df_filtered.empty and has_financial_cols:
        # Preparar datos financieros
        total_tx = len(df_filtered)
        
        # Calcular sumas
        usd_col = 'en $'
        usd_pos_col = 'en $pos' if 'en $pos' in df_filtered.columns else None
        usd_neg_col = 'en $neg' if 'en $neg' in df_filtered.columns else None
        
        usd_total_net = df_filtered[usd_col].sum() if usd_col in df_filtered.columns else 0.0
        usd_total_pos = df_filtered[usd_pos_col].sum() if usd_pos_col and usd_pos_col in df_filtered.columns else df_filtered[df_filtered[usd_col] > 0][usd_col].sum()
        usd_total_neg = df_filtered[usd_neg_col].sum() if usd_neg_col and usd_neg_col in df_filtered.columns else df_filtered[df_filtered[usd_col] < 0][usd_col].sum()
        
        # Renderizar KPI Cards (3 columnas)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            usd_color = "#16a34a" if usd_total_net >= 0 else "#dc2626"
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left-color: {usd_color};">
                    <div class="kpi-label">Saldo USD ($)</div>
                    <div class="kpi-value" style="color: {usd_color};">${usd_total_net:,.2f}</div>
                    <div class="kpi-subvalue">Neto acumulado en el rango</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left-color: #16a34a;">
                    <div class="kpi-label">Flujo USD Detalle</div>
                    <div class="kpi-value" style="font-size: 1.25rem; display: flex; flex-direction: column;">
                        <span style="color: #16a34a;">🟢 +${usd_total_pos:,.2f}</span>
                        <span style="color: #dc2626; margin-top: 4px;">🔴 -${abs(usd_total_neg):,.2f}</span>
                    </div>
                    <div class="kpi-subvalue">Ingresos y egresos en divisas</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left-color: #64748b;">
                    <div class="kpi-label">Transacciones</div>
                    <div class="kpi-value">{total_tx}</div>
                    <div class="kpi-subvalue">Operaciones en la selección</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Si la hoja no tiene las columnas financieras típicas
    elif not df_filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left-color: #2b5298;">
                    <div class="kpi-label">Filas Cargadas</div>
                    <div class="kpi-value">{df_filtered.shape[0]}</div>
                    <div class="kpi-subvalue">Total de registros filtrados</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left-color: #475569;">
                    <div class="kpi-label">Columnas Disponibles</div>
                    <div class="kpi-value">{df_filtered.shape[1]}</div>
                    <div class="kpi-subvalue">Estructura del conjunto de datos</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------------
    # SECCIÓN DEL EXPANDER "data" (REQUERIDO)
    # -------------------------------------------------------------------
    with st.expander("Data de movimientos del Banco Provincial", expanded=True):
        if df_filtered.empty:
            st.info("No hay registros que coincidan con los filtros aplicados.")
        else:
            # Preparar dataframe para mostrar
            df_display = df_filtered.copy()
            
            # Eliminar las columnas técnicas de limpieza y la columna SaldoBs solicitada
            cols_to_drop = [c for c in ['MontoBs_clean', 'SaldoBs_clean', 'SaldoBs'] if c in df_display.columns]
            if cols_to_drop:
                df_display = df_display.drop(columns=cols_to_drop)
                
            # Reemplazar None/NaN con celdas en blanco para en $pos y en $neg
            def clean_none_to_blank(val):
                if pd.isna(val) or val is None or str(val).strip().lower() in ['none', 'nan', '<na>', '']:
                    return ""
                try:
                    # Si es un número, devolverlo formateado
                    num = float(val)
                    return f"{num:,.2f}"
                except (ValueError, TypeError):
                    return str(val)
    
            for col in ['en $pos', 'en $neg', 'en$neg']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(clean_none_to_blank)
                    
            # Formatear la fecha para visualización limpia
            if 'Fecha' in df_display.columns:
                df_display['Fecha'] = df_display['Fecha'].apply(lambda x: x.strftime('%d-%m-%Y') if pd.notna(x) and hasattr(x, 'strftime') else str(x))
    
            # Definir la lógica de styling (Alto Contraste)
            # Fondo verde claro SI "en $" >= 0 y en color rojo en caso contrario. 
            # Alto contraste: textos oscuros sobre fondos claros, con fuente en negrita.
            def style_rows_by_usd(row):
                val = row.get('en $')
                try:
                    val_float = float(val) if pd.notna(val) else float('nan')
                except (ValueError, TypeError):
                    val_float = float('nan')
                    
                if pd.isna(val_float):
                    # Si no tiene datos en USD, mostrar con fondo neutro (blanco) y alto contraste
                    return ['background-color: #ffffff; color: #1e293b; border-bottom: 1px solid #e2e8f0;'] * len(row)
                    
                if val_float >= 0:
                    # Fondo verde claro (#d1e7dd) con texto negro (#000000) de alto contraste y negrita
                    return ['background-color: #d1e7dd; color: #000000; font-weight: bold; border-bottom: 1px solid #b7d1c4;'] * len(row)
                else:
                    # Fondo rojo claro (#f8d7da) con texto negro (#000000) de alto contraste y negrita
                    return ['background-color: #f8d7da; color: #000000; font-weight: bold; border-bottom: 1px solid #f5c2c7;'] * len(row)
    
            # Aplicar el estilo de alto contraste
            styler = df_display.style.apply(style_rows_by_usd, axis=1)
    
            # Formatear la columna 'en $' si es numérica
            if 'en $' in df_display.columns:
                styler = styler.format({'en $': lambda x: f"{x:,.2f}" if (pd.notna(x) and isinstance(x, (int, float))) else ""})
    
            # Mostrar DataFrame con el styler aplicado
            st.dataframe(
                styler, 
                use_container_width=True,
                hide_index=True
            )
            
            # Fila de acciones adicionales dentro del expander
            c_info, c_dl = st.columns([4, 1])
            with c_info:
                st.caption(f"Mostrando {len(df_display)} de {len(df_raw)} registros de la hoja '{SELECTED_SHEET}'.")
            
            with c_dl:
                # Botón para descargar datos filtrados en formato CSV
                csv_data = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name=f"gabe_data_{SELECTED_SHEET}_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # -------------------------------------------------------------------
    # SECCIÓN DE VISUALIZACIÓN GRÁFICA ADICIONAL (PREMIUM)
    # -------------------------------------------------------------------
    if not df_filtered.empty and has_financial_cols:
        st.markdown("### Visualización")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Flujo de Fondos", 
            "Ingresos(Detalle)",
            "Resumen de Ingresos",
            "Egresos(Detalle)"
        ])
        
        with tab1:
            # Flujo de Fondos Diario ($ USD) con barras coloreadas según el signo
            df_trend = df_filtered.sort_values(by='Fecha', ascending=True).dropna(subset=['Fecha']).copy()
            if len(df_trend) > 0:
                df_trend['en $_numeric'] = pd.to_numeric(df_trend['en $'], errors='coerce').fillna(0.0)
                
                # Agrupar por Fecha para ver flujos consolidados diarios y operaciones
                df_daily = df_trend.groupby('Fecha').agg(
                    Flow_Total=('en $_numeric', 'sum'),
                    Operaciones=('en $_numeric', 'count')
                ).reset_index()
                df_daily['Fecha_str'] = df_daily['Fecha'].dt.strftime('%d-%m-%Y')
                
                st.write("#### Flujo de Fondos Diario ($ USD)")
                
                # Gráfico de barras interactivo con Altair para aplicar colores condicionales y tooltip de operaciones
                daily_flow_chart = alt.Chart(df_daily).mark_bar().encode(
                    x=alt.X('Fecha:T', title='Fecha'),
                    y=alt.Y('Flow_Total:Q', title='Monto Neto ($ USD)'),
                    color=alt.condition(
                        alt.datum['Flow_Total'] >= 0,
                        alt.value('#16a34a'),  # Verde para flujo positivo
                        alt.value('#dc2626')   # Rojo para flujo negativo
                    ),
                    tooltip=[
                        alt.Tooltip('Fecha_str:N', title='Fecha'),
                        alt.Tooltip('Flow_Total:Q', title='Monto ($ USD)', format=',.2f'),
                        alt.Tooltip('Operaciones:Q', title='Nº Operaciones')
                    ]
                ).properties(height=400)
                st.altair_chart(daily_flow_chart, use_container_width=True)
            else:
                st.info("Se requiere información temporal para graficar la tendencia.")
                
        with tab2:
            st.write("#### Distribución de Ingresos por Detalle ($ USD)")
            desc_col_name = 'Descripción' if 'Descripción' in df_filtered.columns else ('Descripcion' if 'Descripcion' in df_filtered.columns else None)
            det_col_name = 'Detalle' if 'Detalle' in df_filtered.columns else None
            
            if desc_col_name:
                df_chart_data = df_filtered.copy()
                df_chart_data['en $_numeric'] = pd.to_numeric(df_chart_data['en $'], errors='coerce').fillna(0.0)
                
                # Filtro: Mostrar SOLO las positivas (Ingresos > 0)
                df_chart_data = df_chart_data[df_chart_data['en $_numeric'] > 0]
                
                if not df_chart_data.empty:
                    # Formar etiqueta: unos 50 caracteres del Detalle aplicando create_label_global
                    df_chart_data['Concepto'] = df_chart_data.apply(lambda r: create_label_global(r, det_col_name, desc_col_name), axis=1)
                    
                    # Agrupar, sumar monto y contar operaciones
                    desc_usd_sum = df_chart_data.groupby('Concepto').agg(
                        Monto_Total=('en $_numeric', 'sum'),
                        Operaciones=('en $_numeric', 'count')
                    ).reset_index()
                    
                    # Ordenar por monto descendente
                    desc_usd_sum = desc_usd_sum.sort_values(by='Monto_Total', ascending=False).head(15)
                    
                    # Gráfico de barras horizontales con Altair (incluye Nº Operaciones en Tooltip)
                    select_point = alt.selection_point(fields=['Concepto'], name='select_concept')
                    
                    horizontal_bar = alt.Chart(desc_usd_sum).mark_bar().encode(
                        x=alt.X('Monto_Total:Q', title='Monto Ingreso ($ USD)'),
                        y=alt.Y('Concepto:N', sort='-x', title='Detalle (Agrupado)'),
                        color=alt.value('#16a34a'),  # Verde para ingresos
                        tooltip=[
                            alt.Tooltip('Concepto:N', title='Concepto'), 
                            alt.Tooltip('Monto_Total:Q', title='Monto ($ USD)', format=',.2f'),
                            alt.Tooltip('Operaciones:Q', title='Nº Operaciones')
                        ]
                    ).add_params(
                        select_point
                    ).properties(height=400)
                    
                    event_data = st.altair_chart(horizontal_bar, use_container_width=True, on_select="rerun")
                    
                    # Manejar la selección para el Dialog emergente
                    if event_data and "selection" in event_data:
                        selection = event_data["selection"].get("select_concept", [])
                        selected_concept = None
                        if selection and isinstance(selection, list) and len(selection) > 0:
                            selected_concept = selection[0].get("Concepto") if isinstance(selection[0], dict) else selection[0]
                        elif selection and isinstance(selection, dict):
                            concepts = selection.get("Concepto", [])
                            selected_concept = concepts[0] if concepts else None
                            
                        if selected_concept:
                            if st.session_state.active_dialog_concept != selected_concept:
                                st.session_state.active_dialog_concept = selected_concept
                                # Filtrar operaciones correspondientes a este concepto en df_chart_data
                                df_concept_ops = df_chart_data[df_chart_data['Concepto'] == selected_concept]
                                if not df_concept_ops.empty:
                                    show_details_dialog(selected_concept, df_concept_ops)
                        else:
                            st.session_state.active_dialog_concept = None
                else:
                    st.info("No hay transacciones positivas (ingresos) registradas en esta selección.")
            else:
                st.info("Columna de descripción no encontrada.")
    
        with tab3:
            st.write("#### Distribución de Ingresos ($ USD) Agrupados por Grupo Principal")
            desc_col_name = 'Descripción' if 'Descripción' in df_filtered.columns else ('Descripcion' if 'Descripcion' in df_filtered.columns else None)
            det_col_name = 'Detalle' if 'Detalle' in df_filtered.columns else None
            
            if desc_col_name:
                df_incomes = df_filtered.copy()
                df_incomes['en $_numeric'] = pd.to_numeric(df_incomes['en $'], errors='coerce').fillna(0.0)
                
                # Filtrar solo ingresos (monto > 0)
                df_only_incomes = df_incomes[df_incomes['en $_numeric'] > 0].copy()
                
                if not df_only_incomes.empty:
                    # Clasificar usando exactamente la clasificación global de los detalles
                    df_only_incomes['Concepto'] = df_only_incomes.apply(lambda r: create_label_global(r, det_col_name, desc_col_name), axis=1)
                    
                    # Agrupar en exactamente 3 grupos: "Gabriel", "Sierra", y "Otros ingresos"
                    def donut_rollup(concept):
                        if concept in ["Gabriel", "Sierra"]:
                            return concept
                        return "Otros ingresos"
                        
                    df_only_incomes['Grupo_Donut'] = df_only_incomes['Concepto'].apply(donut_rollup)
                    
                    # Agrupar y sumar
                    incomes_grouped = df_only_incomes.groupby('Grupo_Donut')['en $_numeric'].sum().reset_index()
                    incomes_grouped = incomes_grouped.sort_values(by='en $_numeric', ascending=False)
                    incomes_grouped.columns = ['Grupo Principal', 'Monto USD']
                    
                    # Crear gráfico de donut con Altair
                    donut_chart = alt.Chart(incomes_grouped).mark_arc(innerRadius=60).encode(
                        theta=alt.Theta(field="Monto USD", type="quantitative"),
                        color=alt.Color(field='Grupo Principal', type="nominal", legend=alt.Legend(title="Grupos")),
                        tooltip=['Grupo Principal', alt.Tooltip('Monto USD:Q', format=',.2f')]
                    ).properties(height=450)
                    st.altair_chart(donut_chart, use_container_width=True)
                else:
                    st.info("No se registraron ingresos (valores mayores a 0) en el conjunto filtrado.")
            else:
                st.info("Columna de descripción no encontrada.")
    
        with tab4:
            st.write("#### Distribución de Egresos por Detalle ($ USD)")
            desc_col_name = 'Descripción' if 'Descripción' in df_filtered.columns else ('Descripcion' if 'Descripcion' in df_filtered.columns else None)
            det_col_name = 'Detalle' if 'Detalle' in df_filtered.columns else None
            
            if desc_col_name:
                df_chart_neg = df_filtered.copy()
                
                # Filtrar donde en $neg no es nulo o vacío
                df_chart_neg['en $neg_numeric'] = pd.to_numeric(df_chart_neg['en $neg'], errors='coerce')
                
                # Quedarse con aquellas que tienen valor numérico (negativo)
                df_chart_neg = df_chart_neg[df_chart_neg['en $neg_numeric'].notna()]
                
                if not df_chart_neg.empty:
                    # Aplicar clasificación global de egresos
                    df_chart_neg['Concepto_Neg'] = df_chart_neg.apply(lambda r: classify_expense_global(r, det_col_name, desc_col_name), axis=1)
                    
                    # Agrupar, sumar monto absoluto (para barras a la derecha)
                    df_chart_neg['en $neg_abs'] = df_chart_neg['en $neg_numeric'].abs()
                    
                    desc_neg_sum = df_chart_neg.groupby('Concepto_Neg').agg(
                        Monto_Total=('en $neg_abs', 'sum'),
                        Operaciones=('en $neg_numeric', 'count')
                    ).reset_index()
                    
                    # Ordenar por monto absoluto descendente
                    desc_neg_sum = desc_neg_sum.sort_values(by='Monto_Total', ascending=False).head(15)
                    
                    # Definir selección de puntos en Altair para egresos
                    select_point_neg = alt.selection_point(fields=['Concepto_Neg'], name='select_concept_neg')
                    
                    # Gráfico de barras horizontales con Altair (Rojo para egresos)
                    horizontal_bar_neg = alt.Chart(desc_neg_sum).mark_bar().encode(
                        x=alt.X('Monto_Total:Q', title='Monto Egreso ($ USD)'),
                        y=alt.Y('Concepto_Neg:N', sort='-x', title='Detalle (Agrupado)'),
                        color=alt.value('#dc2626'),  # Rojo para egresos
                        tooltip=[
                            alt.Tooltip('Concepto_Neg:N', title='Concepto'), 
                            alt.Tooltip('Monto_Total:Q', title='Monto Total ($ USD)', format=',.2f'),
                            alt.Tooltip('Operaciones:Q', title='Nº Operaciones')
                        ]
                    ).add_params(
                        select_point_neg
                    ).properties(height=400)
                    
                    event_data_neg = st.altair_chart(horizontal_bar_neg, use_container_width=True, on_select="rerun")
                    
                    # Manejar la selección para el Dialog emergente de egresos
                    if event_data_neg and "selection" in event_data_neg:
                        selection_neg = event_data_neg["selection"].get("select_concept_neg", [])
                        selected_concept_neg = None
                        if selection_neg and isinstance(selection_neg, list) and len(selection_neg) > 0:
                            selected_concept_neg = selection_neg[0].get("Concepto_Neg") if isinstance(selection_neg[0], dict) else selection_neg[0]
                        elif selection_neg and isinstance(selection_neg, dict):
                            concepts_neg = selection_neg.get("Concepto_Neg", [])
                            selected_concept_neg = concepts_neg[0] if concepts_neg else None
                            
                        if selected_concept_neg:
                            if st.session_state.active_dialog_concept_neg != selected_concept_neg:
                                st.session_state.active_dialog_concept_neg = selected_concept_neg
                                # Filtrar operaciones correspondientes a este concepto
                                df_concept_ops_neg = df_chart_neg[df_chart_neg['Concepto_Neg'] == selected_concept_neg]
                                if not df_concept_ops_neg.empty:
                                    show_details_dialog_neg(selected_concept_neg, df_concept_ops_neg)
                        else:
                            st.session_state.active_dialog_concept_neg = None
                else:
                    st.info("No hay transacciones de egreso (en $neg) registradas en esta selección.")
            else:
                st.info("Columna de descripción no encontrada.")


# Pie de página elegante
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 20px;">
        Desarrollado para el <strong>Dashboard Administrativo GABE</strong> | Prondamin 2026. Todos los derechos reservados.
    </div>
    """,
    unsafe_allow_html=True
)
