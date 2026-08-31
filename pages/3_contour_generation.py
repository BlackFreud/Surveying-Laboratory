"""
pages/3_contour_generation.py

Contour Generation page — interpolates the terrain onto a regular grid and
displays a filled, labeled contour map at a user-selected interval.
"""

import streamlit as st

from modules.contour import generate_contour_grid
from modules.viz import build_contour_figure

st.subheader("Contour Generation")
st.caption("Engineering contour map generated from the terrain surface.")

survey_df = st.session_state.get("survey_points")

if survey_df is None or survey_df.empty:
    st.info(
        "No validated survey points loaded yet. "
        "Go to **Survey Data Input** to enter or upload points first."
    )
else:
    interval = st.selectbox(
        "Contour Interval",
        options=[0.5, 1.0, 2.0, 5.0],
        index=1,
        format_func=lambda v: f"{v} m",
        key="contour_interval",
    )

    grid = generate_contour_grid(survey_df, interval)

    if grid["error"]:
        st.warning(grid["error"])
    else:
        st.success(f"Contour Interval: {interval} m — Generated: {grid['n_lines']} contour lines")
        st.plotly_chart(build_contour_figure(grid, interval, survey_df), width="stretch")