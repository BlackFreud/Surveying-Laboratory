"""
pages/7_presentation_mode.py

Presentation Mode — one-click guided demonstration for AUN-QA accreditation
visits. Auto-loads sample survey data and walks through four narrated
steps: Survey Points -> Terrain Surface -> Contour Map -> Engineering
Decision.
"""

from pathlib import Path

import streamlit as st

from modules.data_processing import load_csv_points, validate_points, summarize_points
from modules.terrain_model import generate_tin, build_surface_mesh
from modules.contour import generate_contour_grid
from modules.analysis import compute_elevation_stats, compute_slope_stats, simulate_road_construction
from modules.viz import MAROON, GOLD, INK, SLOPE_GROUP_COLORS, build_terrain_3d_figure, build_contour_figure

SAMPLE_DATA_PATH = Path(__file__).parent.parent / "data" / "survey_points.csv"

STEP_TITLES = [
    "Survey Points",
    "Terrain Surface",
    "Contour Map",
    "Engineering Decision",
]

st.subheader("Presentation Mode")
st.caption("A guided, one-click walkthrough for AUN-QA accreditation demonstrations.")

if "presentation_step" not in st.session_state:
    st.session_state["presentation_step"] = 0  # 0 = not started


def _start_demo():
    with open(SAMPLE_DATA_PATH, "rb") as f:
        df, error = load_csv_points(f)
    if error is None and not validate_points(df):
        st.session_state["survey_points"] = df
    st.session_state["presentation_step"] = 1


def _go_next():
    st.session_state["presentation_step"] = min(4, st.session_state["presentation_step"] + 1)


def _go_back():
    st.session_state["presentation_step"] = max(1, st.session_state["presentation_step"] - 1)


def _restart():
    st.session_state["presentation_step"] = 0


# ---------------------------------------------------------------------------
# Not started yet — show the start button
# ---------------------------------------------------------------------------
if st.session_state["presentation_step"] == 0:
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align:center;'>"
            "<p style='color:#6B5E58;'>This will load the sample survey dataset and step through "
            "the full field-data-to-engineering-decision workflow.</p></div>",
            unsafe_allow_html=True,
        )
        st.button(
            "▶  Start AUN-QA Demonstration",
            on_click=_start_demo,
            type="primary",
            width="stretch",
        )
    st.stop()

# ---------------------------------------------------------------------------
# Step progress indicator
# ---------------------------------------------------------------------------
step = st.session_state["presentation_step"]

pills = []
for i, title in enumerate(STEP_TITLES, start=1):
    if i == step:
        color, weight = MAROON, "700"
    elif i < step:
        color, weight = GOLD, "600"
    else:
        color, weight = "#C9BFB4", "400"
    pills.append(
        f"<span style='color:{color};font-weight:{weight};'>{i}. {title}</span>"
    )
st.markdown(
    "<div style='font-family:\"IBM Plex Mono\",monospace;font-size:0.85rem;"
    "margin-bottom:8px;'>" + " &nbsp;→&nbsp; ".join(pills) + "</div>",
    unsafe_allow_html=True,
)
st.progress(step / 4)

survey_df = st.session_state.get("survey_points")
if survey_df is None or survey_df.empty:
    st.error("Sample data failed to load. Click Restart to try again.")
    st.button("Restart", on_click=_restart)
    st.stop()

tin, tin_error = generate_tin(survey_df)

st.divider()

