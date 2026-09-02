"""
pages/6_aunqa_dashboard.py

Exhibit Dashboard — a single consolidated screen for laboratory
demonstrations: upload/load data, 2D contour map, 3D terrain model, and a
condensed Elevation / Slope / Volume engineering summary, per the original
exhibit spec's dashboard layout.
"""

from pathlib import Path

import streamlit as st

from modules.data_processing import load_csv_points, validate_points, summarize_points
from modules.terrain_model import generate_tin, build_surface_mesh
from modules.contour import generate_contour_grid
from modules.analysis import compute_elevation_stats, compute_slope_stats, simulate_road_construction
from modules.viz import SLOPE_GROUP_COLORS, build_contour_figure, build_terrain_3d_figure

SAMPLE_DATA_PATH = Path(__file__).parent.parent / "data" / "survey_points.csv"

st.subheader("Exhibit Dashboard")
st.caption("Consolidated view: survey data, terrain surface, contour map, and engineering summary.")

# ---------------------------------------------------------------------------
# Upload Survey Data (compact — full manual-entry workflow lives on the
# Survey Data Input page; this is the fast path for a live demonstration)
# ---------------------------------------------------------------------------
survey_df = st.session_state.get("survey_points")

with st.container(border=True):
    st.markdown("**Upload Survey Data**")
    col_upload, col_sample = st.columns([3, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload survey_points.csv", type=["csv"], key="dashboard_csv_uploader",
            label_visibility="collapsed",
        )
    with col_sample:
        load_sample = st.button("Load Sample Data", width="stretch")

    if uploaded_file is not None:
        new_df, csv_error = load_csv_points(uploaded_file)
        if csv_error:
            st.error(csv_error)
        else:
            issues = validate_points(new_df)
            if issues:
                st.warning("Validation issues: " + "; ".join(issues))
            else:
                st.session_state["survey_points"] = new_df
                survey_df = new_df

    if load_sample:
        with open(SAMPLE_DATA_PATH, "rb") as f:
            new_df, csv_error = load_csv_points(f)
        if csv_error:
            st.error(csv_error)
        else:
            issues = validate_points(new_df)
            if issues:
                st.warning("Sample data validation issues: " + "; ".join(issues))
            else:
                st.session_state["survey_points"] = new_df
                survey_df = new_df

    if survey_df is not None and not survey_df.empty:
        summary = summarize_points(survey_df)
        st.caption(
            f"✅ {summary['total_points']} points loaded &nbsp;·&nbsp; "
            f"Elevation {summary['min_elevation']:.2f}\u2013{summary['max_elevation']:.2f} m",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No survey data loaded yet. Upload a CSV or click **Load Sample Data**.")

if survey_df is None or survey_df.empty:
    st.stop()

tin, tin_error = generate_tin(survey_df)
if tin_error:
    st.error(tin_error)
    st.stop()

# ---------------------------------------------------------------------------
# 2D Contour Map + 3D Terrain Model, side by side
# ---------------------------------------------------------------------------
st.write("")
col_contour, col_terrain = st.columns(2)

with col_contour:
    st.markdown("**2D Contour Map**")
    grid = generate_contour_grid(survey_df, interval=1.0)
    if grid["error"]:
        st.warning(grid["error"])
    else:
        st.plotly_chart(build_contour_figure(grid, interval=1.0, survey_df=survey_df), width="stretch")

with col_terrain:
    st.markdown("**3D Terrain Model**")
    mesh = build_surface_mesh(survey_df, tin)
    st.plotly_chart(build_terrain_3d_figure(mesh, show_colorbar=True), width="stretch")

# ---------------------------------------------------------------------------
# Engineering Analysis summary — Elevation / Slope / Volume
# ---------------------------------------------------------------------------
st.write("")
st.markdown("**Engineering Analysis**")

elev = compute_elevation_stats(survey_df)
slope = compute_slope_stats(survey_df, tin)
elev_min = float(survey_df["Elevation"].min())
elev_max = float(survey_df["Elevation"].max())
sim = simulate_road_construction(survey_df, tin, round((elev_min + elev_max) / 2, 2))

col_e, col_s, col_v = st.columns(3)

with col_e:
    st.markdown("Elevation")
    st.markdown(
        f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.4rem;color:#AE2431;'>"
        f"{elev['elevation_difference']:.2f} m</span> relief",
        unsafe_allow_html=True,
    )
    st.caption(f"{elev['lowest_elevation']:.2f} \u2013 {elev['highest_elevation']:.2f} m")

with col_s:
    st.markdown("Slope")
    if slope["error"]:
        st.caption(slope["error"])
    else:
        badge_color = SLOPE_GROUP_COLORS[slope["slope_group"]]
        st.markdown(
            f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.4rem;color:#AE2431;'>"
            f"{slope['average_slope_percent']:.1f}%</span> "
            f"<span class='slope-badge' style='background-color:{badge_color};font-size:0.75rem;'>"
            f"{slope['classification']}</span>",
            unsafe_allow_html=True,
        )
        st.caption("Philippine BSWM classification")

with col_v:
    st.markdown("Volume (at midpoint road elevation)")
    net_label = "Net Cut" if sim["net_cut"] >= 0 else "Net Fill"
    st.markdown(
        f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.4rem;color:#AE2431;'>"
        f"{abs(sim['net_cut']):.0f} m³</span> {net_label}",
        unsafe_allow_html=True,
    )
    st.caption(f"Cut {sim['cut_volume']:.0f} m³ \u00b7 Fill {sim['fill_volume']:.0f} m³")

# ---------------------------------------------------------------------------
# Sign-off
# ---------------------------------------------------------------------------
st.markdown(
    "<div style='text-align:center;margin-top:32px;padding-top:16px;"
    "border-top:2px solid #AE2431;color:#6B5E58;font-family:\"IBM Plex Mono\",monospace;"
    "font-size:0.8rem;letter-spacing:0.05em;'>"
    "SURVEYING LABORATORY &nbsp;&middot;&nbsp; UNIVERSITY OF MINDANAO"
    "<div style='margin-top:4px;font-size:0.7rem;letter-spacing:0.02em;color:#9C9088;'>"
    "Developed by Engr. JF Item &mdash; Laboratory Custodian</div></div>",
    unsafe_allow_html=True,
)