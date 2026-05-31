"""
RC Gestion — Plateforme de Gestion Comptable et Fiscale
"""

import io
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import db
import pdf_reports
import ai

st.set_page_config(page_title="RC Gestion", page_icon="", layout="wide", initial_sidebar_state="expanded")
db.init_db()

# ══════════════════════════════════════════════════════════
#  THEMES — IDENTIQUES
# ══════════════════════════════════════════════════════════
if "theme" not in st.session_state:
    st.session_state.theme = "light"

LIGHT = dict(
    bg="#f0f7ff", bg2="#e2f0fb", sidebar="#0c2a4a",
    card="#ffffff", card2="#f5faff",
    border="#c5dff2", border2="#a8cceb",
    text="#0c2a4a", muted="#4a7096", dim="#8aabbf",
    sky="#1e90d4", sky2="#2ba3f0", sky3="#0a70b8",
    sky_bg="rgba(30,144,212,.08)", sky_brd="rgba(30,144,212,.2)",
    green="#0f9060", red="#c0392b", orange="#d4890a", amber="#e6a817",
    tab_active="linear-gradient(135deg,#1e90d4,#0a70b8)",
    btn="linear-gradient(135deg,#1e90d4,#0a70b8)",
    btn_shadow="rgba(30,144,212,.3)",
    hr="#c5dff2", kpi_default="#ffffff",
    chart_bg="rgba(0,0,0,0)", chart_text="#4a7096",
)
DARK = dict(
    bg="#071524", bg2="#0a1e32", sidebar="#050e1a",
    card="#0d2035", card2="#102540",
    border="#1a3a5a", border2="#224870",
    text="#d8eaf8", muted="#6090b8", dim="#2a4060",
    sky="#2ba3f0", sky2="#44b8ff", sky3="#1e90d4",
    sky_bg="rgba(43,163,240,.1)", sky_brd="rgba(43,163,240,.22)",
    green="#1ab87a", red="#e05555", orange="#e0a030", amber="#f0bc30",
    tab_active="linear-gradient(135deg,#2ba3f0,#1e90d4)",
    btn="linear-gradient(135deg,#2ba3f0,#1e90d4)",
    btn_shadow="rgba(43,163,240,.3)",
    hr="#1a3a5a", kpi_default="#0d2035",
    chart_bg="rgba(0,0,0,0)", chart_text="#6090b8",
)

T  = LIGHT if st.session_state.theme == "light" else DARK
LT = st.session_state.theme == "light"
C  = [T["sky"], T["green"], T["amber"], T["red"], "#7c5cbf", "#0aa4b0", "#e07850", "#6a8fa8"]

def CHART():
    return dict(
        paper_bgcolor=T["chart_bg"], plot_bgcolor=T["chart_bg"],
        font=dict(color=T["chart_text"], family="Inter, sans-serif", size=11),
        margin=dict(t=44, b=16, l=6, r=6),
        xaxis=dict(gridcolor=T["border"], linecolor=T["border"]),
        yaxis=dict(gridcolor=T["border"], linecolor=T["border"]),
    )

# ══════════════════════════════════════════════════════════
#  CSS GLOBAL AMELIORE — MEMES COULEURS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', system-ui, sans-serif !important;
    background: {T["bg"]} !important;
}}

/* ── SCROLLBAR STYLISEE ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {T["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {T["sky"]}60; border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T["sky"]}; }}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {T["sidebar"]} !important;
    border-right: 1px solid rgba(43,163,240,.12) !important;
}}
[data-testid="stSidebar"] * {{ color: #7aaccc !important; }}
[data-testid="stSidebar"] strong {{ color: #d8eaf8 !important; }}

/* ── HEADINGS ── */
h1, h2, h3, h4 {{ color: {T["text"]} !important; font-weight: 700 !important; font-family: 'Inter', sans-serif !important; }}
p, .stMarkdown {{ color: {T["muted"]}; }}
[data-testid="stMarkdownContainer"] p {{ color: {T["muted"]}; font-size: .9rem; }}

/* ══════════════════════════════
   ANIMATIONS GLOBALES
══════════════════════════════ */
@keyframes fadeInUp {{
    from {{ opacity:0; transform:translateY(18px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeInLeft {{
    from {{ opacity:0; transform:translateX(-18px); }}
    to   {{ opacity:1; transform:translateX(0); }}
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:.5; transform:scale(1.3); }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -400px 0; }}
    100% {{ background-position: 400px 0; }}
}}
@keyframes float {{
    0%,100% {{ transform:translateY(0px); }}
    50%      {{ transform:translateY(-8px); }}
}}
@keyframes spin-slow {{
    from {{ transform:rotate(0deg); }}
    to   {{ transform:rotate(360deg); }}
}}
@keyframes glow-pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 {T["sky"]}30; }}
    50%      {{ box-shadow: 0 0 20px 6px {T["sky"]}20; }}
}}
@keyframes count-up {{
    from {{ opacity:0; transform:translateY(10px) scale(.95); }}
    to   {{ opacity:1; transform:translateY(0) scale(1); }}
}}
@keyframes gradient-shift {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
@keyframes border-dance {{
    0%   {{ border-color: {T["sky"]}40; }}
    50%  {{ border-color: {T["sky"]}; }}
    100% {{ border-color: {T["sky"]}40; }}
}}

/* ══════════════════════════════
   HERO BANNER AMELIORE
══════════════════════════════ */
.rc-hero {{
    background: {"linear-gradient(135deg, #c8e4f8 0%, #deeefb 30%, #b5d9f5 70%, #c8e4f8 100%)" if LT else "linear-gradient(135deg, #071524 0%, #0c2240 30%, #081c38 70%, #071524 100%)"};
    background-size: 300% 300%;
    animation: gradient-shift 8s ease infinite;
    border: 1px solid {T["border2"]};
    border-radius: 16px;
    padding: 30px 36px;
    margin-bottom: 22px;
    position: relative; overflow: hidden;
}}
.rc-hero::before {{
    content: '';
    position: absolute; top: -50%; right: -8%;
    width: 400px; height: 400px; border-radius: 50%;
    background: radial-gradient(circle, {T["sky"]}22 0%, transparent 65%);
    pointer-events: none; animation: float 6s ease-in-out infinite;
}}
.rc-hero::after {{
    content: '';
    position: absolute; bottom: -30%; left: 5%;
    width: 250px; height: 250px; border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,.12) 0%, transparent 65%);
    pointer-events: none; animation: float 8s ease-in-out infinite reverse;
}}
.rc-hero-inner {{ position: relative; z-index: 1; animation: fadeInLeft .6s ease; }}
.rc-hero-eyebrow {{
    display: inline-flex; align-items: center; gap: 7px;
    background: {T["sky_bg"]}; border: 1px solid {T["sky_brd"]};
    border-radius: 20px; padding: 3px 12px; margin-bottom: 12px;
    font-size: .6rem; font-weight: 700; color: {T["sky"]};
    letter-spacing: 1px; text-transform: uppercase;
}}
.rc-hero-dot {{
    width: 6px; height: 6px; background: {T["sky"]};
    border-radius: 50%; animation: pulse 2s infinite;
}}
.rc-hero-title {{
    font-size: 1.85rem; font-weight: 800;
    color: {T["sky3"]} !important; margin: 0 0 5px;
    letter-spacing: -.4px; line-height: 1.1;
}}
.rc-hero-sub {{ color: {T["muted"]} !important; font-size: .88rem; margin: 0; font-weight: 400; }}
.rc-hero-date {{
    font-size: .62rem; color: {T["dim"]} !important;
    text-transform: uppercase; letter-spacing: 1.2px; margin-top: 14px;
    display: flex; align-items: center; gap: 8px;
}}
.rc-hero-date::before {{
    content: ''; display: inline-block;
    width: 24px; height: 1px; background: {T["sky"]}80;
}}
.rc-hero-line {{
    height: 2px; border-radius: 2px; margin-top: 18px;
    background: linear-gradient(90deg, {T["sky"]}, {T["sky3"]}50, transparent);
    position: relative; overflow: visible;
}}
.rc-hero-line::after {{
    content: ''; position: absolute; left: 0; top: -2px;
    width: 40px; height: 6px; border-radius: 3px;
    background: {T["sky"]}; filter: blur(4px);
    animation: shimmer 2s infinite linear;
}}

/* ══════════════════════════════
   KPI CARDS WOW
══════════════════════════════ */
.kpi-grid  {{ display: grid; gap: 14px; margin-bottom: 20px; }}
.kpi-4     {{ grid-template-columns: repeat(4, 1fr); }}
.kpi-3     {{ grid-template-columns: repeat(3, 1fr); }}
.kpi-2     {{ grid-template-columns: repeat(2, 1fr); }}

.kpi-card {{
    background: {T["kpi_default"]};
    border: 1.5px solid {T["border"]};
    border-radius: 14px; padding: 22px 18px 18px;
    position: relative; overflow: hidden;
    cursor: pointer;
    animation: fadeInUp .5s ease both;
    transition: transform .25s cubic-bezier(.34,1.56,.64,1),
                box-shadow .25s ease,
                border-color .25s ease,
                background .25s ease;
}}
.kpi-card:nth-child(1) {{ animation-delay:.05s; }}
.kpi-card:nth-child(2) {{ animation-delay:.1s; }}
.kpi-card:nth-child(3) {{ animation-delay:.15s; }}
.kpi-card:nth-child(4) {{ animation-delay:.2s; }}

.kpi-card:hover {{
    transform: translateY(-5px) scale(1.015);
    box-shadow: 0 20px 50px {T["btn_shadow"]},
                0 0 0 1px {T["sky"]}30;
    border-color: {T["sky"]};
    background: {"#eef7ff" if LT else "#132a46"};
    animation: border-dance 1.5s ease infinite;
}}
.kpi-card:active {{ transform: translateY(-2px) scale(1.005); }}

