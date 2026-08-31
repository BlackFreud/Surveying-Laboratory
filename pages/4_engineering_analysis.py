"""
pages/4_engineering_analysis.py

Engineering Analysis page — elevation stats, BSWM slope classification
(Philippine standard), and drainage direction.
"""

import plotly.graph_objects as go
import streamlit as st

from modules.terrain_model import generate_tin
from modules.contour import generate_contour_grid
from modules.analysis import (
    compute_elevation_stats,
    compute_slope_stats,
    compute_drainage_direction,
    BSWM_SLOPE_GROUPS,
)
from modules.viz import MAROON, GOLD, INK, SLOPE_GROUP_COLORS, build_contour_figure

st.subheader("Engineering Analysis")
st.caption("Elevation, slope, and drainage insights derived from the terrain model.")

survey_df = st.session_state.get("survey_points")

if survey_df is None or survey_df.empty:
    st.info(
        "No validated survey points loaded yet. "
        "Go to **Survey Data Input** to enter or upload points first."
    )
else:
    tin, tin_error = generate_tin(survey_df)

    # ---- Elevation Analysis ----
    st.markdown("### Elevation Analysis")
    elev = compute_elevation_stats(survey_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Point", f"{elev['highest_elevation']:.2f} m")
    col1.caption(f"at point {elev['highest_point']}")
    col2.metric("Lowest Point", f"{elev['lowest_elevation']:.2f} m")
    col2.caption(f"at point {elev['lowest_point']}")
    col3.metric("Elevation Difference", f"{elev['elevation_difference']:.2f} m")

    st.divider()

    # ---- Slope Analysis ----
    st.markdown("### Slope Analysis")
    st.caption("Classified per the Philippine BSWM slope grouping standard.")
    if tin_error:
        st.warning(tin_error)
    else:
        slope = compute_slope_stats(survey_df, tin)
        if slope["error"]:
            st.warning(slope["error"])
        else:
            badge_color = SLOPE_GROUP_COLORS[slope["slope_group"]]
            col1, col2 = st.columns(2)
            col1.metric("Average Slope", f"{slope['average_slope_percent']:.1f} %")
            with col2:
                st.markdown("**Classification (BSWM)**")
                bands = " &middot; ".join(f"{b['group']} {b['range']}" for b in BSWM_SLOPE_GROUPS)
                st.markdown(
                    f"<span class='slope-badge' style='background-color:{badge_color};'>"
                    f"{slope['classification']}</span>"
                    f"<div style='color:#6B5E58;font-size:0.8em;margin-top:6px;'>{bands}</div>",
                    unsafe_allow_html=True,
                )
            if slope["pd705_forestland"]:
                st.caption(
                    "ℹ️ Under Philippine law (PD 705), slopes of 18% or greater are classified "
                    "as forestland rather than alienable & disposable land — informational context only."
                )

    st.divider()

    # ---- Drainage Direction ----
    st.markdown("### Drainage Direction")
    drainage = compute_drainage_direction(survey_df)
    if drainage:
        st.write(
            f"Potential drainage flows from **{drainage['high_point']}** "
            f"({drainage['high_elevation']:.2f} m) toward **{drainage['low_point']}** "
            f"({drainage['low_elevation']:.2f} m), bearing **{drainage['bearing']}** "
            f"over **{drainage['distance']:.1f} m**."
        )

        # Visualize on the contour map with an arrow from high -> low point
        grid = generate_contour_grid(survey_df, interval=1.0)
        if not grid["error"]:
            fig = build_contour_figure(grid, interval=1.0)
            hx, hy = drainage["high_xy"]
            lx, ly = drainage["low_xy"]
            fig.add_annotation(
                x=lx, y=ly, ax=hx, ay=hy,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=2,
                arrowcolor=INK,
            )
            fig.add_trace(
                go.Scatter(
                    x=[hx, lx], y=[hy, ly], mode="markers+text",
                    marker=dict(size=9, color=[MAROON, GOLD], line=dict(color="white", width=1)),
                    text=[f"High: {drainage['high_point']}", f"Low: {drainage['low_point']}"],
                    textposition="top center", textfont=dict(size=10),
                    showlegend=False,
                )
            )
            st.plotly_chart(fig, width="stretch")