# ---------------------------------------------------------------------------
# Step 1 — Survey Points
# ---------------------------------------------------------------------------
if step == 1:
    st.markdown("## Step 1 — Survey Points")
    st.write(
        "Every terrain model starts with field data. These points were collected "
        "on-site with a total station — each one records a horizontal position "
        "(Easting, Northing) and an elevation."
    )
    summary = summarize_points(survey_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Points Collected", summary["total_points"])
    col2.metric("Minimum Elevation", f"{summary['min_elevation']:.2f} m")
    col3.metric("Maximum Elevation", f"{summary['max_elevation']:.2f} m")
    st.dataframe(survey_df.head(10), width="stretch")
    st.caption(f"Showing 10 of {len(survey_df)} points.")

# ---------------------------------------------------------------------------
# Step 2 — Terrain Surface
# ---------------------------------------------------------------------------
elif step == 2:
    st.markdown("## Step 2 — Terrain Surface")
    st.write(
        "The survey points are connected into a Triangulated Irregular Network (TIN) — "
        "a mesh of triangles that turns scattered points into a continuous surface, "
        "revealing the shape of the ground."
    )
    if tin_error:
        st.warning(tin_error)
    else:
        mesh = build_surface_mesh(survey_df, tin)
        st.success(f"{mesh['n_triangles']} triangles generated from {len(survey_df)} points.")
        st.plotly_chart(build_terrain_3d_figure(mesh, show_colorbar=True), width="stretch")

# ---------------------------------------------------------------------------
# Step 3 — Contour Map
# ---------------------------------------------------------------------------
elif step == 3:
    st.markdown("## Step 3 — Contour Map")
    st.write(
        "From the terrain surface, we can draw contour lines — each line traces a constant "
        "elevation. This is how engineers read a 3D landscape on a flat, 2D drawing."
    )
    grid = generate_contour_grid(survey_df, interval=1.0)
    if grid["error"]:
        st.warning(grid["error"])
    else:
        st.success(f"Contour interval: 1.0 m — {grid['n_lines']} contour lines generated.")
        st.plotly_chart(build_contour_figure(grid, interval=1.0, survey_df=survey_df), width="stretch")

# ---------------------------------------------------------------------------
# Step 4 — Engineering Decision
# ---------------------------------------------------------------------------
elif step == 4:
    st.markdown("## Step 4 — Engineering Decision")
    st.write(
        "Finally, the terrain model informs real decisions: how steep is the land, which way "
        "will water drain, and — for a proposed road — how much earth needs to be cut or filled."
    )
    elev = compute_elevation_stats(survey_df)
    slope = compute_slope_stats(survey_df, tin) if not tin_error else {"error": tin_error}
    elev_min, elev_max = float(survey_df["Elevation"].min()), float(survey_df["Elevation"].max())
    sim = simulate_road_construction(survey_df, tin, round((elev_min + elev_max) / 2, 2)) if not tin_error else None

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Elevation**")
        st.markdown(
            f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.3rem;color:{MAROON};'>"
            f"{elev['elevation_difference']:.2f} m</span> relief",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("**Slope**")
        if slope.get("error"):
            st.caption(slope["error"])
        else:
            badge_color = SLOPE_GROUP_COLORS[slope["slope_group"]]
            st.markdown(
                f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.3rem;color:{MAROON};'>"
                f"{slope['average_slope_percent']:.1f}%</span> "
                f"<span class='slope-badge' style='background-color:{badge_color};font-size:0.7rem;'>"
                f"{slope['classification']}</span>",
                unsafe_allow_html=True,
            )
    with col3:
        st.markdown("**Road Earthwork**")
        if sim:
            net_label = "Net Cut" if sim["net_cut"] >= 0 else "Net Fill"
            st.markdown(
                f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:1.3rem;color:{MAROON};'>"
                f"{abs(sim['net_cut']):.0f} m³</span> {net_label}",
                unsafe_allow_html=True,
            )

    st.info(
        "This is the full workflow: **Field Survey Data → Coordinate Processing → "
        "Terrain Surface Generation → Contour Mapping → Engineering Interpretation** — "
        "the same pipeline a surveying team uses on a real project."
    )

# ---------------------------------------------------------------------------
# Navigation controls
# ---------------------------------------------------------------------------
st.divider()
nav_back, nav_restart, nav_next = st.columns([1, 1, 1])
with nav_back:
    st.button("⬅ Back", on_click=_go_back, disabled=(step == 1), width="stretch")
with nav_restart:
    st.button("↻ Restart", on_click=_restart, width="stretch")
with nav_next:
    if step < 4:
        st.button("Next ➡", on_click=_go_next, type="primary", width="stretch")
    else:
        st.button("Finish ✓", on_click=_restart, type="primary", width="stretch")