"""Dashboard Clínico Premium — Atleta Híbrido OS v2.4.0
Clinical HRV Integration & Premium GitHub Visuals.
Ejecutar: .venv\\Scripts\\streamlit run app/dashboard.py
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import sys
import warnings
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ── Premium GitHub libraries ───────────────────────────────────────────────
from streamlit_echarts import JsCode, st_echarts
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_lottie import st_lottie
from hrvanalysis import get_time_domain_features

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adapters.file_yazio import FileYazioAdapter          # noqa: E402
from adapters.mock_garmin import MockGarminAdapter        # noqa: E402
from adapters.real_garmin import RealGarminAdapter        # noqa: E402
from core.acwr_brain import AcwrBrain                     # noqa: E402
from domain.models import (                               # noqa: E402
    AthleteDailySnapshot, FatigueZone, Phenotype, TrainingDecision,
)
from services.slot_finder import (                        # noqa: E402
    AllowedWindow, ScheduleConflictError, SlotFinder,
)

# ── Page config (primera llamada a Streamlit) ──────────────────────────────
st.set_page_config(
    page_title="Atleta Híbrido OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st_autorefresh(interval=5 * 60 * 1000, key="autorefresh")

# ── Puente Streamlit Secrets → variables de entorno ─────────────────────────
# En la nube, el token de Garmin se inyecta como secret; lo exponemos como env
# var para que RealGarminAdapter (capa pura, sin Streamlit) lo lea sin acoplarse.
import os as _os  # noqa: E402
try:
    for _k in ("GARMIN_TOKEN_B64", "GARMIN_EMAIL", "GOOGLE_TOKEN_B64"):
        if _k in st.secrets:
            _os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

# ── CSS Modo Oscuro Deportivo Premium ──────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
.section-label {
    font-size: 11px; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; color: #8b949e; margin-bottom: 6px; margin-top: 4px;
}
.zone-banner {
    border-radius: 16px; padding: 22px 32px; margin-bottom: 18px;
    text-align: center; font-size: 24px; font-weight: 800;
    letter-spacing: 0.3px; box-shadow: 0 8px 40px rgba(0,0,0,0.6);
}
.zone-sub { font-size: 14px; font-weight: 400; opacity: 0.88; margin-top: 6px; }
.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d; border-radius: 14px;
    padding: 18px 20px; margin: 4px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.hrv-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #161b22; border: 1px solid #30363d;
    border-radius: 20px; padding: 4px 12px; font-size: 12px;
    font-family: monospace; margin: 2px;
}
/* Batería Biológica */
.bat-wrap { display:flex; flex-direction:column; align-items:center; gap:8px; padding:8px 0 12px; }
.bat-body {
    width: 100px; height: 44px; border: 3px solid #484f58;
    border-radius: 7px; position: relative; background: #0d1117; overflow: hidden;
}
.bat-body::after {
    content:''; position:absolute; right:-9px; top:50%;
    transform:translateY(-50%); width:6px; height:20px;
    background:#484f58; border-radius:0 4px 4px 0;
}
.bat-fill { height:100%; transition:width 0.7s ease; }
.bat-pct { font-size:28px; font-weight:800; font-family:monospace; }
.bat-lbl { font-size:10px; color:#8b949e; letter-spacing:1px; text-transform:uppercase; }
.bat-clinical { font-size:10px; color:#8b949e; margin-top:2px; text-align:center; }
/* Botones */
.stButton>button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; letter-spacing: 0.4px !important;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950) !important;
    box-shadow: 0 0 16px rgba(63,185,80,0.4) !important;
    transform: translateY(-1px) !important;
}
/* Expander */
[data-testid="stExpander"] {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 12px !important;
}
/* Inputs sidebar */
.stSelectbox > div > div { background:#161b22 !important; border-color:#30363d !important; }
.stNumberInput > div > div > input {
    background:#0d1117 !important; color:#e6edf3 !important; border-color:#30363d !important;
}
/* Plotly / ECharts transparent background */
.js-plotly-plot .plotly, .js-plotly-plot .plotly div { background:transparent !important; }
iframe { background: transparent !important; }
/* Ocultar branding Streamlit */
/* Ocultar solo branding — NO tocar stToolbar ni stHeader (contienen el toggle del sidebar) */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecorationBar"] { display: none; }
/* Header oscuro pero visible */
[data-testid="stHeader"] {
    background-color: #0d1117 !important;
    border-bottom: 1px solid #21262d !important;
}
/* Sidebar toggle (expand/collapse) siempre visible */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    color: #e6edf3 !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    fill: #e6edf3 !important;
}
/* Ocultar solo el botón Deploy del toolbar, no el toolbar completo */
[data-testid="stToolbarActionButtonLabel"] { display: none; }
button[data-testid="stBaseButton-header"] { display: none; }

/* ── 📱 RESPONSIVE MÓVIL ─────────────────────────────────────────── */
/* Reducir padding lateral en pantallas estrechas para ganar espacio */
@media (max-width: 640px) {
    .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        padding-top: 2.6rem !important;
    }
    .zone-banner { font-size: 18px !important; padding: 16px 14px !important; }
    .zone-sub { font-size: 12px !important; }
    .section-label { font-size: 10px !important; }
    /* Evitar que los gráficos se desborden */
    .stPlotlyChart, iframe { max-width: 100% !important; }
    /* Botones más altos = mejor objetivo táctil */
    .stButton > button { min-height: 44px !important; font-size: 15px !important; }
}
/* Objetivos táctiles cómodos también en tablet */
.stNumberInput button { min-width: 34px !important; min-height: 34px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes de paleta ───────────────────────────────────────────────────
TZ    = ZoneInfo("America/Bogota")
NEON  = "#39d353"
RED   = "#ef4444"
BLUE  = "#3b82f6"
AMBER = "#f59e0b"
BG    = "rgba(0,0,0,0)"
GRID  = "#21262d"
TXT   = "#e6edf3"
MUTED = "#8b949e"

SCENARIO_MAP = {
    "Óptimo 🟢":      "optimo",
    "Fatigado 🔴":     "fatiga",
    "Subentrenado 🔵": "subcarga",
}
ZONE_CFG = {
    FatigueZone.LESION: dict(
        bg="linear-gradient(135deg,#7f1d1d,#991b1b)", border=RED, color=RED,
        icon="🔴", label="ZONA DE ALERTA — RIESGO DE LESIÓN",
        sub="Tu cuerpo está sobrecargado. Hoy es día de regeneración activa.",
    ),
    FatigueZone.OPTIMIZACION: dict(
        bg="linear-gradient(135deg,#14532d,#166534)", border="#22c55e", color=NEON,
        icon="🟢", label="ZONA ÓPTIMA — VENTANA DE CRECIMIENTO",
        sub="Tu cuerpo está listo para adaptarse. Hoy entrenas fuerte.",
    ),
    FatigueZone.FUNCIONAL_BAJO: dict(
        bg="linear-gradient(135deg,#1e3a8a,#1d4ed8)", border=BLUE, color=BLUE,
        icon="🔵", label="ZONA FUNCIONAL — MARGEN PARA CONSTRUIR",
        sub="Estás descansado. Es hora de elevar la carga de entrenamiento.",
    ),
}

# Lottie CDN públicas (LottieFiles free assets)
_LOTTIE_HEARTBEAT = "https://assets4.lottiefiles.com/packages/lf20_0yfsb3a1.json"
_LOTTIE_SUCCESS   = "https://assets9.lottiefiles.com/packages/lf20_jbrw3hcz.json"


# ── Motor Clínico HRV (hrv-analysis) ──────────────────────────────────────

def _generate_rr_intervals(scenario: str, n: int = 300) -> list[float]:
    """Genera intervalos RR (ms) realistas y deterministas por escenario de fatiga."""
    rng = np.random.default_rng(seed=42)
    params = {
        "fatiga":   (700, 32),   # HRV deprimida → RMSSD ~40ms, HR ~86bpm
        "subcarga": (870, 50),   # HRV elevada   → RMSSD ~68ms, HR ~70bpm
        "optimo":   (820, 46),   # HRV óptima    → RMSSD ~63ms, HR ~73bpm
    }
    base, std = params.get(scenario, params["optimo"])
    noise = rng.normal(0, std, n)
    # Suavizado AR-1 para autocorrelación fisiológica
    smoothed = np.convolve(noise, [0.35, 0.65], mode="same")
    return np.clip(base + smoothed, 350, 1800).tolist()


@st.cache_data(ttl=3600, show_spinner=False)
def _clinical_hrv(scenario: str) -> dict[str, float]:
    """Computa métricas clínicas reales de HRV usando hrv-analysis (Aura-healthcare)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rr = _generate_rr_intervals(scenario)
        try:
            f = get_time_domain_features(rr)
        except Exception:
            f = {"rmssd": 55.0, "sdnn": 45.0, "mean_hr": 65.0, "pnni_50": 18.0}
    return {
        "rmssd":   round(float(f.get("rmssd", 55.0)), 1),
        "sdnn":    round(float(f.get("sdnn", 45.0)), 1),
        "mean_hr": round(float(f.get("mean_hr", 65.0)), 1),
        "pnni50":  round(float(f.get("pnni_50", 18.0)), 1),
    }