/* Barre coloree top */
.kpi-card .kpi-bar {{
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 14px 14px 0 0;
    transition: height .2s ease;
}}
.kpi-card:hover .kpi-bar {{ height: 4px; }}
.kpi-sky   .kpi-bar {{ background: linear-gradient(90deg, {T["sky"]}, {T["sky2"]}); }}
.kpi-green .kpi-bar {{ background: linear-gradient(90deg, {T["green"]}, #30d48a); }}
.kpi-red   .kpi-bar {{ background: linear-gradient(90deg, {T["red"]}, #f07070); }}
.kpi-amber .kpi-bar {{ background: linear-gradient(90deg, {T["amber"]}, #f5cc50); }}
.kpi-neutral .kpi-bar {{ background: {T["border"]}; }}

/* Glow orb */
.kpi-card .kpi-orb {{
    position: absolute; top: -10px; right: -10px;
    width: 70px; height: 70px; border-radius: 50%;
    opacity: .07; filter: blur(14px);
    transition: opacity .2s ease, transform .2s ease;
    pointer-events: none;
}}
.kpi-card:hover .kpi-orb {{ opacity: .14; transform: scale(1.2); }}
.kpi-sky   .kpi-orb {{ background: {T["sky"]}; }}
.kpi-green .kpi-orb {{ background: {T["green"]}; }}
.kpi-red   .kpi-orb {{ background: {T["red"]}; }}
.kpi-amber .kpi-orb {{ background: {T["amber"]}; }}

.kpi-label {{
    font-size: .58rem; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: {T["dim"]}; margin-bottom: 10px;
}}
.kpi-val {{
    font-size: 2.1rem; font-weight: 800;
    color: {T["text"]}; line-height: 1; letter-spacing: -.5px;
    animation: count-up .6s ease both;
    transition: color .2s ease;
}}
.kpi-card:hover .kpi-val {{ color: {T["sky"]} !important; }}
.kpi-sub {{ font-size: .7rem; color: {T["dim"]}; margin-top: 7px; }}

/* Badge tendance */
.kpi-badge {{
    display: inline-flex; align-items: center; gap: 3px;
    font-size: .65rem; font-weight: 700; padding: 2px 8px;
    border-radius: 20px; margin-top: 8px;
}}
.kpi-badge-up   {{ background: rgba(15,144,96,.12); color: {T["green"]}; }}
.kpi-badge-down {{ background: rgba(192,57,43,.12); color: {T["red"]}; }}
.kpi-badge-neu  {{ background: {T["sky_bg"]}; color: {T["sky"]}; }}

/* ══════════════════════════════
   SECTION TITLES AMELIORES
══════════════════════════════ */
.rc-sec {{
    font-size: .6rem; font-weight: 700; color: {T["sky"]} !important;
    text-transform: uppercase; letter-spacing: 1.4px;
    margin: 26px 0 14px; padding-bottom: 9px;
    border-bottom: 1.5px solid {T["border"]};
    display: flex; align-items: center; gap: 9px;
    animation: fadeInLeft .4s ease;
}}
.rc-sec::before {{
    content: ''; width: 3px; height: 14px;
    background: linear-gradient(180deg, {T["sky"]}, {T["sky3"]});
    border-radius: 3px; flex-shrink: 0;
}}
.rc-sec::after {{
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, {T["border"]}, transparent);
}}

/* ══════════════════════════════
   ALERT CARDS AMELIOREES
══════════════════════════════ */
.al-red {{
    background: {"rgba(192,57,43,.05)" if LT else "rgba(220,38,38,.08)"};
    border: 1px solid {"rgba(192,57,43,.15)" if LT else "rgba(220,38,38,.2)"};
    border-left: 3px solid {T["red"]};
    border-radius: 10px; padding: 12px 16px; margin: 5px 0;
    animation: fadeInUp .3s ease;
    transition: transform .15s ease, box-shadow .15s ease;
}}
.al-red:hover {{ transform: translateX(3px); box-shadow: -3px 0 0 {T["red"]}; }}
.al-warn {{
    background: {"rgba(212,137,10,.05)" if LT else "rgba(217,119,6,.08)"};
    border: 1px solid {"rgba(212,137,10,.15)" if LT else "rgba(217,119,6,.2)"};
    border-left: 3px solid {T["amber"]};
    border-radius: 10px; padding: 12px 16px; margin: 5px 0;
    animation: fadeInUp .3s ease;
    transition: transform .15s ease, box-shadow .15s ease;
}}
.al-warn:hover {{ transform: translateX(3px); box-shadow: -3px 0 0 {T["amber"]}; }}
.al-ok {{
    background: {T["sky_bg"]};
    border: 1px solid {T["sky_brd"]};
    border-left: 3px solid {T["sky"]};
    border-radius: 10px; padding: 12px 16px; margin: 5px 0;
    animation: fadeInUp .3s ease;
    transition: transform .15s ease;
}}
.al-ok:hover {{ transform: translateX(3px); }}
.al-title {{ font-size: .86rem; font-weight: 600; margin: 0 0 3px; }}
.al-sub   {{ font-size: .75rem; color: {T["muted"]}; margin: 0; }}

/* ══════════════════════════════
   INPUTS AMELIORES
══════════════════════════════ */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea>div>textarea,
.stSelectbox>div>div>div,
.stDateInput>div>div>input {{
    background: {"#f5faff" if LT else "#0a1e32"} !important;
    border: 1.5px solid {T["border"]} !important;
    border-radius: 9px !important;
    color: {T["text"]} !important;
    font-size: .875rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>textarea:focus {{
    border-color: {T["sky"]} !important;
    box-shadow: 0 0 0 3px {T["sky_bg"]}, 0 2px 8px {T["sky"]}15 !important;
    outline: none !important;
}}
label {{ color: {T["muted"]} !important; font-size: .82rem !important; font-weight: 500 !important; }}

/* ══════════════════════════════
   BUTTONS AMELIORES
══════════════════════════════ */
.stButton>button {{
    background: {T["btn"]} !important;
    color: #fff !important; border: none !important;
    border-radius: 9px !important; font-weight: 600 !important;
    font-size: .86rem !important; letter-spacing: .2px !important;
    box-shadow: 0 3px 14px {T["btn_shadow"]} !important;
    transition: all .2s cubic-bezier(.34,1.2,.64,1) !important;
    position: relative !important; overflow: hidden !important;
}}
.stButton>button::before {{
    content: '' !important;
    position: absolute !important; top: 0 !important; left: -100% !important;
    width: 100% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.15), transparent) !important;
    transition: left .4s ease !important;
}}
.stButton>button:hover {{
    filter: brightness(1.12) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px {T["btn_shadow"]} !important;
}}
.stButton>button:hover::before {{ left: 100% !important; }}
.stButton>button:active {{ transform: translateY(0) !important; }}

.stDownloadButton>button {{
    background: linear-gradient(135deg, #1ab87a, #12a066) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 9px !important; font-weight: 700 !important;
    font-size: .88rem !important; letter-spacing: .3px !important;
    text-shadow: 0 1px 3px rgba(0,0,0,.25) !important;
    box-shadow: 0 3px 14px rgba(15,144,96,.3) !important;
    transition: all .2s ease !important;
}}
.stDownloadButton>button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(15,144,96,.45) !important;
    background: linear-gradient(135deg, #22d48e, #16b878) !important;
}}

/* ══════════════════════════════
   TABS AMELIORES
══════════════════════════════ */
[data-baseweb="tab-list"] {{
    background: {T["card"]} !important;
    border-radius: 11px !important; padding: 4px !important;
    border: 1.5px solid {T["border"]} !important; gap: 3px !important;
    box-shadow: {"0 2px 8px rgba(30,144,212,.06)" if LT else "none"};
}}
[data-baseweb="tab"] {{
    border-radius: 8px !important; color: {T["muted"]} !important;
    font-weight: 500 !important; font-size: .84rem !important;
    transition: all .2s ease !important;
}}
[data-baseweb="tab"]:hover {{ color: {T["sky"]} !important; background: {T["sky_bg"]} !important; }}
[aria-selected="true"] {{
    background: {T["tab_active"]} !important;
    color: #fff !important; font-weight: 700 !important;
    box-shadow: 0 2px 10px {T["btn_shadow"]} !important;
}}

/* ══════════════════════════════
   EXPANDER AMELIORE
══════════════════════════════ */
[data-testid="stExpander"] {{
    background: {T["card"]} !important;
    border: 1.5px solid {T["border"]} !important;
    border-radius: 12px !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"]:hover {{
    border-color: {T["sky"]}60 !important;
    box-shadow: 0 4px 20px {T["btn_shadow"]}20 !important;
}}

/* ══════════════════════════════
   METRICS AMELIORES
══════════════════════════════ */
[data-testid="metric-container"] {{
    background: {T["card"]} !important;
    border: 1.5px solid {T["border"]};
    border-radius: 12px; padding: 16px 18px;
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    animation: fadeInUp .4s ease;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px {T["btn_shadow"]}20;
    border-color: {T["sky"]}50;
}}
[data-testid="stMetricValue"] {{ color: {T["sky"]} !important; font-weight: 800 !important; }}
[data-testid="stMetricLabel"] {{ color: {T["muted"]} !important; font-size: .78rem !important; font-weight: 500 !important; }}

/* ══════════════════════════════
   FORM
══════════════════════════════ */
[data-testid="stForm"] {{
    border: 1.5px solid {T["border"]} !important;
    border-radius: 14px !important; padding: 22px !important;
    background: {T["card"]} !important;
    box-shadow: {"0 4px 20px rgba(30,144,212,.05)" if LT else "none"} !important;
    animation: fadeInUp .4s ease !important;
}}

/* ══════════════════════════════
   DATAFRAME AMELIORE
══════════════════════════════ */
[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; animation: fadeInUp .5s ease; }}

/* ══════════════════════════════
   PROGRESS BAR
══════════════════════════════ */
.stProgress>div>div>div>div {{
    background: linear-gradient(90deg, {T["sky"]}, {T["sky2"]}, {T["sky"]}) !important;
    background-size: 200% 100% !important;
    animation: shimmer 2s infinite linear !important;
    border-radius: 10px !important;
}}

/* ══════════════════════════════
   SLIDER
══════════════════════════════ */
.stSlider [data-baseweb="slider"] {{
    color: {T["sky"]} !important;
}}

hr {{ border-color: {T["hr"]} !important; opacity: .4; margin: 16px 0; }}

/* ══════════════════════════════
   SIDEBAR AMELIOREE
══════════════════════════════ */
.sb-head {{
    padding: 20px 14px 14px;
    border-bottom: 1px solid rgba(43,163,240,.1);
    display: flex; align-items: center; gap: 11px;
}}
.sb-logo-wrap {{
    position: relative; flex-shrink: 0;
}}
.sb-icon {{
    width: 40px; height: 40px; border-radius: 10px;
    background: linear-gradient(135deg, {T["sky"]}, {T["sky3"]});
    display: flex; align-items: center; justify-content: center;
    font-size: .9rem; font-weight: 800; color: #fff;
    box-shadow: 0 4px 14px {T["sky"]}50;
    animation: glow-pulse 3s ease infinite;
}}
.sb-name   {{ font-size: .95rem; font-weight: 800; color: #e2eaf8 !important; letter-spacing: -.2px; }}
.sb-sub    {{ font-size: .57rem; color: {T["sky"]} !important; text-transform: uppercase; letter-spacing: .8px; margin-top: 2px; }}
.sb-user   {{
    margin: 10px 12px 0;
    background: rgba(43,163,240,.07); border: 1px solid rgba(43,163,240,.12);
    border-radius: 9px; padding: 9px 12px; font-size: .73rem;
    display: flex; align-items: center; gap: 8px;
}}
.sb-user-dot {{
    width: 8px; height: 8px; background: {T["green"]};
    border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 6px {T["green"]};
    animation: pulse 2s infinite;
}}
.sb-nav-lbl {{
    font-size: .56rem; font-weight: 700; color: {T["sky"]} !important;
    text-transform: uppercase; letter-spacing: 1.3px;
    padding: 14px 14px 5px;
}}
.sb-stat-block {{
    padding: 10px 14px 6px; border-top: 1px solid rgba(43,163,240,.08); margin-top: 4px;
}}
.sb-stat-lbl {{
    font-size: .55rem; font-weight: 700; color: {T["sky"]} !important;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
}}
.sb-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 0; border-bottom: 1px solid rgba(26,58,90,.4); font-size: .72rem;
}}
.sb-ver {{
    text-align: center; font-size: .55rem; color: rgba(43,163,240,.2) !important;
    padding: 10px 0 4px; text-transform: uppercase; letter-spacing: .6px;
}}

/* ══════════════════════════════
   INFO CARDS CLIENT
══════════════════════════════ */
.info-grid {{
    display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 14px;
}}
.info-card {{
    background: {T["card"]}; border: 1.5px solid {T["border"]};
    border-radius: 12px; padding: 16px 18px;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
    animation: fadeInUp .4s ease both;
}}
.info-card:hover {{
    transform: translateY(-3px);
    border-color: {T["sky"]}60;
    box-shadow: 0 8px 24px {T["btn_shadow"]}15;
}}
.info-lbl {{
    font-size: .57rem; font-weight: 700; color: {T["dim"]};
    text-transform: uppercase; letter-spacing: 1.1px; margin-bottom: 6px;
}}
.info-val {{ font-size: .95rem; font-weight: 600; color: {T["text"]}; }}
.info-val.hl {{ color: {T["sky"]}; }}

/* ══════════════════════════════
   NOTIFICATION BADGE
══════════════════════════════ */
.notif-badge {{
    display: inline-flex; align-items: center; justify-content: center;
    background: {T["red"]}; color: #fff;
    font-size: .6rem; font-weight: 700;
    width: 18px; height: 18px; border-radius: 50%;
    margin-left: 6px; animation: pulse 2s infinite;
}}

/* ══════════════════════════════
   STATS BANNER
══════════════════════════════ */
.stats-banner {{
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 1px; background: {T["border"]};
    border-radius: 12px; overflow: hidden;
    margin: 14px 0; border: 1.5px solid {T["border"]};
}}
.stats-banner-item {{
    background: {T["card"]}; padding: 14px 16px; text-align: center;
    transition: background .2s ease;
}}
.stats-banner-item:hover {{ background: {"#eef7ff" if LT else "#132a46"}; }}
.stats-banner-val {{
    font-size: 1.4rem; font-weight: 800; color: {T["sky"]};
    animation: count-up .5s ease;
}}
.stats-banner-lbl {{
    font-size: .58rem; color: {T["dim"]}; text-transform: uppercase;
    letter-spacing: .8px; margin-top: 3px; font-weight: 600;
}}

/* ══════════════════════════════
   LOGIN GLASSMORPHISM
══════════════════════════════ */
.login-bg {{
    position: fixed; top:0; left:0; right:0; bottom:0;
    background: linear-gradient(145deg, #7dd3f8 0%, #4ab8f0 35%, #2090d8 65%, #1070c0 100%);
    z-index: 0; pointer-events: none;
}}
.login-bg-orb1 {{
    position: fixed; top: 15%; left: 10%; width: 300px; height: 300px;
    border-radius: 50%; background: rgba(255,255,255,.15); filter: blur(40px);
    pointer-events: none; z-index: 0; animation: float 6s ease-in-out infinite;
}}
.login-bg-orb2 {{
    position: fixed; bottom: 20%; right: 10%; width: 250px; height: 250px;
    border-radius: 50%; background: rgba(30,144,212,.2); filter: blur(50px);
    pointer-events: none; z-index: 0; animation: float 8s ease-in-out infinite reverse;
}}
.login-cloud1 {{
    position: fixed; top: 10%; left: 5%; width: 280px; height: 100px;
    border-radius: 60px; background: rgba(255,255,255,.2); filter: blur(1px);
    pointer-events: none; z-index: 0;
}}
.login-cloud2 {{
    position: fixed; top: 60%; right: 8%; width: 200px; height: 80px;
    border-radius: 50px; background: rgba(255,255,255,.15); filter: blur(1px);
    pointer-events: none; z-index: 0;
}}
.login-cloud3 {{
    position: fixed; bottom: 18%; left: 22%; width: 160px; height: 65px;
    border-radius: 40px; background: rgba(255,255,255,.12); filter: blur(1px);
    pointer-events: none; z-index: 0;
}}
.login-card {{
    background: rgba(255,255,255,.58);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255,255,255,.75);
    border-radius: 20px; padding: 38px 34px 30px;
    box-shadow: 0 10px 50px rgba(10,80,180,.2), 0 1px 0 rgba(255,255,255,.85) inset;
    position: relative; z-index: 1; text-align: center;
    animation: fadeInUp .6s cubic-bezier(.34,1.2,.64,1);
}}
.login-card::before {{
    content: ''; position: absolute; top: -1px; left: 20%; right: 20%; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.9), transparent);
    border-radius: 2px;
}}
.login-avatar {{
    width: 66px; height: 66px;
    background: linear-gradient(135deg, #1e90d4, #0a70b8);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px;
    box-shadow: 0 6px 24px rgba(10,80,180,.35), 0 0 0 4px rgba(255,255,255,.5);
    animation: glow-pulse 3s ease infinite;
}}
.login-avatar-svg {{ width: 30px; height: 30px; fill: #fff; }}
.login-title {{
    font-size: 1.25rem; font-weight: 800;
    color: #0c2a4a; margin: 0 0 22px;
    font-family: 'Inter', sans-serif;
    letter-spacing: -.2px;
}}
.login-hint {{
    font-size: .65rem; color: rgba(12,42,74,.5);
    margin-top: 16px; padding-top: 13px;
    border-top: 1px solid rgba(255,255,255,.5);
    line-height: 1.8;
}}

/* ══════════════════════════════
   ETAPES CREATION
══════════════════════════════ */
.etape-item {{
    text-align: center; font-size: .6rem; padding: 8px 4px;
    border-radius: 8px; transition: background .2s ease;
}}
.etape-item:hover {{ background: {T["sky_bg"]}; }}
.etape-done   {{ color: {T["green"]}; font-weight: 700; }}
.etape-active {{ color: {T["sky"]};  font-weight: 600; }}
.etape-wait   {{ color: {T["dim"]};  font-weight: 400; }}
.etape-block  {{ color: {T["red"]};  font-weight: 700; }}

/* ══════════════════════════════
   RADIO BUTTONS
══════════════════════════════ */
.stRadio > div {{ gap: 10px !important; }}
.stRadio > div > label {{
    background: {T["card"]} !important;
    border: 1.5px solid {T["border"]} !important;
    border-radius: 8px !important; padding: 8px 16px !important;
    transition: all .2s ease !important;
    cursor: pointer !important;
}}
.stRadio > div > label:hover {{
    border-color: {T["sky"]} !important;
    background: {T["sky_bg"]} !important;
}}

/* ══════════════════════════════
   SLIDER AMELIORE
══════════════════════════════ */
[data-testid="stSlider"] {{
    padding: 8px 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  USERS & CONSTANTS
# ══════════════════════════════════════════════════════════
USERS = {
    "admin":     {"password":"admin123",  "role":"admin",     "label":"Administrateur","client_id":None},
    "comptable": {"password":"compta456", "role":"comptable", "label":"Comptable",      "client_id":None},
    "client":    {"password":"client789", "role":"client",    "label":"Client",          "client_id":1},
}
MODES=["Annuel","Trimestriel","Mensuel"]
STATUTS_CLI=["Actif","Inactif","Suspendu"]
FORMES_JUR=["SARL","SA","SNC","SCS","Auto-Entrepreneur","Personne Physique"]
SECTEURS=["Commerce","Transport","Industrie","BTP","Immobilier","Artisanat","Agriculture","Services","Formation","Restauration","Autre"]
TYPES_DECL=["TVA","IS","IR","CNSS","Patente","Taxe Professionnelle"]
STATUTS_DECL=["Deposee","En attente","En retard","Annulee"]
TYPES_PIECE=["Facture Vente","Facture Achat","Recu","Note de Debit","Note de Credit","OD"]
REGIMES=["RNR","RF","Auto-Entrepreneur"]
ETAPES_STAT=["En cours","Terminee","En attente","Bloquee"]
TVA_TAUX=[0,7,10,14,20]
VILLES=["El Kelaa des Sraghna","Marrakech","Casablanca","Rabat","Fes","Meknes","Tanger","Agadir","Autre"]

# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def fmt(n):
    try: return f"{float(n):,.2f} MAD"
    except: return "0.00 MAD"

def excel_bytes(df,sheet="Donnees"):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w: df.to_excel(w,index=False,sheet_name=sheet)
    return buf.getvalue()

def section(t):
    st.markdown(f'<div class="rc-sec">{t}</div>',unsafe_allow_html=True)

def client_opts():
    df=db.get_clients()
    if df.empty: return {}
    return {db.client_label(r):r["id"] for _,r in df.iterrows()}

def get_role(): return st.session_state.get("role","client")

def safe_date(d):
    try: return datetime.strptime(str(d),"%Y-%m-%d").date()
    except: return None

def kpi_row(items,cols=4,animate_delay=0):
    cls=f"kpi-{cols}" if cols in (2,3,4) else "kpi-4"
    inner=""
    for i,it in enumerate(items):
        val=it.get("val","0"); lbl=it.get("label","")
        color=it.get("color","neutral"); sub=it.get("sub","")
        badge=it.get("badge",""); badge_type=it.get("badge_type","neu")
        sub_h=f'<div class="kpi-sub">{sub}</div>' if sub else ""
        badge_h=f'<div class="kpi-badge kpi-badge-{badge_type}">{badge}</div>' if badge else ""
        inner+=(f'<div class="kpi-card kpi-{color}" style="animation-delay:{animate_delay+i*.05}s">'
                f'<div class="kpi-bar"></div><div class="kpi-orb"></div>'
                f'<div class="kpi-label">{lbl}</div>'
                f'<div class="kpi-val">{val}</div>'
                f'{sub_h}{badge_h}</div>')
    st.markdown(f'<div class="kpi-grid {cls}">{inner}</div>',unsafe_allow_html=True)

def al_danger(title,sub=""):
    sh=f'<p class="al-sub">{sub}</p>' if sub else ""
    st.markdown(f'<div class="al-red"><p class="al-title" style="color:{T["red"]}">{title}</p>{sh}</div>',unsafe_allow_html=True)

def al_warn(title,sub=""):
    sh=f'<p class="al-sub">{sub}</p>' if sub else ""
    st.markdown(f'<div class="al-warn"><p class="al-title" style="color:{T["amber"]}">{title}</p>{sh}</div>',unsafe_allow_html=True)

def al_ok(title,sub=""):
    sh=f'<p class="al-sub">{sub}</p>' if sub else ""
    st.markdown(f'<div class="al-ok"><p class="al-title" style="color:{T["sky"]}">{title}</p>{sh}</div>',unsafe_allow_html=True)

def stats_banner(items):
    """Banniere de stats en ligne (4 items)."""
    inner="".join([
        f'<div class="stats-banner-item"><div class="stats-banner-val">{it["val"]}</div><div class="stats-banner-lbl">{it["lbl"]}</div></div>'
        for it in items])
    st.markdown(f'<div class="stats-banner">{inner}</div>',unsafe_allow_html=True)

def hero(title,sub,eyebrow="Plateforme Active",show_line=True):
    line_h='<div class="rc-hero-line"></div>' if show_line else ""
    st.markdown(f"""
    <div class="rc-hero">
      <div class="rc-hero-inner">
        <div class="rc-hero-eyebrow"><div class="rc-hero-dot"></div>{eyebrow}</div>
        <div class="rc-hero-title">{title}</div>
        <div class="rc-hero-sub">{sub}</div>
        <div class="rc-hero-date">{datetime.now().strftime('%d %B %Y')}</div>
        {line_h}
      </div>
    </div>""",unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div class="login-bg"></div>
    <div class="login-bg-orb1"></div>
    <div class="login-bg-orb2"></div>
    <div class="login-cloud1"></div>
    <div class="login-cloud2"></div>
    <div class="login-cloud3"></div>
    """,unsafe_allow_html=True)
    st.markdown("<br><br>",unsafe_allow_html=True)
    _,col,_=st.columns([1,.88,1])
    with col:
        st.markdown(f"""
        <div class="login-card">
          <div class="login-avatar">
            <svg class="login-avatar-svg" viewBox="0 0 24 24">
              <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
            </svg>
          </div>
          <div class="login-title">User Login</div>
        </div>
        """,unsafe_allow_html=True)
        st.markdown("""
        <style>
        .stTextInput>div>div>input {
            background: rgba(255,255,255,.72) !important;
            border: 1.5px solid rgba(255,255,255,.88) !important;
            border-radius: 10px !important; color: #0c2a4a !important;
            font-size: .9rem !important;
            box-shadow: 0 2px 10px rgba(10,80,180,.08) !important;
            transition: all .2s ease !important;
        }
        .stTextInput>div>div>input:focus {
            border-color: rgba(30,144,212,.7) !important;
            box-shadow: 0 0 0 3px rgba(30,144,212,.18) !important;
        }
        .stTextInput>div>div>input::placeholder { color: rgba(30,80,140,.4) !important; }
        label { color: rgba(12,42,74,0) !important; height: 0 !important; }
        .stButton>button {
            background: linear-gradient(135deg, #1e90d4, #0a70b8) !important;
            border-radius: 25px !important; font-size: .92rem !important;
            letter-spacing: .3px !important;
            box-shadow: 0 5px 20px rgba(10,80,180,.4) !important;
        }
        .stButton>button:hover { filter: brightness(1.08) !important; transform: translateY(-2px) !important; }
        </style>
        """,unsafe_allow_html=True)
        with st.form("login_form"):
            username=st.text_input("",placeholder="Username",key="li_u")
            password=st.text_input("",type="password",placeholder="Password",key="li_p")
            st.markdown(f'<div style="text-align:right;margin:-6px 0 12px;"><span style="font-size:.72rem;color:rgba(12,42,74,.45);cursor:pointer;transition:color .2s;">Forgot Password?</span></div>',unsafe_allow_html=True)
            if st.form_submit_button("Login",use_container_width=True):
                u=USERS.get(username)
                if u and u["password"]==password:
                    st.session_state.update({"logged_in":True,"username":username,"role":u["role"],"role_label":u["label"],"client_id":u.get("client_id")})
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
        st.markdown(f'<div style="text-align:center;margin-top:12px;font-size:.67rem;color:rgba(255,255,255,.72);text-shadow:0 1px 3px rgba(0,0,0,.2);line-height:1.9;">admin / admin123 &nbsp;·&nbsp; comptable / compta456 &nbsp;·&nbsp; client / client789</div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 1 — TABLEAU DE BORD
# ══════════════════════════════════════════════════════════
def page_dashboard():
    r=get_role()

    # ── VUE CLIENT ──
    if r=="client":
        cid=st.session_state.get("client_id")
        if not cid: al_warn("Aucun dossier associe. Contactez votre bureau."); return
        row=db.get_client(cid)
        if not row: al_warn("Dossier introuvable. Contactez votre bureau."); return
        nom=row.get("raison_sociale") or f"{row.get('prenom','')} {row.get('nom','')}".strip()
        hero("Etat de Votre Dossier",f"{nom} — RC Gestion · El Kelaa des Sraghna","Dossier Client")

        section("Informations du Dossier")
        st.markdown(f"""
        <div class="info-grid">
          <div class="info-card" style="animation-delay:.05s">
            <div class="info-lbl">Type de Personne</div>
            <div class="info-val hl">{row.get("type_personne","—")}</div>
          </div>
          <div class="info-card" style="animation-delay:.1s">
            <div class="info-lbl">Statut du Dossier</div>
            <div class="info-val hl">{row.get("statut","—")}</div>
          </div>
          <div class="info-card" style="animation-delay:.15s">
            <div class="info-lbl">Mode de Declaration</div>
            <div class="info-val">{row.get("mode_declaration","—")}</div>
          </div>
          <div class="info-card" style="animation-delay:.2s">
            <div class="info-lbl">Registre de Commerce (RC)</div>
            <div class="info-val {"hl" if row.get("rc") else ""}">{row.get("rc") or "Non renseigne"}</div>
          </div>
          <div class="info-card" style="animation-delay:.25s">
            <div class="info-lbl">Identifiant Fiscal (IF)</div>
            <div class="info-val {"hl" if row.get("if_fiscal") else ""}">{row.get("if_fiscal") or "Non renseigne"}</div>
          </div>
          <div class="info-card" style="animation-delay:.3s">
            <div class="info-lbl">ICE</div>
            <div class="info-val {"hl" if row.get("ice") else ""}">{row.get("ice") or "Non renseigne"}</div>
          </div>
        </div>""",unsafe_allow_html=True)

        if row.get("secteur_activite"):
            al_ok(f"Secteur : {row.get('secteur_activite','—')} · Ville : {row.get('ville','—')} · Regime : {row.get('regime_fiscal','—')}")

        section("Etat de vos Declarations Fiscales")
        df_all=db.get_declarations()
        if df_all.empty or "client_id" not in df_all.columns:
            al_ok("Aucune declaration enregistree pour ce dossier.")
        else:
            df_cli=df_all[df_all["client_id"]==cid].copy()
            if df_cli.empty:
                al_ok("Aucune declaration pour ce dossier.")
            else:
                nb_ret=int((df_cli["statut"]=="En retard").sum())
                nb_dep=int((df_cli["statut"]=="Deposee").sum())
                nb_att=int((df_cli["statut"]=="En attente").sum())
                kpi_row([
                    {"val":len(df_cli),"label":"Total Declarations","color":"sky",   "sub":"Enregistrees","badge":"Actif","badge_type":"neu"},
                    {"val":nb_dep,      "label":"Deposees",          "color":"green", "sub":"Conformes",   "badge":"OK","badge_type":"up"},
                    {"val":nb_att,      "label":"En Attente",        "color":"amber", "sub":"A traiter"},
                    {"val":nb_ret,      "label":"En Retard","color":"red" if nb_ret else "neutral","sub":"Urgent" if nb_ret else "Aucun","badge":"Urgent" if nb_ret else "","badge_type":"down"},
                ],cols=4)
                if nb_ret>0:
                    al_danger(f"{nb_ret} declaration(s) en retard","Contactez votre comptable pour regulariser votre situation fiscale.")
                dcols=[c for c in ["type_decl","annee","periode","statut","montant_du","montant_paye","date_echeance"] if c in df_cli.columns]
                ren={"type_decl":"Type","annee":"Annee","periode":"Periode","statut":"Statut","montant_du":"Montant Du","montant_paye":"Montant Paye","date_echeance":"Echeance"}
                st.dataframe(df_cli[dcols].rename(columns=ren),use_container_width=True,hide_index=True)
                st.markdown(f'<div style="margin-top:12px;padding:11px 14px;background:{T["sky_bg"]};border:1px solid {T["sky_brd"]};border-radius:10px;font-size:.8rem;color:{T["muted"]};animation:fadeInUp .4s ease">Pour toute question : <strong style="color:{T["sky"]}">RC Gestion · El Kelaa des Sraghna</strong></div>',unsafe_allow_html=True)
        return

    # ── VUE ADMIN / COMPTABLE ──
    hero("RC Gestion","Plateforme de Gestion Comptable, Fiscale et Sociale · El Kelaa des Sraghna")

    c1,c2=st.columns(2)
    with c1:
        if st.button("Charger donnees de demonstration",use_container_width=True):
            db.seed_demo(); st.success("Donnees chargees."); st.rerun()
    with c2:
        if st.button("Actualiser le tableau de bord",use_container_width=True): st.rerun()

    s=db.get_stats()
    taux=round(s.get("montant_paye",0)/s["montant_du"]*100,1) if s.get("montant_du",0)>0 else 0

    # Banniere de stats rapides
    stats_banner([
        {"val":s["total_clients"], "lbl":"Total Clients"},
        {"val":s["actifs"],         "lbl":"Clients Actifs"},
        {"val":s["decl_total"],     "lbl":"Declarations"},
        {"val":f"{taux}%",          "lbl":"Recouvrement"},
    ])

    section("Portefeuille Clients")
    kpi_row([
        {"val":s["total_clients"], "label":"Total Clients",      "color":"sky",    "sub":f"{s['actifs']} actifs","badge":f"+{s['actifs']}","badge_type":"up"},
        {"val":s["pp"],             "label":"Personnes Physiques","color":"neutral","sub":"Dossiers individuels"},
        {"val":s["pm"],             "label":"Personnes Morales",  "color":"neutral","sub":"Societes"},
        {"val":s["actifs"],         "label":"Clients Actifs",     "color":"green",  "sub":f"{s['total_clients']-s['actifs']} inactifs"},
    ],cols=4)

    section("Activite Fiscale")
    rc="red" if s["decl_retard"]>0 else "green"
    kpi_row([
        {"val":s["decl_total"],                "label":"Declarations",  "color":"sky",  "sub":"Total enregistrees"},
        {"val":s["decl_retard"],               "label":"En Retard",     "color":rc,     "sub":"A regulariser","badge":"Urgent" if s["decl_retard"]>0 else "","badge_type":"down"},
        {"val":f"{s.get('montant_du',0):,.0f}","label":"Total Du (MAD)","color":"amber","sub":f"Recouvrement {taux}%"},
        {"val":s["creations"],                 "label":"Creations",     "color":"neutral","sub":"En cours"},
    ],cols=4)

    # ── SECTION IA — ALERTES INTELLIGENTES ──
    section("Intelligence Artificielle — Alertes Predictives")
    with st.spinner("Analyse IA en cours..."):
        anomalies = ai.detecter_anomalies_declarations()
        if anomalies is not None and not anomalies.empty:
            al_danger(f"IA : {len(anomalies)} declaration(s) avec montant anormal detecte(s)",
                      "Le modele Isolation Forest a detecte des valeurs statistiquement inhabituelles.")
            st.dataframe(anomalies, use_container_width=True, hide_index=True)
        else:
            al_ok("IA : Aucune anomalie detectee dans les montants des declarations.")

        df_all_c = db.get_clients(statut="Actif")
        if not df_all_c.empty:
            risques = []
            for _, cli in df_all_c.iterrows():
                for type_d in ["TVA","IS","IR"]:
                    r = ai.predire_risque_retard(cli["id"], type_d)
                    if r is not None and r >= 0.6:
                        nom = cli.get("raison_sociale") or f"{cli.get('prenom','')} {cli.get('nom','')}".strip()
                        risques.append({"Client": nom, "Type": type_d, "Risque": f"{int(r*100)}%"})
            if risques:
                al_warn(f"IA : {len(risques)} risque(s) de retard predits (>60% de probabilite)",
                        "Recommandation : relancer ces clients avant l'echeance.")
                st.dataframe(pd.DataFrame(risques), use_container_width=True, hide_index=True)
            else:
                al_ok("IA : Aucun risque de retard eleve detecte parmi les clients actifs.")

    if s["decl_retard"]>0:
        section("Declarations en Retard")
        df_r=db.get_declarations(statut="En retard")
        if not df_r.empty:
            for _,row in df_r.head(5).iterrows():
                al_danger(f"{row.get('type_decl','')} — {row.get('client_label',row.get('client_id',''))}",f"Echeance : {row.get('date_echeance','—')} · {row.get('montant_du',0):,.0f} MAD")

    df_c=db.get_clients()
    section("Analyse du Portefeuille")
    g1,g2,g3=st.columns(3)
    with g1:
        if not df_c.empty:
            grp=df_c.groupby("type_personne").size().reset_index(name="nb")
            fig=go.Figure(go.Pie(labels=grp["type_personne"],values=grp["nb"],hole=.58,
                marker_colors=[T["sky"],"#5a80b8"],
                hovertemplate="<b>%{label}</b><br>%{value} clients<br>%{percent}<extra></extra>"))
            fig.update_layout(title=dict(text="Repartition par Type",font=dict(color=T["text"])),
                              **CHART(),legend=dict(font=dict(color=T["muted"])))
            st.plotly_chart(fig,use_container_width=True)
    with g2:
        monthly=db.get_clients_par_mois()
        if not monthly.empty:
            fig2=px.bar(monthly,x="mois",y="nb",color="type_personne",title="Inscriptions par Mois",
                barmode="stack",color_discrete_map={"Physique":T["sky"],"Morale":"#5a80b8"})
            fig2.update_layout(**CHART(),title=dict(font=dict(color=T["text"])),legend=dict(font=dict(color=T["muted"])))
            st.plotly_chart(fig2,use_container_width=True)
    with g3:
        df_dt=db.get_decl_par_type()
        if not df_dt.empty:
            grp3=df_dt.groupby("type_decl")["nb"].sum().reset_index()
            fig3=px.bar(grp3,x="type_decl",y="nb",title="Declarations par Type",color="type_decl",color_discrete_sequence=C)
            fig3.update_layout(**CHART(),showlegend=False,title=dict(font=dict(color=T["text"])))
            st.plotly_chart(fig3,use_container_width=True)

    section("Derniers Dossiers")
    if not df_c.empty:
        cols=["type_personne","nom","prenom","raison_sociale","cin","rc","if_fiscal","mode_declaration","statut","date_creation"]
        ren={"type_personne":"Type","nom":"Nom","prenom":"Prenom","raison_sociale":"Raison Sociale","cin":"CIN","rc":"RC","if_fiscal":"IF","mode_declaration":"Mode","statut":"Statut","date_creation":"Date"}
        st.dataframe(df_c[cols].rename(columns=ren).tail(8).iloc[::-1],use_container_width=True,hide_index=True)


# ══════════════════════════════════════════════════════════
#  PAGE 2 — CLIENTS
# ══════════════════════════════════════════════════════════
def page_clients():
    hero("Gestion des Dossiers Clients","Personnes Physiques et Morales","Dossiers")
    tab_add,tab_pp,tab_pm,tab_edit=st.tabs(["Nouveau Dossier","Personnes Physiques","Personnes Morales","Modifier / Supprimer"])

    with tab_add:
        tc=st.radio("Type de Personne",["Personne Physique","Personne Morale"],horizontal=True)
        is_pp="Physique" in tc
        with st.form("fac",clear_on_submit=True):
            section("Identite")
            if is_pp:
                a1,a2=st.columns(2); nom=a1.text_input("Nom *"); prenom=a2.text_input("Prenom *")
                a3,a4=st.columns(2); cin=a3.text_input("CIN *"); patente=a4.text_input("N Patente")
                rs=fj=""; capital=0.0
            else:
                a1,a2=st.columns(2); rs=a1.text_input("Raison Sociale *"); fj=a2.selectbox("Forme Juridique *",FORMES_JUR)
                a3,a4=st.columns(2); capital=a3.number_input("Capital Social (MAD)",0.0,step=1000.0); patente=a4.text_input("N Patente")
                nom=prenom=cin=""
            section("Informations Fiscales")
            f1,f2,f3=st.columns(3); rc_v=f1.text_input("RC"); if_v=f2.text_input("IF"); ice_v=f3.text_input("ICE")
            f4,f5,f6=st.columns(3); secteur=f4.selectbox("Secteur",SECTEURS); mode=f5.selectbox("Mode Declaration",MODES); regime=f6.selectbox("Regime",REGIMES)
            section("Coordonnees")
            c1,c2,c3=st.columns(3); tel=c1.text_input("Telephone"); email=c2.text_input("Email"); ville=c3.selectbox("Ville",VILLES)
            adr=st.text_input("Adresse"); notes=st.text_area("Notes",height=55)
            if st.form_submit_button("Enregistrer le Dossier",use_container_width=True):
                errs=[]
                if is_pp and (not nom.strip() or not prenom.strip() or not cin.strip()): errs.append("Nom, Prenom, CIN obligatoires.")
                if not is_pp and not rs.strip(): errs.append("Raison Sociale obligatoire.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    db.add_client(dict(type_personne="Physique" if is_pp else "Morale",nom=nom.strip().upper(),prenom=prenom.strip(),cin=cin.strip().upper(),raison_sociale=rs.strip().upper(),forme_juridique=fj,capital_social=capital,rc=rc_v.strip(),if_fiscal=if_v.strip(),patente=patente.strip(),ice=ice_v.strip(),secteur_activite=secteur,mode_declaration=mode,regime_fiscal=regime,telephone=tel.strip(),email=email.strip(),adresse=adr.strip(),ville=ville,notes=notes.strip()))
                    st.success("Dossier enregistre avec succes.")

    with tab_pp:
        lp1,lp2=st.columns([3,1])
        q_pp=lp1.text_input("Recherche",key="qpp",placeholder="Nom, CIN, RC, IF...")
        s_pp=lp2.selectbox("Statut",["Tous"]+STATUTS_CLI,key="spp")
        df_pp=db.get_clients("Physique",s_pp,q_pp)
        st.caption(f"{len(df_pp)} dossier(s) trouves")
        if not df_pp.empty:
            dl,_=st.columns([1,6]); dl.download_button("Exporter Excel",excel_bytes(df_pp),f"PP_{datetime.now():%Y%m%d}.xlsx",mime="application/vnd.ms-excel",use_container_width=True)
            cols=["nom","prenom","cin","rc","if_fiscal","patente","secteur_activite","mode_declaration","statut","date_creation"]
            ren={"nom":"Nom","prenom":"Prenom","cin":"CIN","rc":"RC","if_fiscal":"IF","patente":"Patente","secteur_activite":"Secteur","mode_declaration":"Mode","statut":"Statut","date_creation":"Date"}
            st.dataframe(df_pp[cols].rename(columns=ren),use_container_width=True,hide_index=True)
        else: al_ok("Aucune personne physique trouvee.")

    with tab_pm:
        lm1,lm2=st.columns([3,1])
        q_pm=lm1.text_input("Recherche",key="qpm",placeholder="Raison sociale, RC, IF...")
        s_pm=lm2.selectbox("Statut",["Tous"]+STATUTS_CLI,key="spm")
        df_pm=db.get_clients("Morale",s_pm,q_pm)
        st.caption(f"{len(df_pm)} dossier(s) trouves")
        if not df_pm.empty:
            dl2,_=st.columns([1,6]); dl2.download_button("Exporter Excel",excel_bytes(df_pm),f"PM_{datetime.now():%Y%m%d}.xlsx",mime="application/vnd.ms-excel",use_container_width=True)
            cols=["raison_sociale","forme_juridique","capital_social","rc","if_fiscal","ice","secteur_activite","mode_declaration","statut","date_creation"]
            ren={"raison_sociale":"Raison Sociale","forme_juridique":"Forme","capital_social":"Capital","rc":"RC","if_fiscal":"IF","ice":"ICE","secteur_activite":"Secteur","mode_declaration":"Mode","statut":"Statut","date_creation":"Date"}
            st.dataframe(df_pm[cols].rename(columns=ren),use_container_width=True,hide_index=True)
        else: al_ok("Aucune personne morale trouvee.")

    with tab_edit:
        opts=client_opts()
        if not opts: al_ok("Aucun client enregistre."); return
        sel=st.selectbox("Choisir un dossier",list(opts.keys()))
        cid=opts[sel]; row=db.get_client(cid); is_ppe=row.get("type_personne")=="Physique"
        with st.form("fec"):
            ec1,ec2=st.columns(2)
            with ec1:
                if is_ppe:
                    e_nom=st.text_input("Nom",value=row.get("nom","")); e_cin=st.text_input("CIN",value=row.get("cin",""))
                    e_rs=""; e_fj=row.get("forme_juridique","SARL"); e_cap=0.0
                else:
                    e_rs=st.text_input("Raison Sociale",value=row.get("raison_sociale",""))
                    fj_i=FORMES_JUR.index(row.get("forme_juridique","SARL")) if row.get("forme_juridique") in FORMES_JUR else 0
                    e_fj=st.selectbox("Forme Juridique",FORMES_JUR,index=fj_i)
                    e_cap=st.number_input("Capital (MAD)",value=float(row.get("capital_social",0) or 0),step=1000.0)
                    e_nom=""; e_cin=""
                e_rc=st.text_input("RC",value=row.get("rc","")); e_if=st.text_input("IF",value=row.get("if_fiscal",""))
            with ec2:
                e_pre=st.text_input("Prenom",value=row.get("prenom","")) if is_ppe else None
                e_ice=st.text_input("ICE",value=row.get("ice",""))
                sec_i=SECTEURS.index(row.get("secteur_activite","Commerce")) if row.get("secteur_activite") in SECTEURS else 0
                e_sec=st.selectbox("Secteur",SECTEURS,index=sec_i)
                mod_i=MODES.index(row.get("mode_declaration","Annuel")) if row.get("mode_declaration") in MODES else 0
                e_mode=st.selectbox("Mode Declaration",MODES,index=mod_i)
                sta_i=STATUTS_CLI.index(row.get("statut","Actif")) if row.get("statut") in STATUTS_CLI else 0
                e_stat=st.selectbox("Statut",STATUTS_CLI,index=sta_i)
            e_tel=st.text_input("Telephone",value=row.get("telephone","")); e_email=st.text_input("Email",value=row.get("email",""))
            e_adr=st.text_input("Adresse",value=row.get("adresse","")); e_note=st.text_area("Notes",value=row.get("notes",""),height=55)
            b1,b2=st.columns(2)
            if b1.form_submit_button("Sauvegarder les modifications",use_container_width=True):
                epv=e_pre if is_ppe and isinstance(e_pre,str) else row.get("prenom","")
                db.update_client(cid,dict(type_personne=row['type_personne'],nom=e_nom.upper() if is_ppe else "",prenom=epv,cin=e_cin.upper() if is_ppe else "",raison_sociale=e_rs.upper() if not is_ppe else "",forme_juridique=e_fj,capital_social=e_cap if not is_ppe else 0,rc=e_rc,if_fiscal=e_if,patente=row.get("patente",""),ice=e_ice,secteur_activite=e_sec,mode_declaration=e_mode,regime_fiscal=row.get("regime_fiscal","RNR"),telephone=e_tel,email=e_email,adresse=e_adr,ville=row.get("ville",""),statut=e_stat,notes=e_note))
                st.success("Dossier mis a jour avec succes."); st.rerun()
            if b2.form_submit_button("Supprimer ce dossier",use_container_width=True):
                db.delete_client(cid); st.warning("Dossier supprime."); st.rerun()


# ══════════════════════════════════════════════════════════
#  PAGE 3 — DECLARATIONS
# ══════════════════════════════════════════════════════════
def page_declarations():
    hero("Declarations Fiscales","TVA · IS · IR · CNSS · Patente · Taxe Professionnelle","Fiscal")
    tab_add,tab_list,tab_stats=st.tabs(["Nouvelle Declaration","Historique","Analyses"])

    with tab_add:
        opts=client_opts()
        if not opts: al_warn("Ajoutez d'abord des clients."); return
        with st.form("fdl",clear_on_submit=True):
            d1,d2=st.columns(2); cli_d=d1.selectbox("Client *",list(opts.keys())); type_d=d2.selectbox("Type *",TYPES_DECL)
            d3,d4=st.columns(2); annee=d3.number_input("Annee",2015,2030,datetime.now().year); periode=d4.text_input("Periode",placeholder="ex: T1 2024")
            d5,d6=st.columns(2); statut=d5.selectbox("Statut",STATUTS_DECL); echeance=d6.date_input("Echeance")
            d7,d8=st.columns(2); mont_du=d7.number_input("Montant Du (MAD)",0.0,step=0.01); mont_pa=d8.number_input("Montant Paye (MAD)",0.0,step=0.01)
            depot=st.date_input("Date de Depot"); notes_d=st.text_area("Notes",height=55)
            if st.form_submit_button("Enregistrer la Declaration",use_container_width=True):
                db.add_declaration(dict(client_id=opts[cli_d],type_decl=type_d,annee=int(annee),periode=periode,date_echeance=str(echeance),date_depot=str(depot),montant_du=mont_du,montant_paye=mont_pa,statut=statut,notes=notes_d))
                st.success(f"Declaration {type_d} enregistree avec succes.")

    with tab_list:
        l1,l2=st.columns(2); ft=l1.selectbox("Type",["Tous"]+TYPES_DECL,key="dlt"); fs=l2.selectbox("Statut",["Tous"]+STATUTS_DECL,key="dls")
        df_d=db.get_declarations(type_d=ft,statut=fs); st.caption(f"{len(df_d)} declaration(s)")
        if not df_d.empty:
            ex1, ex2, _ = st.columns([1, 1, 5])
            ex1.download_button("Exporter Excel", excel_bytes(df_d), f"decl_{datetime.now():%Y%m%d}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
            pdf_decl = pdf_reports.rapport_declarations(df_d)
            ex2.download_button("Exporter PDF", pdf_decl, f"declarations_{datetime.now():%Y%m%d}.pdf", mime="application/pdf", use_container_width=True)
            cols_show=[c for c in df_d.columns if c not in ("client_id","type_personne")]
            st.dataframe(df_d[cols_show],use_container_width=True,hide_index=True)
            section("Mise a Jour Rapide")
            u1,u2,u3=st.columns(3); did=u1.number_input("ID Declaration",1,step=1,key="uid"); nst=u2.selectbox("Nouveau Statut",STATUTS_DECL,key="ust"); npay=u3.number_input("Montant Paye (MAD)",0.0,step=0.01,key="upay")
            if st.button("Appliquer la mise a jour",key="bupd"):
                db.update_decl(int(did),nst,npay if npay>0 else None); st.success("Mise a jour effectuee."); st.rerun()
        else: al_ok("Aucune declaration trouvee.")

    with tab_stats:
        df_a=db.get_declarations()
        if df_a.empty: al_ok("Aucune donnee."); return
        kpi_row([
            {"val":fmt(df_a['montant_du'].sum()),                           "label":"Total Du",      "color":"amber","badge":"MAD","badge_type":"neu"},
            {"val":fmt(df_a['montant_paye'].sum()),                         "label":"Total Paye",    "color":"green","badge":"Recu","badge_type":"up"},
            {"val":fmt(df_a['montant_du'].sum()-df_a['montant_paye'].sum()),"label":"Reste a Payer", "color":"red",  "badge":"A regulariser","badge_type":"down"},
        ],cols=3)
        sc1,sc2=st.columns(2)
        with sc1:
            grp=df_a.groupby("statut").size().reset_index(name="nb")
            cols_m={"Deposee":T['green'],"En attente":T['amber'],"En retard":T['red'],"Annulee":T['dim']}
            fig=go.Figure(go.Pie(labels=grp["statut"],values=grp["nb"],hole=.55,marker_colors=[cols_m.get(s,T['sky']) for s in grp["statut"]]))
            fig.update_layout(title=dict(text="Repartition par Statut",font=dict(color=T['text'])),**CHART(),legend=dict(font=dict(color=T['muted']))); st.plotly_chart(fig,use_container_width=True)
        with sc2:
            grp2=df_a.groupby("type_decl")["montant_du"].sum().reset_index()
            fig2=px.bar(grp2,x="type_decl",y="montant_du",title="Montants Dus par Type",color="type_decl",color_discrete_sequence=C)
            fig2.update_layout(**CHART(),showlegend=False,title=dict(font=dict(color=T['text']))); st.plotly_chart(fig2,use_container_width=True)


# ══════════════════════════════════════════════════════════
#  PAGE 4 — COMPTABILITE
# ══════════════════════════════════════════════════════════
def page_comptabilite():
    hero("Tenue de Comptabilite","Journal des operations · Bilan simplifie","Comptabilite")
    tab_add,tab_journal,tab_bilan=st.tabs(["Saisir une Piece","Journal","Bilan"])

    with tab_add:
        opts=client_opts()
        if not opts: al_warn("Ajoutez d'abord des clients."); return
        with st.form("fpc",clear_on_submit=True):
            p1,p2=st.columns(2); cli_p=p1.selectbox("Client *",list(opts.keys())); type_p=p2.selectbox("Type *",TYPES_PIECE)
            p3,p4=st.columns(2); num=p3.text_input("N Piece"); date_p=p4.date_input("Date",value=date.today())
            libelle=st.text_input("Libelle *")
            p5,p6,p7=st.columns(3); ht=p5.number_input("Montant HT (MAD)",0.0,step=0.01); tva_r=p6.selectbox("Taux TVA (%)",TVA_TAUX,index=4); ttc=round(ht*(1+tva_r/100),2); p7.metric("TTC",fmt(ttc))
            p8,p9=st.columns(2); cdebit=p8.text_input("Compte Debit (PCM)",placeholder="ex: 3421"); ccred=p9.text_input("Compte Credit (PCM)",placeholder="ex: 4411")
            notes_p=st.text_area("Notes",height=50)
            if st.form_submit_button("Saisir la Piece",use_container_width=True):
                if not libelle.strip(): st.error("Le libelle est obligatoire.")
                else:
                    db.add_piece(dict(client_id=opts[cli_p],type_piece=type_p,numero=num.strip(),date_piece=str(date_p),libelle=libelle.strip(),compte_debit=cdebit,compte_credit=ccred,montant_ht=ht,taux_tva=tva_r,notes=notes_p))
                    st.success(f"Piece saisie — TTC : {fmt(ttc)}")

    with tab_journal:
        jt=st.selectbox("Filtrer par type",["Tous"]+TYPES_PIECE,key="jt")
        df_j=db.get_pieces(type_p=jt); st.caption(f"{len(df_j)} ecriture(s)")
        if not df_j.empty:
            dl,_=st.columns([1,6]); dl.download_button("Exporter Excel",excel_bytes(df_j),f"journal_{datetime.now():%Y%m%d}.xlsx",mime="application/vnd.ms-excel",use_container_width=True)
            st.dataframe(df_j,use_container_width=True,hide_index=True)
        else: al_ok("Aucune ecriture comptable.")

    with tab_bilan:
        df_all=db.get_pieces()
        if df_all.empty: al_ok("Aucune ecriture comptable."); return
        ventes=df_all[df_all['type_piece']=='Facture Vente']['montant_ttc'].sum()
        achats=df_all[df_all['type_piece']=='Facture Achat']['montant_ttc'].sum()
        kpi_row([
            {"val":fmt(ventes),       "label":"Chiffre d Affaires TTC","color":"green","badge":"Ventes","badge_type":"up"},
            {"val":fmt(achats),        "label":"Total Achats TTC",      "color":"red",  "badge":"Achats","badge_type":"down"},
            {"val":fmt(ventes-achats), "label":"Resultat Brut",         "color":"sky" if ventes>=achats else "red"},
        ],cols=3)
        bc1,bc2=st.columns(2)
        with bc1:
            grp=df_all.groupby("type_piece")["montant_ttc"].sum().reset_index()
            fig=px.bar(grp,x="type_piece",y="montant_ttc",title="Montants TTC par Type",color="type_piece",color_discrete_sequence=C)
            fig.update_layout(**CHART(),showlegend=False,title=dict(font=dict(color=T['text']))); st.plotly_chart(fig,use_container_width=True)
        with bc2:
            df_v=df_all[df_all['type_piece']=='Facture Vente'].copy()
            if not df_v.empty:
                df_v['mois']=pd.to_datetime(df_v['date_piece'],errors='coerce').dt.to_period('M').astype(str)
                grp2=df_v.groupby("mois")["montant_ttc"].sum().reset_index()
                fig2=px.area(grp2,x="mois",y="montant_ttc",title="Evolution CA Mensuel",color_discrete_sequence=[T['sky']])
                fig2.update_layout(**CHART(),title=dict(font=dict(color=T['text']))); st.plotly_chart(fig2,use_container_width=True)


# ══════════════════════════════════════════════════════════
#  PAGE 5 — PAIE
# ══════════════════════════════════════════════════════════
def page_paie():
    hero("Paie et Charges Sociales","Calcul CNSS · AMO · IR — Bareme DGI Maroc","Paie")
    tab_sim,tab_add,tab_hist=st.tabs(["Simulateur","Nouveau Bulletin","Historique"])

    with tab_sim:
        # Simulateur ameliore avec apercu temps reel
        brut=st.slider("Salaire Brut Mensuel (MAD)",3000,50000,8000,step=100,help="Glissez pour simuler differents salaires")
        if brut>0:
            c=db.calculer_paie(brut); tr=c['cnss_salariale']+c['amo_salariale']+c['ir_mensuel']; tp=c['cnss_patronale']+c['amo_patronale']; pn=round(c['salaire_net']/brut*100,1)
            kpi_row([
                {"val":fmt(brut),            "label":"Salaire Brut",  "color":"sky","badge":"Brut","badge_type":"neu"},
                {"val":fmt(tr),              "label":"Retenues Totales","color":"red","sub":"CNSS+AMO+IR","badge":f"-{round(tr/brut*100,1)}%","badge_type":"down"},
                {"val":fmt(c['salaire_net']),"label":"Salaire Net",    "color":"green","sub":f"{pn}% du brut","badge":"Net","badge_type":"up"},
                {"val":fmt(brut+tp),         "label":"Cout Employeur", "color":"amber","sub":f"Charges pat.: {fmt(tp)}"},
            ],cols=4)

            # Graphique waterfall
            fig=go.Figure(go.Waterfall(
                orientation="v",measure=["absolute","relative","relative","relative","total"],
                x=["Brut","- CNSS","- AMO","- IR","Net"],
                y=[brut,-c['cnss_salariale'],-c['amo_salariale'],-c['ir_mensuel'],0],
                connector={"line":{"color":T['border']}},
                decreasing={"marker":{"color":T['red']}},
                increasing={"marker":{"color":T['green']}},
                totals={"marker":{"color":T['sky']}},
                text=[fmt(brut),fmt(-c['cnss_salariale']),fmt(-c['amo_salariale']),fmt(-c['ir_mensuel']),fmt(c['salaire_net'])],
                textposition="outside"))
            fig.update_layout(title=dict(text="Decomposition Detaillee du Salaire",font=dict(color=T['text'])),**CHART())
            st.plotly_chart(fig,use_container_width=True)

            col1,col2=st.columns(2)
            with col1:
                section("Retenues Salariales")
                st.metric("CNSS Salariale (4.48% / plaf.6000)",fmt(c['cnss_salariale']))
                st.metric("AMO Salariale (2.26%)",fmt(c['amo_salariale']))
                st.metric("IR Mensuel",fmt(c['ir_mensuel']))
            with col2:
                section("Charges Patronales")
                st.metric("CNSS Patronale (8.98% / plaf.6000)",fmt(c['cnss_patronale']))
                st.metric("AMO Patronale (3.96%)",fmt(c['amo_patronale']))

            with st.expander("Detail du calcul IR — Bareme DGI Maroc"):
                frais=min(brut*.20,2500); rni=max(brut-c['cnss_salariale']-c['amo_salariale']-frais,0)
                st.markdown(f"""
| Etape | Formule | Montant |
|-------|---------|---------|
| Salaire Brut | — | {fmt(brut)} |
| - CNSS Salariale | min(brut,6000) x 4.48% | {fmt(c['cnss_salariale'])} |
| - AMO Salariale | brut x 2.26% | {fmt(c['amo_salariale'])} |
| - Frais Professionnels | 20% plafonne a 2500 MAD | {fmt(frais)} |
| RNI Mensuel | — | {fmt(rni)} |
| RNI Annuel | x 12 | {fmt(rni*12)} |
| IR Mensuel | Bareme progressif | {fmt(c['ir_mensuel'])} |
| **Net a Payer** | Brut - CNSS - AMO - IR | **{fmt(c['salaire_net'])}** |
""")

    with tab_add:
        opts=client_opts()
        if not opts: al_warn("Ajoutez d'abord des clients."); return
        with st.form("fpa",clear_on_submit=True):
            q1,q2=st.columns(2); cli_p=q1.selectbox("Entreprise *",list(opts.keys())); emp_nom=q2.text_input("Nom Employe *")
            q3,q4=st.columns(2); emp_pre=q3.text_input("Prenom Employe *"); emp_cin=q4.text_input("CIN Employe")
            q5,q6,q7=st.columns(3); mois_p=q5.selectbox("Mois",list(range(1,13)),format_func=lambda m:db.MOIS_NOMS[m]); annee_p=q6.number_input("Annee",2020,2030,datetime.now().year); brut_b=q7.number_input("Salaire Brut *",3000.0,step=100.0)
            avances=st.number_input("Avances (MAD)",0.0,step=100.0)
            if st.form_submit_button("Calculer et Enregistrer",use_container_width=True):
                if not emp_nom.strip() or not emp_pre.strip(): st.error("Nom et prenom obligatoires.")
                else:
                    db.add_paie(dict(client_id=opts[cli_p],employe_nom=emp_nom.strip().upper(),employe_prenom=emp_pre.strip(),employe_cin=emp_cin.strip(),mois=int(mois_p),annee=int(annee_p),salaire_brut=brut_b,avances=avances))
                    cc=db.calculer_paie(brut_b); st.success(f"Bulletin enregistre — Net a payer : {fmt(cc['salaire_net']-avances)}")

    with tab_hist:
        df_p=db.get_paie()
        if df_p.empty: al_ok("Aucun bulletin de paie."); return
        st.caption(f"{len(df_p)} bulletin(s)")
        ex1, ex2, _ = st.columns([1, 1, 5])
        ex1.download_button("Exporter Excel", excel_bytes(df_p), f"paie_{datetime.now():%Y%m%d}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
        disp=df_p.copy(); disp['mois']=disp['mois'].apply(lambda m:db.MOIS_NOMS[int(m)] if pd.notnull(m) and int(m) in range(1,13) else str(m))
        st.dataframe(disp, use_container_width=True, hide_index=True)

        section("Telecharger un Bulletin PDF")
        opts_paie = client_opts()
        if opts_paie:
            sel_cli_paie = st.selectbox("Choisir un client", list(opts_paie.keys()), key="paie_pdf_cli")
            cid_paie = opts_paie[sel_cli_paie]
            df_cli_paie = db.get_paie(client_id=cid_paie)
            if not df_cli_paie.empty:
                df_cli_paie['label'] = df_cli_paie.apply(
                    lambda r: f"{r['employe']} — {db.MOIS_NOMS[int(r['mois'])]} {int(r['annee'])}", axis=1)
                sel_bul = st.selectbox("Choisir un bulletin", df_cli_paie['label'].tolist(), key="paie_pdf_bul")
                row_bul = df_cli_paie[df_cli_paie['label'] == sel_bul].iloc[0].to_dict()
                cli_info = db.get_client(cid_paie)
                pdf_bul = pdf_reports.bulletin_paie(row_bul, cli_info)
                employe_fn = row_bul.get('employe','employe').replace(' ','_')
                st.download_button(
                    f"Telecharger le bulletin PDF — {sel_bul}",
                    data=pdf_bul,
                    file_name=f"bulletin_{employe_fn}_{int(row_bul['mois'])}_{int(row_bul['annee'])}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


# ══════════════════════════════════════════════════════════
#  PAGE 6 — CREATION
# ══════════════════════════════════════════════════════════
def page_creation():
    hero("Creation d Entreprises","Suivi du parcours : Statuts — RC — IF — Patente — ICE — CNSS — Compte Bancaire","Creation")
    tab_new,tab_suivi=st.tabs(["Nouveau Dossier","Suivi des Dossiers"])

    with tab_new:
        opts=client_opts(); co={"Aucun (prospect)":None}; co.update(opts)
        with st.form("fcr",clear_on_submit=True):
            cr1,cr2=st.columns(2)
            with cr1:
                cli_c=st.selectbox("Client associe",list(co.keys())); nom_e=st.text_input("Nom de l Entreprise *")
                fj_c=st.selectbox("Forme Juridique *",FORMES_JUR); cap_c=st.number_input("Capital Prevu (MAD)",0.0,step=1000.0)
            with cr2:
                assoc=st.text_area("Associes",height=80); siege=st.text_input("Siege Social"); objet=st.text_area("Objet Social",height=80)
            notes_c=st.text_area("Notes",height=50)
            if st.form_submit_button("Creer le Dossier",use_container_width=True):
                if not nom_e.strip(): st.error("Nom de l'entreprise obligatoire.")
                else:
                    db.add_creation(dict(client_id=co[cli_c],nom_entreprise=nom_e.strip().upper(),forme_juridique=fj_c,capital_prevu=cap_c,associes=assoc.strip(),siege_social=siege.strip(),objet_social=objet.strip(),notes=notes_c.strip()))
                    st.success(f"Dossier {nom_e.upper()} cree avec succes.")

    with tab_suivi:
        df_cr=db.get_creations()
        if df_cr.empty: al_ok("Aucun dossier de creation en cours."); return
        sty={"Terminee":T['green'],"En cours":T['sky'],"En attente":T['dim'],"Bloquee":T['red']}
        ico={"Terminee":"✓","En cours":"→","En attente":"○","Bloquee":"✗"}
        for idx,(_,row) in enumerate(df_cr.iterrows()):
            done=sum(1 for e in db.ETAPES if row.get(e)=="Terminee"); pct=int(done/len(db.ETAPES)*100)
            with st.expander(f"  {row['nom_entreprise']}  ·  {row['forme_juridique']}  ·  {pct}% complete"):
                # Header info
                h1,h2,h3=st.columns(3)
                h1.metric("Capital Prevu",fmt(row.get('capital_prevu',0)))
                h2.metric("Date d'Ouverture",row.get('date_debut',''))
                h3.metric("Progression",f"{pct}%")
                st.progress(pct/100,text=f"{done} / {len(db.ETAPES)} etapes terminees")
                st.markdown("---")

                # Etapes visuelles ameliorees
                ec=st.columns(len(db.ETAPES))
                for i,(ce,le) in enumerate(zip(db.ETAPES,db.ETAPES_LABELS)):
                    val=row.get(ce,"En attente")
                    color_css=sty.get(val,T['dim'])
                    bg_css=f"background:{T['sky_bg']};border:1px solid {T['sky_brd']};" if val=="Terminee" else ""
                    ec[i].markdown(
                        f"<div style='text-align:center;font-size:.6rem;color:{T['muted']};padding:6px 4px;border-radius:8px;{bg_css}'>"
                        f"<div style='font-size:.9rem;color:{color_css}'>{ico.get(val,'○')}</div>"
                        f"{le}<br><b style='color:{color_css};font-size:.62rem'>{val}</b></div>",
                        unsafe_allow_html=True)
                st.markdown("---")
                u1,u2,u3=st.columns(3)
                el=u1.selectbox("Etape a modifier",db.ETAPES_LABELS,key=f"el{row['id']}")
                ei=db.ETAPES_LABELS.index(el); ns=u2.selectbox("Nouveau Statut",ETAPES_STAT,key=f"es{row['id']}")
                if u3.button("Mettre a Jour",key=f"bu{row['id']}"):
                    db.update_creation_etape(row['id'],db.ETAPES[ei],ns); st.success("Etape mise a jour."); st.rerun()


# ══════════════════════════════════════════════════════════
#  PAGE 7 — RAPPORTS
# ══════════════════════════════════════════════════════════
def page_rapports():
    hero("Rapports et Analyses","Tableaux de bord analytiques · Export Excel multi-feuilles","Rapports")
    df_c=db.get_clients(); df_d=db.get_declarations(); df_p=db.get_pieces()
    if df_c.empty and df_d.empty: al_ok("Aucune donnee disponible."); return

    if not df_c.empty:
        section("Analyse Clients")
        rc1,rc2,rc3=st.columns(3)
        with rc1:
            grp=df_c.groupby(["type_personne","statut"]).size().reset_index(name="nb")
            fig=px.sunburst(grp,path=["type_personne","statut"],values="nb",title="Type x Statut",color_discrete_sequence=C)
            fig.update_layout(**CHART(),title=dict(font=dict(color=T['text']))); st.plotly_chart(fig,use_container_width=True)
        with rc2:
            grp2=df_c.groupby("secteur_activite").size().reset_index(name="nb").sort_values("nb")
            fig2=px.bar(grp2,y="secteur_activite",x="nb",orientation="h",title="Clients par Secteur",color_discrete_sequence=[T['sky']])
            fig2.update_layout(**CHART(),title=dict(font=dict(color=T['text']))); st.plotly_chart(fig2,use_container_width=True)
        with rc3:
            grp3=df_c.groupby("mode_declaration").size().reset_index(name="nb")
            fig3=go.Figure(go.Pie(labels=grp3["mode_declaration"],values=grp3["nb"],hole=.45,marker_colors=C[:3]))
            fig3.update_layout(title=dict(text="Mode de Declaration",font=dict(color=T['text'])),**CHART(),legend=dict(font=dict(color=T['muted']))); st.plotly_chart(fig3,use_container_width=True)

    if not df_d.empty:
        section("Analyse Fiscale")
        dc1,dc2=st.columns(2)
        with dc1:
            grp4=df_d.groupby(["type_decl","statut"]).size().reset_index(name="nb")
            fig4=px.bar(grp4,x="type_decl",y="nb",color="statut",title="Declarations : Type x Statut",color_discrete_sequence=C)
            fig4.update_layout(**CHART(),title=dict(font=dict(color=T['text'])),legend=dict(font=dict(color=T['muted']))); st.plotly_chart(fig4,use_container_width=True)
        with dc2:
            grp5=df_d.groupby("annee").agg(du=("montant_du","sum"),paye=("montant_paye","sum")).reset_index()
            fig5=go.Figure(); fig5.add_trace(go.Bar(name="Du",x=grp5["annee"],y=grp5["du"],marker_color=T['red'])); fig5.add_trace(go.Bar(name="Paye",x=grp5["annee"],y=grp5["paye"],marker_color=T['green']))
            fig5.update_layout(title=dict(text="Du vs Paye par Annee",font=dict(color=T['text'])),barmode="group",**CHART(),legend=dict(font=dict(color=T['muted']))); st.plotly_chart(fig5,use_container_width=True)

    section("Export du Rapport Complet")
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        if not df_c.empty: df_c.to_excel(w,index=False,sheet_name="Clients")
        if not df_d.empty: df_d.to_excel(w,index=False,sheet_name="Declarations")
        if not df_p.empty: df_p.to_excel(w,index=False,sheet_name="Comptabilite")
        db.get_paie().to_excel(w,index=False,sheet_name="Paie"); db.get_creations().to_excel(w,index=False,sheet_name="Creations")

    r1, r2 = st.columns(2)
    r1.download_button("Telecharger le Rapport Complet Excel — Toutes Feuilles",data=buf.getvalue(),file_name=f"rapport_{datetime.now():%Y%m%d_%H%M}.xlsx",mime="application/vnd.ms-excel",use_container_width=True)

    stats_g = db.get_stats()
    pdf_g = pdf_reports.rapport_general(stats_g, clients_df=df_c, declarations_df=df_d)
    r2.download_button("Telecharger le Rapport General PDF",data=pdf_g,file_name=f"rapport_cabinet_{datetime.now():%Y%m%d}.pdf",mime="application/pdf",use_container_width=True)

    section("Rapport PDF par Client")
    opts_rc = client_opts()
    if opts_rc:
        sel_rc = st.selectbox("Choisir un client", list(opts_rc.keys()), key="rpt_cli")
        cid_rc = opts_rc[sel_rc]
        cli_rc = db.get_client(cid_rc)
        decl_rc = db.get_declarations(client_id=cid_rc)
        paie_rc = db.get_paie(client_id=cid_rc)
        pdf_cli = pdf_reports.rapport_client(cli_rc, declarations=decl_rc, paie=paie_rc)
        nom_rc = (cli_rc.get("raison_sociale") or f"{cli_rc.get('prenom','')}_{cli_rc.get('nom','')}").replace(" ","_")
        st.download_button(f"Telecharger la Fiche PDF — {sel_rc}",data=pdf_cli,file_name=f"fiche_{nom_rc}.pdf",mime="application/pdf",use_container_width=True)


# ══════════════════════════════════════════════════════════
#  PAGE 8 — ALERTES
# ══════════════════════════════════════════════════════════
def page_alertes():
    hero("Alertes et Surveillance","Suivi automatique des declarations, echeances et activite clients","Alertes")
    df_d=db.get_declarations(); df_c=db.get_clients(); today=date.today()
    crit=0; warn=0

    section("Declarations en Retard")
    if not df_d.empty:
        retard=df_d[df_d['statut']=='En retard'].copy(); crit+=len(retard)
        if retard.empty: al_ok("Aucune declaration en retard.")
        else:
            for _,r in retard.iterrows():
                al_danger(f"{r.get('type_decl','')} — {r.get('client_label',r.get('client_id',''))}",
                          f"Periode : {r.get('periode','—')} · Echeance : {r.get('date_echeance','—')} · {r.get('montant_du',0):,.0f} MAD")
    else: al_ok("Aucune donnee de declarations.")

    section("Echeances dans les 7 Prochains Jours")
    if not df_d.empty:
        df_ech=df_d.copy(); df_ech['_ech']=df_ech['date_echeance'].apply(safe_date)
        proch=df_ech[df_ech['_ech'].notna()&(df_ech['_ech']>=today)&(df_ech['_ech']<=today+timedelta(days=7))&df_ech['statut'].isin(['En attente'])]
        warn+=len(proch)
        if proch.empty: al_ok("Aucune echeance dans les 7 prochains jours.")
        else:
            for _,r in proch.iterrows():
                al_warn(f"{r.get('type_decl','')} — {r.get('client_label',r.get('client_id',''))}",
                        f"Echeance dans {(r['_ech']-today).days} jour(s) ({r.get('date_echeance','')}) · {r.get('montant_du',0):,.0f} MAD")

    section("CNSS — Cotisations en Attente")
    if not df_d.empty:
        cnss_att=df_d[(df_d['type_decl']=='CNSS')&(df_d['annee']==today.year)&df_d['statut'].isin(['En attente','En retard'])]
        if cnss_att.empty: al_ok(f"CNSS en ordre pour {today.year}.")
        else:
            for _,r in cnss_att.iterrows():
                warn+=1; al_warn(f"CNSS — {r.get('client_label',r.get('client_id',''))}",f"Periode : {r.get('periode','—')} · {r.get('statut','')} · {r.get('montant_du',0):,.0f} MAD")

    section("Clients Sans Activite Recente (90 jours)")
    if not df_c.empty and not df_d.empty and 'client_id' in df_d.columns:
        date_lim=today-timedelta(days=90)
        df_dep=df_d.copy(); df_dep['_dep']=df_dep['date_depot'].apply(safe_date)
        df_v=df_dep[df_dep['_dep'].notna()]
        dernieres=df_v.groupby('client_id')['_dep'].max() if not df_v.empty else pd.Series(dtype=object)
        inactifs=[]
        actifs=df_c[df_c['statut']=='Actif'] if 'statut' in df_c.columns else df_c
        for _,c in actifs.iterrows():
            cid=c['id']; last=dernieres.get(cid,None)
            if last is None or last<date_lim:
                inactifs.append({"cli":db.client_label(c),"last":str(last) if last else "Jamais","j":(today-last).days if last else "—"})
        warn+=len(inactifs)
        if not inactifs: al_ok("Tous les clients actifs ont eu une activite recente.")
        else:
            for ci in inactifs[:10]:
                al_warn(ci["cli"],f"Derniere declaration : {ci['last']} · Inactif depuis : {ci['j']} jours")
    else: al_ok("Donnees insuffisantes pour cette analyse.")

    st.markdown("---")
    kpi_row([
        {"val":crit,"label":"Alertes Critiques","color":"red"  if crit else "neutral","badge":"Urgent" if crit else "","badge_type":"down"},
        {"val":warn,"label":"Avertissements",   "color":"amber" if warn else "neutral","badge":"Attention" if warn else "","badge_type":"neu"},
        {"val":crit+warn,"label":"Total Alertes","color":"sky"},
    ],cols=3)
    st.session_state['_crit']=crit; st.session_state['_warn']=warn


# ══════════════════════════════════════════════════════════
#  PAGE 9 — INTELLIGENCE ARTIFICIELLE
# ══════════════════════════════════════════════════════════
def page_ia():
    hero("Intelligence Artificielle", "Predictions · Anomalies · Previsions CA — Random Forest & Isolation Forest", "IA")

    tab_retard, tab_ca, tab_anomalies = st.tabs([
        "Prediction Retards", "Prevision CA", "Detection Anomalies"
    ])

    # ── TAB 1 : PREDICTION RETARD ──
    with tab_retard:
        section("Modele : Random Forest — Risque de Retard de Declaration")
        st.markdown(f"""
        <div style='background:{T["sky_bg"]};border:1px solid {T["sky_brd"]};border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:.87rem;color:{T["muted"]}'>
        <b style='color:{T["sky"]}'>Comment ca fonctionne ?</b><br>
        Le modele Random Forest analyse l'historique des declarations (type, montant, secteur, mode de declaration)
        et calcule la probabilite qu'un client soit en retard pour sa prochaine declaration.
        Un risque &gt; 60% declanche une alerte de relance.
        </div>""", unsafe_allow_html=True)

        opts = client_opts()
        if not opts:
            al_warn("Ajoutez des clients et des declarations pour activer l'IA.")
        else:
            col1, col2 = st.columns(2)
            sel_cli = col1.selectbox("Choisir un client", list(opts.keys()), key="ia_cli")
            sel_type = col2.selectbox("Type de declaration", ["TVA","IS","IR","CNSS","Patente"], key="ia_type")
            cid_ia = opts[sel_cli]

            if st.button("Analyser le Risque", key="ia_btn", use_container_width=True):
                with st.spinner("Analyse en cours..."):
                    risque = ai.predire_risque_retard(cid_ia, sel_type)
                if risque is None:
                    al_warn("Donnees insuffisantes pour entrainer le modele (minimum 5 declarations necessaires).")
                else:
                    pct = int(risque * 100)
                    couleur = T["red"] if pct >= 60 else T["amber"] if pct >= 35 else T["green"]
                    niveau = "ELEVE — Relance recommandee" if pct >= 60 else "MODERE — A surveiller" if pct >= 35 else "FAIBLE — Situation normale"
                    st.markdown(f"""
                    <div style='background:{T["card"]};border:2px solid {couleur};border-radius:14px;padding:24px;text-align:center;margin:16px 0'>
                      <div style='font-size:3rem;font-weight:800;color:{couleur}'>{pct}%</div>
                      <div style='font-size:1rem;color:{T["muted"]};margin-top:6px'>Probabilite de retard — {sel_type}</div>
                      <div style='font-size:.85rem;font-weight:700;color:{couleur};margin-top:8px;
                                  background:{couleur}15;border-radius:8px;padding:6px 14px;display:inline-block'>
                        {niveau}
                      </div>
                    </div>""", unsafe_allow_html=True)

            section("Analyse de tous les clients actifs")
            if st.button("Lancer l'analyse globale", key="ia_global"):
                with st.spinner("Analyse de tous les clients..."):
                    df_actifs = db.get_clients(statut="Actif")
                    resultats = []
                    for _, cli in df_actifs.iterrows():
                        for td in ["TVA","IS","IR"]:
                            r = ai.predire_risque_retard(cli["id"], td)
                            if r is not None:
                                nom = cli.get("raison_sociale") or f"{cli.get('prenom','')} {cli.get('nom','')}".strip()
                                resultats.append({"Client": nom, "Type": td, "Risque": f"{int(r*100)}%",
                                                  "Niveau": "Eleve" if r>=0.6 else "Modere" if r>=0.35 else "Faible"})
                if resultats:
                    df_res = pd.DataFrame(resultats)
                    kpi_row([
                        {"val": len(df_res[df_res["Niveau"]=="Eleve"]),  "label":"Risques Eleves",  "color":"red"},
                        {"val": len(df_res[df_res["Niveau"]=="Modere"]), "label":"Risques Moderes", "color":"amber"},
                        {"val": len(df_res[df_res["Niveau"]=="Faible"]), "label":"Risques Faibles", "color":"green"},
                    ], cols=3)
                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                else:
                    al_warn("Donnees insuffisantes pour l'analyse globale.")

    # ── TAB 2 : PREVISION CA ──
    with tab_ca:
        section("Modele : Regression Lineaire — Prevision du Chiffre d'Affaires")
        st.markdown(f"""
        <div style='background:{T["sky_bg"]};border:1px solid {T["sky_brd"]};border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:.87rem;color:{T["muted"]}'>
        <b style='color:{T["sky"]}'>Comment ca fonctionne ?</b><br>
        La regression lineaire analyse les factures de vente historiques du client
        et projette le chiffre d'affaires probable pour le mois suivant.
        Necessite au minimum 3 mois de donnees de facturation.
        </div>""", unsafe_allow_html=True)

        opts2 = client_opts()
        if opts2:
            sel2 = st.selectbox("Choisir un client", list(opts2.keys()), key="ca_cli")
            cid2 = opts2[sel2]

            # BOUTON DEMO JURY
            col_demo, col_reset = st.columns([3, 1])
            with col_demo:
                if st.button("🎲 Generer donnees demo (6 mois)", key="ca_demo_btn", use_container_width=True):
                    import random, calendar
                    today = date.today()
                    conn_demo = db.get_conn()
                    base_ca = random.uniform(25000, 80000)
                    for i in range(6, 0, -1):
                        y = today.year if today.month > i else today.year - 1
                        m = (today.month - i) % 12 or 12
                        last_day = calendar.monthrange(y, m)[1]
                        d_piece = f"{y}-{m:02d}-{random.randint(1, last_day):02d}"
                        montant_ht = round(base_ca * random.uniform(0.85, 1.20), 2)
                        tva = round(montant_ht * 0.20, 2)
                        ttc = round(montant_ht + tva, 2)
                        conn_demo.execute(
                            "INSERT INTO pieces_comptables (client_id,type_piece,numero,date_piece,libelle,montant_ht,taux_tva,montant_tva,montant_ttc,statut) VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (cid2, "Facture Vente", f"FV-DEMO-{y}{m:02d}", d_piece,
                             f"CA Demo {calendar.month_name[m]} {y}",
                             montant_ht, 20.0, tva, ttc, "Validee"))
                    conn_demo.commit(); conn_demo.close()
                    st.success("✅ 6 mois generes ! Cliquez sur Calculer la Prevision CA")
                    st.rerun()
            with col_reset:
                if st.button("🗑️ Reset", key="ca_reset_btn", use_container_width=True):
                    conn_r = db.get_conn()
                    conn_r.execute("DELETE FROM pieces_comptables WHERE client_id=? AND numero LIKE 'FV-DEMO-%'", (cid2,))
                    conn_r.commit(); conn_r.close()
                    st.warning("Donnees demo supprimees.")
                    st.rerun()

            if st.button("Calculer la Prevision CA", key="ca_btn", use_container_width=True):
                with st.spinner("Calcul de la prevision..."):
                    ca_prevu = ai.prevoir_ca_prochain_mois(cid2)
                    df_hist = db.get_pieces(client_id=cid2, type_p="Facture Vente")
                if ca_prevu is None:
                    al_warn("Donnees insuffisantes (minimum 3 mois de facturation requis).")
                else:
                    st.markdown(f"""
                    <div style='background:{T["card"]};border:2px solid {T["green"]};border-radius:14px;
                                padding:24px;text-align:center;margin:16px 0'>
                      <div style='font-size:.8rem;color:{T["muted"]};text-transform:uppercase;letter-spacing:1px'>
                        Prevision CA — Mois Prochain
                      </div>
                      <div style='font-size:2.4rem;font-weight:800;color:{T["green"]};margin-top:8px'>
                        {ca_prevu:,.2f} MAD
                      </div>
                      <div style='font-size:.78rem;color:{T["muted"]};margin-top:6px'>
                        Base : regression lineaire sur l'historique des factures de vente
                      </div>
                    </div>""", unsafe_allow_html=True)

                    if not df_hist.empty:
                        df_hist['date_piece'] = pd.to_datetime(df_hist['date_piece'], errors='coerce')
                        df_mois = df_hist.groupby(df_hist['date_piece'].dt.to_period('M'))['montant_ttc'].sum().reset_index()
                        df_mois['mois'] = df_mois['date_piece'].astype(str)
                        fig_ca = px.area(df_mois, x='mois', y='montant_ttc',
                                         title="Historique CA mensuel (TTC)",
                                         color_discrete_sequence=[T['sky']])
                        fig_ca.add_scatter(x=[str(pd.Period.now('M')+1)], y=[ca_prevu],
                                           mode='markers', marker=dict(size=14, color=T['green'], symbol='star'),
                                           name=f"Prevision: {ca_prevu:,.0f} MAD")
                        fig_ca.update_layout(**CHART(), title=dict(font=dict(color=T['text'])))
                        st.plotly_chart(fig_ca, use_container_width=True)

    # ── TAB 3 : ANOMALIES ──
    with tab_anomalies:
        section("Modele : Isolation Forest — Detection d'Anomalies")
        st.markdown(f"""
        <div style='background:{T["sky_bg"]};border:1px solid {T["sky_brd"]};border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:.87rem;color:{T["muted"]}'>
        <b style='color:{T["sky"]}'>Comment ca fonctionne ?</b><br>
        L'algorithme Isolation Forest detecte automatiquement les declarations dont les montants
        sont statistiquement anormaux par rapport au reste des donnees, sans avoir besoin de donnees labellisees.
        Utile pour detecter des erreurs de saisie ou des fraudes potentielles.
        </div>""", unsafe_allow_html=True)

        opts3 = {"Tous les clients": None}
        opts3.update(client_opts())
        sel3 = st.selectbox("Perimetre d'analyse", list(opts3.keys()), key="ano_cli")
        cid3 = opts3[sel3]

        if st.button("Lancer la Detection d'Anomalies", key="ano_btn", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                anomalies = ai.detecter_anomalies_declarations(client_id=cid3)
            if anomalies is None or anomalies.empty:
                al_ok("Aucune anomalie detectee. Toutes les declarations semblent normales.")
            else:
                al_danger(f"{len(anomalies)} anomalie(s) detectee(s)",
                          "Ces declarations ont des montants statistiquement inhabituels. Verifiez les saisies.")
                st.dataframe(anomalies, use_container_width=True, hide_index=True)
                st.caption("Note : Une anomalie ne signifie pas necessairement une erreur — c'est un signal a verifier.")


# ══════════════════════════════════════════════════════════
#  ROUTING
# ══════════════════════════════════════════════════════════
PAGES_STAFF={
    "Tableau de Bord":       page_dashboard,
    "Gestion des Clients":   page_clients,
    "Declarations Fiscales": page_declarations,
    "Comptabilite":          page_comptabilite,
    "Paie et CNSS":          page_paie,
    "Creation d Entreprises":page_creation,
    "Rapports et Analyses":  page_rapports,
    "Alertes":               page_alertes,
    "Intelligence Artificielle": page_ia,
}
PAGES_CLIENT={"Mon Dossier":page_dashboard}


def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in=False
    if not st.session_state.logged_in: show_login(); st.stop()

    role=st.session_state.get("role","client")
    pages_dispo=PAGES_STAFF if role in ("admin","comptable") else PAGES_CLIENT
    username=st.session_state.get("username",""); role_label=st.session_state.get("role_label",role)

    st.sidebar.markdown(f"""
    <div class="sb-head">
      <div class="sb-logo-wrap">
        <div class="sb-icon">RC</div>
      </div>
      <div>
        <div class="sb-name">RC Gestion</div>
        <div class="sb-sub">El Kelaa des Sraghna</div>
      </div>
    </div>
    <div class="sb-user">
      <div class="sb-user-dot"></div>
      <div><strong>{username}</strong> <span style="color:#4a7ab0;font-size:.68rem;">— {role_label}</span></div>
    </div>
    """,unsafe_allow_html=True)

    col_th,col_lo=st.sidebar.columns(2)
    th_lbl="Mode Sombre" if LT else "Mode Clair"
    if col_th.button(th_lbl,use_container_width=True,key="btn_theme"):
        st.session_state.theme="dark" if LT else "light"; st.rerun()
    if col_lo.button("Deconnexion",use_container_width=True,key="btn_logout"):
        for k in ["logged_in","username","role","role_label","client_id"]:
            if k in st.session_state: del st.session_state[k]
        st.session_state.logged_in=False; st.rerun()

    st.sidebar.markdown(f'<div class="sb-nav-lbl">Navigation</div>',unsafe_allow_html=True)
    selected=st.sidebar.radio("",list(pages_dispo.keys()),label_visibility="collapsed")

    if role in ("admin","comptable"):
        s=db.get_stats(); crit=st.session_state.get("_crit",0); warn=st.session_state.get("_warn",0)
        rc_c="#e07070" if s["decl_retard"]>0 else "#4ab8a0"
        st.sidebar.markdown(f"""
        <div class="sb-stat-block">
          <div class="sb-stat-lbl">Apercu Rapide</div>
          <div class="sb-row"><span>Clients</span><strong style="color:#90b8d0">{s['total_clients']}</strong></div>
          <div class="sb-row"><span>Actifs</span><strong style="color:#4ab8a0">{s['actifs']}</strong></div>
          <div class="sb-row"><span>Declarations</span><strong style="color:#90b8d0">{s['decl_total']}</strong></div>
          <div class="sb-row"><span>En Retard</span><strong style="color:{rc_c}">{s['decl_retard']}</strong></div>
          <div class="sb-row" style="border:none"><span>Alertes actives</span><strong style="color:#e0b040">{crit+warn}</strong></div>
          <div class="sb-ver">RC Gestion v4.0</div>
        </div>
        """,unsafe_allow_html=True)

    pages_dispo[selected]()

if __name__=="__main__": main()