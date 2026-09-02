"""
app.py

Digital Terrain Model (DTM) Simulator — application entrypoint.

This file renders the shared chrome (page config, global CSS, the branding
title block) and then hands off to Streamlit's native multipage navigation
(st.navigation / st.Page). Because this script runs on every interaction
before the selected page's script executes, the header/CSS defined here
appears consistently across all pages without being duplicated in each one.
"""

import base64
from pathlib import Path

import streamlit as st

from modules.viz import MAROON, TERRACOTTA, PAPER, INK

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DTM Simulator | Civil Engineering Laboratory",
    page_icon="📐",
    layout="wide",
)

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
PAGES_DIR = ROOT_DIR / "pages"


@st.cache_resource(show_spinner=False)
def _img_to_base64(filename: str) -> str:
    path = ASSETS_DIR / filename
    return base64.b64encode(path.read_bytes()).decode()


UM_SEAL_B64 = _img_to_base64("Logo_only.png")
CEE_LOGO_B64 = _img_to_base64("CEE_Logo.png")

# ---------------------------------------------------------------------------
# Global styling
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {{
            font-family: 'IBM Plex Sans', sans-serif;
        }}
        .stApp {{
            background-color: {PAPER};
        }}
        h1, h2, h3, h4, h5 {{
            color: {INK};
            font-family: 'IBM Plex Sans', sans-serif;
        }}
        /* Numeric readouts feel like an instrument display */
        [data-testid="stMetricValue"] {{
            font-family: 'IBM Plex Mono', monospace;
            color: {MAROON};
        }}
        [data-testid="stMetric"] {{
            background-color: white;
            border: 1px solid #E5DFD5;
            border-left: 4px solid {MAROON};
            border-radius: 4px;
            padding: 12px 16px 8px 16px;
        }}
        [data-testid="stDataFrame"] {{
            font-family: 'IBM Plex Mono', monospace;
        }}
        .title-block {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            background-color: white;
            border: 1px solid #E5DFD5;
            border-top: 5px solid {MAROON};
            border-radius: 4px;
            padding: 18px 28px;
            margin-bottom: 18px;
        }}
        .title-block img {{ height: 64px; }}
        .title-block-center {{ text-align: center; flex: 1; }}
        .title-block-eyebrow {{
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            color: {TERRACOTTA};
            text-transform: uppercase;
            margin: 0;
        }}
        .title-block-title {{
            font-size: 1.9rem;
            font-weight: 700;
            color: {INK};
            margin: 2px 0 4px 0;
        }}
        .title-block-flow {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: #6B5E58;
            margin: 0;
        }}
        .slope-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 3px;
            font-weight: 600;
            font-family: 'IBM Plex Mono', monospace;
            color: white;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {INK};
        }}
        section[data-testid="stSidebar"] * {{
            color: {PAPER} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Branding header — styled as an engineering drawing title block
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="title-block">
        <img src="data:image/png;base64,{UM_SEAL_B64}" alt="University of Mindanao Seal">
        <div class="title-block-center">
            <p class="title-block-eyebrow">University of Mindanao &nbsp;·&nbsp; Civil Engineering Laboratory</p>
            <p class="title-block-title">Digital Terrain Model Simulator</p>
            <p class="title-block-flow">Field Survey Data → Coordinate Processing → Terrain Surface → Contour Mapping → Engineering Interpretation</p>
        </div>
        <img src="data:image/png;base64,{CEE_LOGO_B64}" alt="College of Engineering Education Logo">
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Native multipage navigation (Streamlit's recommended UX pattern, replacing
# the manual sidebar-radio routing used in earlier phases)
# ---------------------------------------------------------------------------
pages = [
    st.Page(PAGES_DIR / "6_dashboard.py", title="Exhibit Dashboard", icon="🏛️", default=True),
    st.Page(PAGES_DIR / "7_presentation_mode.py", title="Presentation Mode", icon="🎬"),
    st.Page(PAGES_DIR / "1_survey_data_input.py", title="Survey Data Input", icon="📋"),
    st.Page(PAGES_DIR / "2_terrain_surface_generation.py", title="Terrain Surface Generation", icon="⛰️"),
    st.Page(PAGES_DIR / "3_contour_generation.py", title="Contour Generation", icon="🗺️"),
    st.Page(PAGES_DIR / "4_engineering_analysis.py", title="Engineering Analysis", icon="📐"),
    st.Page(PAGES_DIR / "5_scenario_simulation.py", title="Scenario Simulation", icon="🛣️"),
]
pg = st.navigation(pages)

st.sidebar.markdown("---")
st.sidebar.caption("Surveying Laboratory Interactive Exhibit")
st.sidebar.caption("Developed by Engr. JF Item — Laboratory Custodian")

pg.run()