"""
pages/5_scenario_simulation.py

Scenario Simulation page — Road Construction cut/fill estimate for a
proposed level road elevation, with DPWH reference embankment slopes.
"""

import streamlit as st

from modules.terrain_model import generate_tin, build_surface_mesh
from modules.analysis import (
    simulate_road_construction,
    DPWH_MIN_FILL_SLOPE,
    DPWH_CUT_SLOPE_SOFT_ROCK,
    DPWH_CUT_SLOPE_HARD_ROCK,
)
from modules.viz import build_terrain_3d_figure, build_cutfill_figure

st.subheader("Scenario Simulation — Road Construction")
st.caption("Estimate cut and fill earthwork for a proposed level road elevation.")

survey_df = st.session_state.get("survey_points")

if survey_df is None or survey_df.empty:
    st.info(
        "No validated survey points loaded yet. "
        "Go to **Survey Data Input** to enter or upload points first."
    )
else:
    tin, tin_error = generate_tin(survey_df)

    if tin_error:
        st.warning(tin_error)
    else:
        elev_min = float(survey_df["Elevation"].min())
        elev_max = float(survey_df["Elevation"].max())
        default_road_elev = round((elev_min + elev_max) / 2, 2)

        road_elevation = st.number_input(
            "Road Elevation (m)",
            min_value=elev_min - 10.0,
            max_value=elev_max + 10.0,
            value=default_road_elev,
            step=0.1,
            key="road_elevation",
            help=f"Terrain spans {elev_min:.2f}-{elev_max:.2f} m. Defaults to the midpoint.",
        )

        sim = simulate_road_construction(survey_df, tin, road_elevation)

        st.markdown(
            "<div style='color:#6B5E58;font-size:0.8em;'>Estimated via the average-end-area "
            "method over each triangulated surface panel — a planning-level approximation, "
            "not a certified quantity survey.</div>",
            unsafe_allow_html=True,
        )
        st.write("")

        col1, col2, col3 = st.columns(3)
        col1.metric("Required Cut", f"{sim['cut_volume']:.1f} m³")
        col2.metric("Required Fill", f"{sim['fill_volume']:.1f} m³")
        net_label = "Net Cut" if sim["net_cut"] >= 0 else "Net Fill"
        col3.metric(net_label, f"{abs(sim['net_cut']):.1f} m³")

        with st.expander("DPWH reference embankment slopes", expanded=False):
            st.caption(
                "For comparison only — this simulation models the road as a level plane "
                "and does not compute embankment side-slope geometry."
            )
            st.markdown(
                f"- **Minimum fill slope:** {DPWH_MIN_FILL_SLOPE}\n"
                f"- **Cut slope (soft/rippable rock):** {DPWH_CUT_SLOPE_SOFT_ROCK}\n"
                f"- **Cut slope (hard/solid rock):** {DPWH_CUT_SLOPE_HARD_ROCK}"
            )

        st.divider()

        col_3d, col_2d = st.columns(2)
        mesh = build_surface_mesh(survey_df, tin)

        with col_3d:
            st.markdown("**3D View — Terrain vs. Road Plane**")
            fig_3d = build_terrain_3d_figure(
                mesh, show_colorbar=False, road_plane_elevation=road_elevation
            )
            st.plotly_chart(fig_3d, width="stretch")

        with col_2d:
            st.markdown("**2D View — Cut / Fill Map**")
            st.plotly_chart(build_cutfill_figure(sim["triangles"]), width="stretch")