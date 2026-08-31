"""
pages/2_terrain_surface_generation.py

Terrain Surface Generation page — builds the TIN from validated survey
points and shows the 2D triangulation and 3D terrain surface.
"""

import streamlit as st

from modules.terrain_model import generate_tin, build_surface_mesh
from modules.viz import build_terrain_2d_figure, build_terrain_3d_figure

st.subheader("Terrain Surface Generation")
st.caption("Triangulated Irregular Network (TIN) built from survey points.")

survey_df = st.session_state.get("survey_points")

if survey_df is None or survey_df.empty:
    st.info(
        "No validated survey points loaded yet. "
        "Go to **Survey Data Input** to enter or upload points first."
    )
else:
    tin, error = generate_tin(survey_df)

    if error:
        st.error(error)
    else:
        mesh = build_surface_mesh(survey_df, tin)
        st.success(f"Triangulation complete: {mesh['n_triangles']} triangles generated.")

        col_2d, col_3d = st.columns(2)

        with col_2d:
            st.markdown("**2D View — Points & Triangulation**")
            st.plotly_chart(build_terrain_2d_figure(mesh, survey_df), width="stretch")

        with col_3d:
            st.markdown("**3D View — Terrain Surface**")
            st.plotly_chart(build_terrain_3d_figure(mesh, show_colorbar=True), width="stretch")