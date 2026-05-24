"""GreenSky 공통 유틸 — 스타일, 데이터 로더"""
import streamlit as st
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent / "data"

# 통합 CSS
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans KR', -apple-system, sans-serif; }
.stApp { background: linear-gradient(180deg, #0a0e1a 0%, #0d1320 100%); color: #e8eaed; }
.main .block-container { padding-top: 2.5rem; max-width: 1280px; }
h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; }
.serif-accent { font-family: 'Cormorant Garamond', serif; font-style: italic; font-weight: 500; color: #6ee7b7; }
.eyebrow { text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.72rem; color: #6ee7b7; font-weight: 500; }
.metric-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(110, 231, 183, 0.15); border-radius: 4px; padding: 1.4rem 1.2rem; margin-bottom: 0.8rem; }
.hero-num { font-family: 'IBM Plex Mono', monospace; font-size: 2.6rem; font-weight: 500; color: #f0f4f8; line-height: 1.0; }
.hero-unit { font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; color: #94a3b8; margin-left: 0.3rem; }
.divider-thin { border: 0; border-top: 1px solid rgba(148, 163, 184, 0.15); margin: 2rem 0; }
.callout { background: rgba(252,211,77,0.04); border-left: 3px solid #fcd34d; padding: 1rem 1.3rem; margin: 1rem 0; }
.callout-good { background: rgba(110,231,183,0.04); border-left: 3px solid #6ee7b7; padding: 1rem 1.3rem; margin: 1rem 0; }
.callout-bad { background: rgba(248,113,113,0.04); border-left: 3px solid #f87171; padding: 1rem 1.3rem; margin: 1rem 0; }
section[data-testid="stSidebar"] { background: #060912; border-right: 1px solid rgba(148, 163, 184, 0.1); }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #6ee7b7; }
.stPlotlyChart { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(148, 163, 184, 0.08); border-radius: 4px; padding: 0.6rem; }
[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace !important; color: #f0f4f8 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.72rem !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] { background: rgba(15, 23, 42, 0.4); border-radius: 2px; color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.1); padding: 0.4rem 1rem; }
.stTabs [aria-selected="true"] { background: rgba(110, 231, 183, 0.08) !important; color: #6ee7b7 !important; border-color: rgba(110, 231, 183, 0.4) !important; }
.stDataFrame { background: rgba(15,23,42,0.4); }
</style>
"""

# Plotly 공통 레이아웃
PLOT_BG = "rgba(15,23,42,0)"
GRID_COLOR = "rgba(148,163,184,0.1)"
TEXT_COLOR = "#cbd5e1"
ACCENT = "#6ee7b7"

def apply_layout(fig, height=420, showlegend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans KR", color=TEXT_COLOR, size=12),
        showlegend=showlegend,
        legend=dict(bgcolor="rgba(15,23,42,0.7)", bordercolor=GRID_COLOR, borderwidth=1, font=dict(size=11)),
        margin=dict(l=50, r=30, t=50, b=50),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
    )
    return fig

def page_header(eyebrow, title, subtitle=None):
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"<span class='eyebrow'>{eyebrow}</span>", unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(
            f"<p style='color:#94a3b8; font-size:1rem; line-height:1.7; margin-top:-0.5rem;'>{subtitle}</p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

def apply_global_style():
    """페이지 단순 스타일 적용 — page_header보다 가벼움"""
    st.markdown(CSS, unsafe_allow_html=True)

def hero_metric(label, value, sub=""):
    """카드형 핵심 메트릭 HTML"""
    return f"""
    <div class='metric-card'>
        <div style='color:#94a3b8; font-size:0.74rem; text-transform:uppercase; letter-spacing:0.1em;'>{label}</div>
        <div class='hero-num' style='font-size:1.6rem; margin-top:0.4rem;'>{value}</div>
        <div style='color:#6ee7b7; font-size:0.78rem; margin-top:0.3rem;'>{sub}</div>
    </div>
    """

def sidebar_nav(active):
    with st.sidebar:
        st.markdown("# 🛫 GreenSky")
        st.markdown("<span class='serif-accent'>Carbon × Cost Co-optimization</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.caption(f"현재: **{active}**")

@st.cache_data
def load_m1():
    return pd.read_excel(DATA / "greensky_module1_v4.xlsx", sheet_name="Sheet1")

@st.cache_data
def load_m2():
    x = pd.ExcelFile(DATA / "greensky_module2_v4.xlsx")
    return {s: pd.read_excel(x, sheet_name=s) for s in x.sheet_names}

@st.cache_data
def load_m3():
    x = pd.ExcelFile(DATA / "greensky_module3_v1.xlsx")
    return {s: pd.read_excel(x, sheet_name=s) for s in x.sheet_names}

@st.cache_data
def load_m4():
    x = pd.ExcelFile(DATA / "greensky_module4_v1.xlsx")
    return {s: pd.read_excel(x, sheet_name=s) for s in x.sheet_names}

@st.cache_data
def load_mops():
    df = pd.read_csv(DATA / "mops_full.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_flights_summary():
    x = pd.ExcelFile(DATA / "flights_summary.xlsx")
    return {s: pd.read_excel(x, sheet_name=s) for s in x.sheet_names}