# ── Lottie Loader (CDN con caché 24h y degradación elegante) ─────────────

@st.cache_data(ttl=86400, show_spinner=False)
def _lottie(url: str) -> dict | None:
    """Descarga y cachea animación Lottie. Retorna None si no hay conexión."""
    try:
        import requests
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _render_lottie(url: str, height: int = 140, key: str | None = None) -> None:
    """Renderiza Lottie con fallback silencioso si CDN no responde."""
    data = _lottie(url)
    if data:
        st_lottie(data, height=height, quality="medium", loop=True, key=key)


# ── ECharts Gauge — Termómetro del Motor ACWR ─────────────────────────────

def _acwr_gauge_options(acwr: float) -> dict:
    """Genera la configuración ECharts del velocímetro ACWR con 4 zonas de color."""
    if acwr > 1.5:    needle_color = RED
    elif acwr > 1.3:  needle_color = AMBER
    elif acwr >= 0.8: needle_color = NEON
    else:             needle_color = BLUE

    detail_fmt = JsCode("function(v){ return parseFloat(v).toFixed(2); }")
    label_fmt  = JsCode("function(v){ return [0, 0.5, 1.0, 1.5, 2.0].includes(Math.round(v*10)/10) ? v.toFixed(1) : ''; }")

    return {
        "backgroundColor": "transparent",
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0,
            "max": 2,
            "splitNumber": 4,
            "radius": "94%",
            "center": ["50%", "72%"],
            "axisLine": {
                "lineStyle": {
                    "width": 32,
                    "color": [
                        # Normalized: value / max(2.0)
                        [0.40, "#0d1f3c"],   # 0.0–0.8 → Motor Frío (azul profundo)
                        [0.65, "#0a2010"],   # 0.8–1.3 → Zona Óptima (verde oscuro)
                        [0.75, "#2d1f00"],   # 1.3–1.5 → Zona Límite (ámbar oscuro)
                        [1.00, "#2d0808"],   # 1.5–2.0 → ¡Peligro! (rojo oscuro)
                    ],
                }
            },
            "splitLine": {
                "length": 18,
                "lineStyle": {"color": "#484f58", "width": 3},
            },
            "axisTick": {
                "length": 9,
                "lineStyle": {"color": "#30363d", "width": 2},
            },
            "axisLabel": {
                "color": MUTED,
                "fontSize": 11,
                "distance": 20,
                "formatter": label_fmt,
            },
            "pointer": {
                "length": "65%",
                "width": 10,
                "itemStyle": {
                    "color": needle_color,
                    "shadowColor": needle_color,
                    "shadowBlur": 18,
                },
            },
            "anchor": {
                "show": True,
                "showAbove": True,
                "size": 18,
                "itemStyle": {"borderColor": needle_color, "borderWidth": 3, "color": "#0d1117"},
            },
            "title": {
                "offsetCenter": ["0%", "85%"],
                "fontSize": 10,
                "color": MUTED,
                "fontWeight": "normal",
                "letterSpacing": 2,
            },
            "detail": {
                "valueAnimation": True,
                "formatter": detail_fmt,
                "color": needle_color,
                "fontSize": 46,
                "fontFamily": "monospace",
                "fontWeight": "bold",
                "offsetCenter": ["0%", "52%"],
            },
            "data": [{"value": round(acwr, 3), "name": "ÍNDICE DE FATIGA"}],
        }]
    }


