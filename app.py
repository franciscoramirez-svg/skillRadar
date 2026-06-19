import os
import sys
from datetime import datetime

# ── Headless server fixes (Render / no display) ──────────────
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("STREAMLIT_THEME_BASE", "dark")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
# Prevent interactive backends on headless servers
import matplotlib as _mpl
_mpl.use("Agg")
# Speed up font cache (avoid long build on first import)
import matplotlib.font_manager as _fm
try:
    _fm._load_fontmanager(try_read_cache=False)
except Exception:
    pass
# ──────────────────────────────────────────────────────────────

# ── Headless render: force Agg backend before any matplotlib import ──
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("STREAMLIT_THEME_BASE", "dark")
# ──────────────────────────────────────────────────────────────────────

import pandas as pd
import plotly.express as px
import streamlit as st

from core.processing import (
    CATEGORIAS_RADAR,
    COLUMNAS_REQUERIDAS,
    ETIQUETAS_RADAR,
    calcular_skill_radar,
    validar_columnas,
    validar_datos,
)
from core.radar import generar_radar_jugador
from core.risk import evaluar_todos
from core.wbgt import calcular_wbgt
from core.weather import obtener_clima
from reports.pdf_generator import PDFReporte

st.set_page_config(
    page_title="SkillRadar",
    page_icon="\u26bd",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');

        :root {
            --bg: #07111f;
            --bg-soft: rgba(10, 22, 40, 0.78);
            --line: rgba(120, 208, 255, 0.18);
            --primary: #5ef2ff;
            --secondary: #80ffb8;
            --text: #eaf7ff;
            --muted: #92abc6;
            --danger: #ff6b88;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(94, 242, 255, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(128, 255, 184, 0.14), transparent 24%),
                linear-gradient(135deg, #02060d 0%, #07111f 55%, #0b1730 100%);
            color: var(--text);
            font-family: 'Space Grotesk', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.04em;
            color: var(--text) !important;
        }

        .hero-card, .glass-panel, .section-header {
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(12, 25, 43, 0.9), rgba(6, 14, 25, 0.72));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(16px);
            border-radius: 26px;
        }

        .hero-card {
            padding: 44px 32px;
            margin-bottom: 24px;
            text-align: center;
        }

        .logo-orbit {
            width: 112px;
            height: 112px;
            margin: 0 auto 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(94, 242, 255, 0.45);
            box-shadow: 0 0 40px rgba(94, 242, 255, 0.18);
            background:
                radial-gradient(circle, rgba(94, 242, 255, 0.20), transparent 62%),
                conic-gradient(from 90deg, rgba(94, 242, 255, 0.1), rgba(128, 255, 184, 0.32), rgba(94, 242, 255, 0.1));
        }

        .logo-core {
            width: 72px;
            height: 72px;
            border-radius: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #03131c;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }

        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.2em;
            font-size: 0.8rem;
            color: var(--primary);
        }

        .hero-copy {
            color: var(--muted);
            max-width: 760px;
            margin: 0 auto;
        }

        .glass-panel {
            padding: 22px;
            min-height: 100%;
        }

        .section-header {
            padding: 22px 26px;
            margin-bottom: 20px;
        }

        div[data-testid="stMetric"] {
            border: 1px solid var(--line);
            background: rgba(8, 19, 34, 0.76);
            padding: 12px;
            border-radius: 20px;
        }

        div[data-testid="stForm"] {
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(5, 14, 25, 0.68);
            padding: 16px;
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 16px;
            min-height: 48px;
            border: 1px solid rgba(94, 242, 255, 0.32);
            background: linear-gradient(135deg, rgba(94, 242, 255, 0.14), rgba(128, 255, 184, 0.10));
            color: white;
            font-weight: 700;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--primary);
            background: linear-gradient(135deg, rgba(94, 242, 255, 0.25), rgba(128, 255, 184, 0.18));
            color: white;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 20px;
            background: rgba(5, 14, 25, 0.5);
        }

        .st-emotion-cache-1r6slb0, .st-emotion-cache-1aehpvj {
            color: var(--text);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 16px;
            padding: 8px 20px;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(94, 242, 255, 0.2), rgba(128, 255, 184, 0.1));
            border-color: var(--primary) !important;
        }

        .stSidebar {
            background: rgba(2, 6, 13, 0.85);
            border-right: 1px solid var(--line);
        }

        .stSidebar .sidebar-content {
            background: transparent;
        }

        .stFileUploader section {
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(5, 14, 25, 0.5);
        }

        .stSpinner > div {
            border-color: var(--primary) transparent transparent transparent;
        }

        .metric-card {
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(12, 25, 43, 0.9), rgba(6, 14, 25, 0.72));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(16px);
            border-radius: 26px;
            padding: 24px 16px;
            text-align: center;
        }

        .metric-card .value {
            font-size: 2.2rem;
            font-weight: 800;
            font-family: 'Orbitron', sans-serif;
            color: var(--primary);
            line-height: 1.2;
        }

        .metric-card .label {
            font-size: 0.75rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-top: 6px;
        }

        .risk-badge {
            display: inline-block;
            padding: 4px 16px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .stDataFrame [data-testid="StyledDataFrameDataCell"] {
            color: var(--text);
        }

        hr {
            border-color: var(--line) !important;
        }

        .stTextInput > div > div {
            border-radius: 12px;
            border-color: var(--line);
            background: rgba(5, 14, 25, 0.6);
            color: var(--text);
        }

        .stNumberInput > div > div {
            border-radius: 12px;
            border-color: var(--line);
            background: rgba(5, 14, 25, 0.6);
            color: var(--text);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:24px;">
            <div style="display:flex; justify-content:center;">
                <div class="logo-orbit">
                    <div class="logo-core">SR</div>
                </div>
            </div>
            <div class="eyebrow" style="margin-top:12px;">SkillRadar</div>
            <p style="color:var(--muted); font-size:0.85rem; margin-top:4px;">
                Analítica Deportiva
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='color:var(--text); font-weight:700; font-size:0.9rem; "
        "margin-bottom:12px;'>\u2699\ufe0f Configuraci\u00f3n</div>",
        unsafe_allow_html=True,
    )

    api_key = st.text_input(
        "🔑 API Key (WeatherAPI)",
        type="password",
        placeholder="Pega tu key aquí",
    )
    if api_key:
        os.environ["WEATHERAPI_KEY"] = api_key

    ciudad = st.text_input(
        "Ubicaci\u00f3n", value="Veracruz",
        placeholder="Ciudad o c\u00f3digo postal",
        label_visibility="collapsed",
    )

    st.markdown(
        "<hr style='margin:18px 0; border-color:var(--line);'/>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:var(--text); font-weight:700; font-size:0.9rem; "
        "margin-bottom:12px;'>\U0001f4c2 Datos del Partido</div>",
        unsafe_allow_html=True,
    )

    archivo = st.file_uploader(
        "Sube tu archivo .xlsx o .csv",
        type=["xlsx", "csv"],
        label_visibility="collapsed",
        help="Columnas: Nombre_Jugador, Posicion, Minutos, Pases_OK, "
        "Pases_Fallados, Tiros_Arco, Recuperaciones, Km_Corridos",
    )

    if archivo:
        st.markdown(
            f"<div style='color:var(--secondary); font-size:0.85rem;'>"
            f"\u2705 {archivo.name}</div>",
            unsafe_allow_html=True,
        )

if not archivo:
    st.markdown(
        """
        <div class='hero-card' style='max-width:800px; margin:60px auto;'>
            <div style='font-size:3rem; margin-bottom:16px;'>\u26bd</div>
            <div class='eyebrow' style='margin-bottom:8px;'>Bienvenido a</div>
            <h1 style='font-size:2.8rem; margin-bottom:12px;'>SkillRadar</h1>
            <p class='hero-copy'>
                Sistema de Anal\u00edtica Deportiva y Prevenci\u00f3n T\u00e9rmica.
                Carga tu planilla de partido y obt\u00e9n m\u00e9tricas FIFA, gr\u00e1ficos de radar
                y diagn\u00f3stico cl\u00ednico WBGT en segundos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📋 Formato esperado del archivo"):
        ejemplo = pd.DataFrame(
            [
                ["Luis Pérez", "Delantero", 90, 30, 5, 4, 8, 7.2],
                ["Carlos Gómez", "Defensa", 90, 40, 3, 1, 12, 5.8],
                ["Andrés López", "Medio", 85, 45, 6, 2, 10, 6.9],
            ],
            columns=COLUMNAS_REQUERIDAS,
        )
        st.dataframe(ejemplo, use_container_width=True)
    st.stop()

# ─── Carga y validación ─────────────────────────────────────────────────────
try:
    if archivo.name.endswith(".csv"):
        df_raw = pd.read_csv(archivo)
    else:
        df_raw = pd.read_excel(archivo)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

faltan = validar_columnas(df_raw)
if faltan:
    st.error(f"Columnas faltantes: {', '.join(faltan)}")
    st.stop()

errores = validar_datos(df_raw)
if errores:
    st.warning("Errores de validación:")
    for err in errores:
        st.caption(f"  • {err}")
    st.stop()

# ─── Clima ───────────────────────────────────────────────────────────────────
with st.spinner("Obteniendo datos climatológicos..."):
    clima = obtener_clima(ciudad)

if clima.get("ok"):
    temp = clima["temp"]
    humedad = clima["humidity"]
    st.sidebar.markdown(
        f"<div style='color:var(--primary); font-size:0.85rem; margin-top:12px;'>"
        f"\U0001f324 {clima['city']}: {temp}°C, {humedad}% HR</div>",
        unsafe_allow_html=True,
    )
else:
    temp = st.sidebar.number_input("Temperatura (°C)", value=30.0, step=0.5)
    humedad = st.sidebar.number_input(
        "Humedad Relativa (%)", value=75.0, step=1.0, max_value=100.0
    )
    if "error" in clima:
        st.sidebar.markdown(
            f"<div style='color:var(--danger); font-size:0.75rem;'>"
            f"\u26a0\ufe0f {clima['error']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            "<div style='color:var(--muted); font-size:0.75rem;'>"
            "\u2139\ufe0f Sin API key — datos manuales</div>",
            unsafe_allow_html=True,
        )

wbgt = calcular_wbgt(temp, humedad)

# ─── Procesamiento ───────────────────────────────────────────────────────────
df_procesado = calcular_skill_radar(df_raw)
riesgos = evaluar_todos(df_procesado, wbgt)

df_mostrar = df_procesado[
    [
        "Nombre_Jugador",
        "Posicion",
        "Minutos",
        "Distribucion",
        "Ataque",
        "Defensa",
        "Km_Puntaje",
        "Rendimiento",
    ]
].copy()

for col in ["Distribucion", "Ataque", "Defensa", "Km_Puntaje", "Rendimiento"]:
    df_mostrar[col] = df_mostrar[col].round(1)

# ─── Dashboard ───────────────────────────────────────────────────────────────
RIESGO_COLOR = {
    "BAJO": "#4CAF50",
    "MODERADO": "#FF9800",
    "ALTO": "#F44336",
    "CRÍTICO": "#9C27B0",
}

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="value">{temp:.1f}°C</div>'
        f'<div class="label">Temperatura</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div class="value">{humedad:.0f}%</div>'
        f'<div class="label">Humedad</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div class="value">{wbgt}°C</div>'
        f'<div class="label">WBGT (Estrés Térmico)</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    nivel_global = max(
        riesgos,
        key=lambda r: {"BAJO": 0, "MODERADO": 1, "ALTO": 2, "CRÍTICO": 3}[r["nivel"]],
    )
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="value" style="color:{RIESGO_COLOR[nivel_global["nivel"]]}">'
        f'{nivel_global["nivel"]}</div>'
        f'<div class="label">Riesgo General</div></div>',
        unsafe_allow_html=True,
    )

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📊 Plantilla General", "🎯 SkillRadar Individual", "🩺 Bloque Clínico"]
)

with tab1:
    st.markdown(
        "<h3 style='margin-bottom:16px;'>Rendimiento de la Plantilla</h3>",
        unsafe_allow_html=True,
    )

    def color_fila(row):
        r = row["Rendimiento"]
        if r >= 70:
            return ["background: rgba(76, 175, 80, 0.15);"] * len(row)
        if r >= 50:
            return ["background: rgba(255, 152, 0, 0.15);"] * len(row)
        return ["background: rgba(244, 67, 54, 0.15);"] * len(row)

    styled = df_mostrar.style.apply(color_fila, axis=1)
    st.dataframe(styled, use_container_width=True, height=350)

    fig = px.bar(
        df_mostrar,
        x="Nombre_Jugador",
        y="Rendimiento",
        color="Rendimiento",
        color_continuous_scale=["#F44336", "#FF9800", "#4CAF50"],
        text="Rendimiento",
        template="plotly_dark",
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Rendimiento (0-99)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#eaf7ff"},
        height=400,
        margin=dict(l=20, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown(
        "<h3 style='margin-bottom:16px;'>Gráficos de Radar Individuales</h3>",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, (_, row) in enumerate(df_procesado.iterrows()):
        vals = [row[c] for c in CATEGORIAS_RADAR]
        buf = generar_radar_jugador(vals, row["Nombre_Jugador"])

        with cols[i % 3]:
            st.image(buf, use_container_width=True)
            with st.expander(f"📊 {row['Nombre_Jugador']} - Detalle"):
                det = pd.DataFrame(
                    {
                        "Métrica": ETIQUETAS_RADAR,
                        "Puntaje": [f"{v:.1f}/99" for v in vals],
                    }
                )
                st.dataframe(det, hide_index=True, use_container_width=True)

with tab3:
    st.markdown(
        "<h3 style='margin-bottom:16px;'>Diagnóstico de Seguridad Térmica</h3>",
        unsafe_allow_html=True,
    )

    for r in riesgos:
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 3])
            with c1:
                st.markdown(f"**{r['jugador']}**")
                st.caption(r["posicion"])
            with c2:
                st.markdown(f"{r['km']:.2f} km")
            with c3:
                st.markdown(
                    f'<span class="risk-badge" style="background:{RIESGO_COLOR[r["nivel"]]};'
                    f'color:white">{r["nivel"]}</span>',
                    unsafe_allow_html=True,
                )
            with c4:
                st.markdown(r["accion"])
            st.markdown(
                "<hr style='margin:8px 0; border-color:var(--line);'/>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("#### 📋 Recomendaciones Generales")
    st.markdown(
        """
    - **Hidratación:** Consumir agua cada 15-20 minutos durante el partido.
    - **Pausas:** Realizar pausas de recuperación en zonas de sombra.
    - **Monitoreo:** Observar signos de golpe de calor (mareos, náuseas, piel seca).
    - **Comunicación:** Reportar cualquier síntoma al cuerpo técnico y padres de familia.
    """
    )

# ─── PDF ─────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border-color:var(--line);'/>", unsafe_allow_html=True)

if st.button("📄 Generar Reporte PDF Completo", type="primary"):
    with st.spinner("Generando reporte PDF..."):
        radares = []
        for _, row in df_procesado.iterrows():
            vals = [row[c] for c in CATEGORIAS_RADAR]
            radares.append(
                (row["Nombre_Jugador"], generar_radar_jugador(vals, row["Nombre_Jugador"]))
            )

        pdf = PDFReporte()
        pdf.agregar_encabezado(
            datetime.now().strftime("%d/%m/%Y"),
            f"{temp}°C / {humedad}% HR",
            f"{wbgt}°C",
        )
        pdf.agregar_tabla_plantilla(df_procesado)
        pdf.agregar_radares(radares)
        pdf.agregar_bloque_clinico(riesgos, wbgt)
        buf = pdf.generar()

    st.download_button(
        label="⬇️ Descargar PDF",
        data=buf,
        file_name=f"skillradar_reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
    )
    st.success("Reporte generado exitosamente.")