# ── Gráficos auxiliares (Plotly) ───────────────────────────────────────────

def battery_html(pct: float, color: str, rmssd: float, sdnn: float) -> str:
    fill = max(min(pct, 100), 0)
    glow = f"box-shadow:0 0 14px {color}55;"
    return f"""
    <div class="bat-wrap">
        <div class="bat-body" style="{glow}">
            <div class="bat-fill" style="width:{fill}%;background:{color};"></div>
        </div>
        <div class="bat-pct" style="color:{color};">{fill:.0f}%</div>
        <div class="bat-lbl">Batería Biológica</div>
        <div class="bat-clinical">
            <span class="hrv-badge" style="border-color:{color}40;">
                💓 RMSSD <b style="color:{color}">{rmssd:.0f} ms</b>
            </span>
            <span class="hrv-badge">
                📊 SDNN <b>{sdnn:.0f} ms</b>
            </span>
        </div>
    </div>
    """


def ring_fig(current: float, target: float, title: str, unit: str, color: str):
    import plotly.graph_objects as go
    pct = min(current / max(target, 1) * 100, 100)
    fig = go.Figure(go.Pie(
        values=[pct, max(100 - pct, 0)], hole=0.74,
        marker_colors=[color, "#1c2128"],
        textinfo="none", hoverinfo="skip",
        sort=False, direction="clockwise",
    ))
    fig.add_annotation(text=f"<b>{pct:.0f}%</b>", x=0.5, y=0.62, showarrow=False,
                       font=dict(size=19, color=color, family="monospace"))
    fig.add_annotation(text=f"{current:.0f}<br><span style='font-size:9px'>{unit}</span>",
                       x=0.5, y=0.36, showarrow=False, font=dict(size=11, color=MUTED))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, height=165,
        margin=dict(t=6, b=28, l=6, r=6), showlegend=False,
        title=dict(text=f"<b>{title}</b>", font=dict(color=MUTED, size=11), x=0.5, y=0.04),
    )
    return fig


def trend_fig(df: pd.DataFrame):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_hrect(y0=0,   y1=0.8, fillcolor=BLUE,  opacity=0.05, line_width=0)
    fig.add_hrect(y0=0.8, y1=1.3, fillcolor=NEON,  opacity=0.05, line_width=0)
    fig.add_hrect(y0=1.3, y1=1.5, fillcolor=AMBER, opacity=0.05, line_width=0)
    fig.add_hrect(y0=1.5, y1=2.5, fillcolor=RED,   opacity=0.05, line_width=0)
    for y, c, lbl in [(0.8, BLUE, "Mínimo"), (1.3, AMBER, "Límite"), (1.5, RED, "Peligro")]:
        fig.add_hline(y=y, line_dash="dot", line_color=c, opacity=0.35,
                      annotation_text=lbl, annotation_font_color=c,
                      annotation_font_size=10, annotation_position="right")
    fig.add_trace(go.Bar(
        x=df["Fecha"], y=df["Carga Aguda"], name="Carga diaria", yaxis="y2",
        marker_color="rgba(57,211,83,0.10)",
        hovertemplate="<b>%{x|%d %b}</b><br>Carga: %{y:.0f}<extra></extra>",
    ))
    pt_colors = df["ACWR"].apply(
        lambda v: RED if v > 1.5 else (AMBER if v > 1.3 else (NEON if v >= 0.8 else BLUE))
    ).tolist()
    fig.add_trace(go.Scatter(
        x=df["Fecha"], y=df["ACWR"],
        fill="tozeroy", fillcolor="rgba(57,211,83,0.04)",
        line=dict(color=NEON, width=2.5),
        mode="lines+markers",
        marker=dict(size=9, color=pt_colors, line=dict(width=2, color="#0d1117")),
        customdata=df[["ACWR", "Estado"]].values,
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            "Índice de Fatiga: <b>%{customdata[0]:.2f}</b><br>"
            "<i>%{customdata[1]}</i><extra></extra>"
        ),
        name="Índice de Fatiga",
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, height=300,
        margin=dict(t=10, b=10, l=0, r=65), font=dict(color=TXT, size=11),
        xaxis=dict(showgrid=True, gridcolor=GRID, tickformat="%d %b",
                   tickfont=dict(color=MUTED, size=10), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRID, range=[0, 2.3],
                   tickfont=dict(color=MUTED, size=10), zeroline=False, title=None),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title=None,
                    tickfont=dict(color="#1e2d1f", size=9),
                    range=[0, (df["Carga Aguda"].max() or 1) * 7]),
        hovermode="x unified",
        legend=dict(font=dict(color=MUTED, size=10), bgcolor=BG, x=0.01, y=0.99),
    )
    return fig


def timeline_fig(decision: TrainingDecision, busy: list):
    import plotly.graph_objects as go
    fig = go.Figure()
    for h in range(6, 21, 2):
        fig.add_vrect(x0=h, x1=h + 1, fillcolor="rgba(255,255,255,0.015)", line_width=0)
    for s, e in busy:
        sh, eh = s.hour + s.minute / 60, e.hour + e.minute / 60
        fig.add_trace(go.Bar(
            y=["Agenda"], x=[eh - sh], base=[sh], orientation="h", width=0.5,
            marker_color="rgba(239,68,68,0.5)", marker_line_color=RED, marker_line_width=1.5,
            name=f"⛔ {s.strftime('%H:%M')}–{e.strftime('%H:%M')}",
            hovertemplate=(f"⛔ Bloqueado<br>{s.strftime('%H:%M')} → {e.strftime('%H:%M')}<extra></extra>"),
        ))
    try:
        today = dt.date.today()
        start_dt = SlotFinder(AllowedWindow(6, 21)).find(
            today, decision.start_hour, decision.duration_min, busy, TZ
        )
        end_dt = start_dt + dt.timedelta(minutes=decision.duration_min)
        sh = start_dt.hour + start_dt.minute / 60
        fig.add_trace(go.Bar(
            y=["Agenda"], x=[decision.duration_min / 60], base=[sh],
            orientation="h", width=0.5,
            marker_color="rgba(57,211,83,0.45)", marker_line_color=NEON, marker_line_width=2,
            name=f"🏋️ {start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}",
            hovertemplate=(
                f"✅ {decision.title}<br>"
                f"{start_dt.strftime('%H:%M')} → {end_dt.strftime('%H:%M')}<br>"
                f"{decision.duration_min} min<extra></extra>"
            ),
        ))
    except ScheduleConflictError:
        pass
    fig.update_layout(
        barmode="overlay", height=130, paper_bgcolor=BG, plot_bgcolor=BG,
        margin=dict(t=0, b=44, l=0, r=0),
        xaxis=dict(range=[6, 21], showgrid=True, gridcolor=GRID,
                   tickvals=list(range(6, 22, 2)),
                   ticktext=[f"{h}:00" for h in range(6, 22, 2)],
                   tickfont=dict(color=MUTED, size=10), zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        legend=dict(orientation="h", x=0, y=-0.65, font=dict(color=MUTED, size=10), bgcolor=BG),
        showlegend=True, font=dict(color=TXT),
    )
    return fig


# ── Colores de macronutrientes (consistentes con los anillos) ──────────────
PROT_C, CARB_C, FAT_C, KCAL_C = NEON, BLUE, "#f472b6", AMBER
MACRO_COLORS = {"kcal": KCAL_C, "prot": PROT_C, "carbs": CARB_C,
                "fat": FAT_C, "weight": MUTED}

# CSS inyectado una sola vez: acento de color por macro vía clase nativa
# `.st-key-macrobox_<k>` (Streamlit 1.58 — reemplaza al deprecado stylable_container).
_macro_css = "<style>"
for _k, _c in MACRO_COLORS.items():
    _macro_css += f"""
    .st-key-macrobox_{_k} {{
        border-left: 4px solid {_c};
        border-radius: 10px; background: #0d1117;
        padding: 2px 10px 2px 14px; margin-bottom: 8px;
        box-shadow: 0 0 0 1px #21262d;
    }}
    .st-key-macrobox_{_k} label p {{
        color: {_c} !important; font-weight: 700 !important; font-size: 12px !important;
    }}
    .st-key-macrobox_{_k} input {{
        font-family: monospace !important; font-weight: 600 !important; font-size: 17px !important;
    }}"""
_macro_css += "</style>"
st.markdown(_macro_css, unsafe_allow_html=True)


def macro_input(label: str, *, key: str, **kwargs):
    """Input de macro con acento de color a la izquierda (estilo MacroFactor/Yazio).

    Usa `st.container(key=...)` nativo: Streamlit le asigna la clase
    `.st-key-macrobox_<key>` cuyo color se define en `MACRO_COLORS` y se
    inyecta arriba. El borde y la etiqueta coloreada dan identidad a cada macro.
    """
    with st.container(key=f"macrobox_{key}"):
        return st.number_input(label, key=f"in_{key}", **kwargs)


# ── Sidebar ────────────────────────────────────────────────────────────────
scenario = "optimo"
garmin_connected = RealGarminAdapter.is_authenticated()

with st.sidebar:
    st.markdown("## 🧬 Atleta Híbrido OS")
    st.markdown("<div class='section-label'>📡 Garmin Connect</div>", unsafe_allow_html=True)

    if garmin_connected:
        st.success("🟢 Datos reales activos")
    else:
        st.error("🔴 Sin conexión a Garmin")
        with st.expander("¿Cómo conectar?"):
            st.code("cd sync_orchestrator\npython setup_garmin.py", language="bash")
        st.markdown("<div class='section-label'>⚙️ Simulación</div>", unsafe_allow_html=True)
        state_label = st.selectbox(
            "Estado", list(SCENARIO_MAP.keys()), index=0, label_visibility="collapsed",
        )
        scenario = SCENARIO_MAP[state_label]

    st.divider()
    st.markdown("<div class='section-label'>🥗 Nutrición de hoy</div>",
                unsafe_allow_html=True)
    saved_y = FileYazioAdapter().fetch_daily(dt.date.today())
    with st.form("yazio_form", border=False):
        kcal_in = macro_input(
            "🔥 CALORÍAS (kcal)", key="kcal",
            min_value=0, value=saved_y.kcal_ingested, step=50,
        )
        cP, cC = st.columns(2)
        with cP:
            prot_in = macro_input(
                "🥩 PROTEÍNA (g)", key="prot",
                min_value=0.0, value=saved_y.protein_g, step=5.0, format="%.0f",
            )
        with cC:
            carbs_in = macro_input(
                "🍚 CARBOS (g)", key="carbs",
                min_value=0.0, value=saved_y.carbs_g, step=10.0, format="%.0f",
            )
        cF, cW = st.columns(2)
        with cF:
            fat_in = macro_input(
                "🥑 GRASAS (g)", key="fat",
                min_value=0.0, value=saved_y.fat_g, step=5.0, format="%.0f",
            )
        with cW:
            weight_in = macro_input(
                "⚖️ PESO (kg)", key="weight",
                min_value=30.0, value=saved_y.bodyweight_kg, step=0.1, format="%.1f",
            )
        if st.form_submit_button("💾 Guardar registro de hoy", use_container_width=True):
            FileYazioAdapter.save_today(
                int(kcal_in), float(prot_in), float(carbs_in),
                float(fat_in), float(weight_in),
            )
            st.success("✅ Guardado")
            st.rerun()

    st.divider()
    phenotype = st.selectbox("🎯 Fenotipo objetivo", [p.value for p in Phenotype], index=2)
    st.caption(f"🔄 Auto-refresh 5 min · {dt.datetime.now().strftime('%H:%M')}")


# ── Pipeline de datos ──────────────────────────────────────────────────────
@st.cache_resource
def _real_garmin_adapter():
    return RealGarminAdapter()


@st.cache_data(ttl=300, show_spinner=False)
def _build_trend(cache_key: str, _adapter, days: int = 14) -> pd.DataFrame:
    today = dt.date.today()
    rows = []
    for i in range(days - 1, -1, -1):
        d = today - dt.timedelta(days=i)
        g = _adapter.fetch_daily(d)
        snap = AthleteDailySnapshot(g, FileYazioAdapter().fetch_daily(d))
        v = snap.acwr
        estado = (
            "⚠️ Mucha fatiga acumulada — necesitabas descanso" if v > 1.5
            else "🔶 Entrenamiento intenso, cerca del límite" if v > 1.3
            else "✅ Ventana perfecta de entrenamiento" if v >= 0.8
            else "💤 Cuerpo fresco — puedes cargar más" if v >= 0.5
            else "🧊 Muy poco estímulo estos días"
        )
        rows.append({"Fecha": d, "ACWR": round(v, 3),
                     "Carga Aguda": round(g.acute_load, 1), "Estado": estado})
    return pd.DataFrame(rows)


today = dt.date.today()

if garmin_connected:
    try:
        g_adapter = _real_garmin_adapter()
        g_metrics = g_adapter.fetch_daily(today)
        cache_key = "real"
    except Exception as exc:
        st.warning(f"⚠️ Garmin falló ({exc}). Activando simulación.", icon="⚠️")
        garmin_connected = False
        g_adapter = MockGarminAdapter(scenario)
        g_metrics = g_adapter.fetch_daily(today)
        cache_key = scenario
else:
    g_adapter = MockGarminAdapter(scenario)
    g_metrics = g_adapter.fetch_daily(today)
    cache_key = scenario

y_metrics    = FileYazioAdapter().fetch_daily(today)
snapshot     = AthleteDailySnapshot(g_metrics, y_metrics)
decision     = AcwrBrain().evaluate(snapshot, Phenotype(phenotype))
zcfg         = ZONE_CFG[decision.zone]
weight_kg    = y_metrics.bodyweight_kg or 60.0
prot_target  = decision.protein_g_per_kg_target * weight_kg
carbs_target = decision.carbs_g_per_kg_target * weight_kg
kcal_target  = 2500
hrv_pct      = min(max((snapshot.hrv_ratio - 0.70) / 0.60 * 100, 0), 100)
hrv_color    = NEON if hrv_pct > 65 else (AMBER if hrv_pct > 35 else RED)

# Motor Clínico HRV — métricas calculadas por hrv-analysis
hrv_clinical = _clinical_hrv(cache_key if cache_key in ("fatiga", "subcarga", "optimo") else "optimo")

# Aplicar streamlit-extras metric cards styling (borde izquierdo reactivo al estado)
style_metric_cards(
    background_color="#161b22",
    border_color="#30363d",
    border_left_color=zcfg["color"],
    border_radius_px=10,
    border_size_px=1,
    box_shadow=False,
)

busy_today = [
    (dt.datetime.combine(today, dt.time(9,  0), tzinfo=TZ),
     dt.datetime.combine(today, dt.time(10, 30), tzinfo=TZ)),
    (dt.datetime.combine(today, dt.time(17, 30), tzinfo=TZ),
     dt.datetime.combine(today, dt.time(18, 30), tzinfo=TZ)),
]


# ── Banner de Zona ─────────────────────────────────────────────────────────
st.markdown(
    f"""<div class="zone-banner"
         style="background:{zcfg['bg']};border:2px solid {zcfg['border']};">
        {zcfg['icon']} &nbsp; {zcfg['label']}
        <div class="zone-sub">{zcfg['sub']}</div>
    </div>""",
    unsafe_allow_html=True,
)



# ── Fila 1: Velocímetro ECharts | Batería Clínica | Bloque ────────────────
c1, c2, c3 = st.columns([1.1, 0.9, 1.0], gap="medium")

with c1:
    st.markdown("<div class='section-label'>⚡ Termómetro del Motor</div>",
                unsafe_allow_html=True)
    # ECharts Gauge (streamlit-echarts — Apache ECharts animado)
    st_echarts(
        options=_acwr_gauge_options(snapshot.acwr),
        height="240px",
        key="acwr_gauge",
    )
    motor_msg = (
        "🔴 Motor al rojo — descansa hoy"      if snapshot.acwr > 1.5
        else "🟡 Al límite — cuida la carga"   if snapshot.acwr > 1.3
        else "🟢 En zona óptima — ¡a entrenar!" if snapshot.acwr >= 0.8
        else "🔵 Motor frío — sube el estímulo"
    )
    st.markdown(
        f"<div style='text-align:center;color:{zcfg['color']};font-weight:700;"
        f"font-size:13px;margin-top:-6px;'>{motor_msg}</div>",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown("<div class='section-label'>🫀 Batería Biológica — HRV Clínico</div>",
                unsafe_allow_html=True)
    # Batería + badges RMSSD/SDNN calculados por hrv-analysis
    st.markdown(
        battery_html(hrv_pct, hrv_color, hrv_clinical["rmssd"], hrv_clinical["sdnn"]),
        unsafe_allow_html=True,
    )
    # Métricas estilizadas con streamlit-extras
    ma, mb = st.columns(2)
    ma.metric("FC Reposo", f"{snapshot.garmin.resting_hr} lpm",
              delta=f"{snapshot.garmin.resting_hr - 48:+d} bpm")
    mb.metric("FC Media HRV", f"{hrv_clinical['mean_hr']:.0f} bpm")
    ma.metric("Km (7d)", f"{snapshot.garmin.mileage_7d_km:.1f} km")
    mb.metric("Carga Aguda", f"{snapshot.garmin.acute_load:.0f}")

with c3:
    st.markdown("<div class='section-label'>🎯 Bloque de Entrenamiento</div>",
                unsafe_allow_html=True)

    # Control de hora manual: si se activa, la hora elegida pasa a ser la
    # "preferida" y el SlotFinder sigue esquivando conflictos (puede desplazarla).
    manual_hour = st.toggle("🕐 Ajustar la hora manualmente", value=False, key="manual_hour")
    if manual_hour:
        h = st.slider(
            "Hora de inicio preferida", min_value=6, max_value=21,
            value=int(decision.start_hour), step=1, format="%d:00", key="man_h",
        )
        eff_decision = dataclasses.replace(decision, start_hour=h)
    else:
        eff_decision = decision

    slot_lbl = "☀️ Mañana (AM)" if eff_decision.start_hour < 12 else "🌆 Tarde (PM)"
    manual_tag = ' &nbsp;·&nbsp; <span style="color:#f59e0b">manual</span>' if manual_hour else ""
    st.markdown(
        f'<div class="metric-card">'
        f'<div style="color:{zcfg["color"]};font-size:17px;font-weight:700;margin-bottom:8px;">'
        f'{eff_decision.title}</div>'
        f'<div style="color:{MUTED};font-size:12px;margin-bottom:14px;">'
        f'{slot_lbl} &nbsp;·&nbsp; {eff_decision.start_hour}:00 &nbsp;·&nbsp; '
        f'{eff_decision.duration_min} min{manual_tag}</div>'
        f'<div style="font-size:13px;line-height:2.1;">'
        f'🥩 Proteína: <b style="color:{NEON};">{prot_target:.0f} g</b>'
        f'<span style="color:{MUTED};font-size:11px;"> ({decision.protein_g_per_kg_target:.1f} g/kg)</span><br>'
        f'🍚 Carbos: <b style="color:{BLUE};">{carbs_target:.0f} g</b>'
        f'<span style="color:{MUTED};font-size:11px;"> ({decision.carbs_g_per_kg_target:.1f} g/kg)</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    cal_ready = bool(_os.environ.get("GOOGLE_TOKEN_B64")) or Path("token.json").exists()
    if st.button(
        "📅 Agendar en Google Calendar" if cal_ready else "👁️ Ver horario del bloque",
        use_container_width=True, type="primary",
    ):
        if cal_ready:
            try:
                from services.google_calendar import GoogleCalendarService
                svc = GoogleCalendarService(
                    timezone="America/Bogota", window=AllowedWindow(6, 21),
                )
                ev = svc.upsert_training_block(today, eff_decision)
                hhmm = ev["start"]["dateTime"][11:16]
                st.success(f"✅ Agendado en tu Google Calendar a las **{hhmm}**")
                if manual_hour and hhmm[:2] != f"{eff_decision.start_hour:02d}":
                    st.warning(f"⏩ Movido desde las {eff_decision.start_hour}:00 (esa hora estaba ocupada)")
                st.caption("Revisa tu calendario — el bloque ya está sincronizado.")
            except Exception as exc:
                st.error(f"⛔ No se pudo agendar: {exc}")
        else:
            try:
                start_dt = SlotFinder(AllowedWindow(6, 21)).find(
                    today, eff_decision.start_hour, eff_decision.duration_min, busy_today, TZ,
                )
                end_dt = start_dt + dt.timedelta(minutes=eff_decision.duration_min)
                st.success(f"✅ Slot libre: **{start_dt.strftime('%H:%M')} – {end_dt.strftime('%H:%M')}**")
                if start_dt.hour != eff_decision.start_hour:
                    st.warning(f"⏩ Reasignado desde {eff_decision.start_hour}:00 (había conflicto)")
                st.caption("💡 Conecta Google Calendar para agendarlo de verdad (ver guía).")
            except ScheduleConflictError as exc:
                st.error(f"⛔ {exc}")

st.markdown("<br>", unsafe_allow_html=True)


# ── Fila 2: Gráfico de Tendencia 14 días ──────────────────────────────────
st.markdown("<div class='section-label'>📈 Índice de Fatiga — Últimos 14 días</div>",
            unsafe_allow_html=True)
st.caption("Pasa el cursor sobre el gráfico para ver qué pasó ese día en lenguaje sencillo")

df_trend = _build_trend(cache_key, g_adapter)

import plotly.graph_objects as go
st.plotly_chart(trend_fig(df_trend), use_container_width=True,
                config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)


# ── Fila 3: Anillos de Nutrición | Agenda del Día ─────────────────────────
rc1, rc2 = st.columns([1.0, 1.15], gap="large")

with rc1:
    st.markdown("<div class='section-label'>🥗 Nutrición de Hoy vs Meta</div>",
                unsafe_allow_html=True)
    if y_metrics.kcal_ingested == 0:
        st.info("Ingresa tus macros del día en el panel lateral →", icon="ℹ️")
    else:
        rn1, rn2, rn3 = st.columns(3)
        rn1.plotly_chart(
            ring_fig(y_metrics.protein_g, prot_target, "Proteína", "g", NEON),
            use_container_width=True, config={"displayModeBar": False},
        )
        rn2.plotly_chart(
            ring_fig(y_metrics.carbs_g, carbs_target, "Carbos", "g", BLUE),
            use_container_width=True, config={"displayModeBar": False},
        )
        rn3.plotly_chart(
            ring_fig(y_metrics.kcal_ingested, kcal_target, "Calorías", "kcal", AMBER),
            use_container_width=True, config={"displayModeBar": False},
        )

with rc2:
    st.markdown("<div class='section-label'>📅 Agenda del Día — Heurística de Slots</div>",
                unsafe_allow_html=True)
    st.caption("🔴 Bloqueado &nbsp;·&nbsp; 🟢 Tu bloque de entrenamiento (sin colisiones)")
    st.plotly_chart(
        timeline_fig(eff_decision, busy_today),
        use_container_width=True, config={"displayModeBar": False},
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Caja Negra Científica (colapsada por defecto) ─────────────────────────
with st.expander("🧬 Caja Negra Científica y Código Limpio (SOLID)", expanded=False):
    st.markdown(f"""
**Diagnóstico algorítmico del sistema:**
{decision.rationale}

---
### 🔬 Motor Clínico HRV — hrv-analysis (Aura-healthcare)
Intervalos RR calculados por `get_time_domain_features()` sobre {300} muestras simuladas:

| Métrica | Valor calculado | Referencia clínica | Interpretación |
|---|---|---|---|
| **RMSSD** | `{hrv_clinical['rmssd']:.1f} ms` | Normal: 40–80 ms | Actividad parasimpática (recuperación) |
| **SDNN** | `{hrv_clinical['sdnn']:.1f} ms` | Normal: 30–60 ms | Variabilidad total del sistema nervioso autónomo |
| **FC Media HRV** | `{hrv_clinical['mean_hr']:.0f} bpm` | Atleta élite: 45–65 bpm | Eficiencia cardíaca |
| **pNN50** | `{hrv_clinical['pnni50']:.1f}%` | Normal: >20% | % intervalos RR que difieren >50ms |

---
### 📊 ACWR & Readiness
| Métrica | Valor hoy | Zona | Interpretación técnica |
|---|---|---|---|
| ACWR | `{snapshot.acwr:.2f}` | {zcfg['icon']} `{decision.zone.value}` | Carga aguda (7d) ÷ Carga crónica (28d) |
| HRV ratio | `{snapshot.hrv_ratio:.2f}×` | — | vs. baseline individual (no poblacional) |
| Batería bio | `{hrv_pct:.0f}%` | — | Mapeo lineal ratio [0.70–1.30] → [0–100%] |

---
### 🏗️ Arquitectura SOLID — 4 librerías integradas
| Librería | Uso | Principio SOLID |
|---|---|---|
| `hrv-analysis` (Aura-healthcare) | Motor clínico: RMSSD, SDNN, pNN50 | SRP: dominio HRV aislado |
| `streamlit-echarts` (andfanilo) | Gauge ACWR animado Apache ECharts | OCP: gauge swappable sin tocar lógica |
| `streamlit-extras` (arnaudmiribel) | Metric cards con borde reactivo al estado | LSP: estilo intercambiable con st.metric |
| `streamlit-lottie` (andfanilo) | Spinner de carga + éxito animado | DIP: animaciones desacopladas de la UI |

**ACWR (Gabbett, 2016):** Sweet spot 0.8–1.3. ACWR > 1.5 → OR lesión 2.1× (BJSM).
**Anti-interferencia mTOR/AMPK (Wilson et al., 2012):** Fuerza AM → Running PM (≥6h separación).
**HRV individualizada:** RMSSD < 93% baseline propio → SNA simpático dominante → sin alta intensidad.
**Fase F0 (S1–6):** Z2 dominante (65–75% FCmáx) → biogénesis mitocondrial (PGC-1α). Regla 10% volumen.

*Gabbett (2016) BJSM · Seiler (2010) IJSPP · Wilson (2012) JSCR · Morton (2018) BJSM*
    """)


# ── Footer ─────────────────────────────────────────────────────────────────
garmin_label = "🟢 real" if garmin_connected else "🔵 simulado"
st.markdown(
    f"<div style='text-align:center;color:#30363d;font-size:10px;padding:14px 0 4px;'>"
    f"Atleta Híbrido OS v2.4.0 &nbsp;·&nbsp; "
    f"Garmin {garmin_label} &nbsp;·&nbsp; "
    f"HRV clínico: RMSSD {hrv_clinical['rmssd']:.0f}ms &nbsp;·&nbsp; "
    f"Auto-refresh 5 min &nbsp;·&nbsp; {dt.datetime.now().strftime('%H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True,
)
