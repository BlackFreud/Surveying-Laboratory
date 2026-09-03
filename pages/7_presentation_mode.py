"""
pages/7_presentation_mode.py

Presentation Mode — one-click guided demonstration for laboratory
visits. Loads a chosen sample dataset and walks through four narrated
steps: Survey Points -> Terrain Surface -> Contour Map -> Engineering
Decision. Supports both manual Back/Next navigation and a timed
auto-advance mode for unattended or hands-free presenting.
"""

import time

import streamlit as st

from modules.data_processing import load_csv_points, validate_points, summarize_points
from modules.terrain_model import generate_tin, build_surface_mesh
from modules.contour import generate_contour_grid
from modules.analysis import compute_elevation_stats, compute_slope_stats, simulate_road_construction
from modules.viz import MAROON, GOLD, INK, SLOPE_GROUP_COLORS, build_terrain_3d_figure, build_contour_figure
from modules.samples import SAMPLE_DATASETS

STEP_TITLES = [
    "Survey Points",
    "Terrain Surface",
    "Contour Map",
    "Engineering Decision",
]

AUTO_ADVANCE_INTERVALS = [5, 8, 10, 15]

st.subheader("Presentation Mode")
st.caption("A guided, one-click walkthrough for laboratory demonstrations.")

if "presentation_step" not in st.session_state:
    st.session_state["presentation_step"] = 0  # 0 = not started
if "auto_advance_enabled" not in st.session_state:
    st.session_state["auto_advance_enabled"] = True
if "auto_advance_interval" not in st.session_state:
    st.session_state["auto_advance_interval"] = 8


def _start_demo(sample_index: int):
    with open(SAMPLE_DATASETS[sample_index]["path"], "rb") as f:
        df, error = load_csv_points(f)
    if error is None and not validate_points(df):
        st.session_state["survey_points"] = df
    st.session_state["presentation_step"] = 1
    st.session_state["step_started_at"] = time.time()


def _go_next():
    st.session_state["presentation_step"] = min(4, st.session_state["presentation_step"] + 1)
    st.session_state["step_started_at"] = time.time()


def _go_back():
    st.session_state["presentation_step"] = max(1, st.session_state["presentation_step"] - 1)
    st.session_state["step_started_at"] = time.time()


def _restart():
    st.session_state["presentation_step"] = 0


# ---------------------------------------------------------------------------
# Not started yet — show sample choice, auto-advance options, and start button
# ---------------------------------------------------------------------------
if st.session_state["presentation_step"] == 0:
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align:center;'>"
            "<p style='color:#6B5E58;'>Choose a sample terrain, then start the guided walkthrough "
            "of the full field-data-to-engineering-decision workflow.</p></div>",
            unsafe_allow_html=True,
        )

        sample_index = st.selectbox(
            "Sample dataset",
            options=range(len(SAMPLE_DATASETS)),
            format_func=lambda i: SAMPLE_DATASETS[i]["label"],
            key="presentation_sample_choice",
        )
        st.caption(SAMPLE_DATASETS[sample_index]["description"])

        col_toggle, col_interval = st.columns(2)
        with col_toggle:
            st.checkbox("Auto-advance slides", key="auto_advance_enabled")
        with col_interval:
            st.selectbox(
                "Seconds per slide",
                options=AUTO_ADVANCE_INTERVALS,
                key="auto_advance_interval",
                disabled=not st.session_state["auto_advance_enabled"],
            )

        st.button(
            "▶  Start Demonstration",
            on_click=_start_demo,
            args=(sample_index,),
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

auto_on = st.session_state["auto_advance_enabled"]
interval = st.session_state["auto_advance_interval"]

nav_back, nav_restart, nav_next, nav_auto = st.columns([1, 1, 1, 1.3])
with nav_back:
    st.button("⬅ Back", on_click=_go_back, disabled=(step == 1), width="stretch")
with nav_restart:
    st.button("↻ Restart", on_click=_restart, width="stretch")
with nav_next:
    if step < 4:
        st.button("Next ➡", on_click=_go_next, type="primary", width="stretch")
    else:
        st.button("Finish ✓", on_click=_restart, type="primary", width="stretch")
with nav_auto:
    st.checkbox("Auto-advance", key="auto_advance_enabled", value=auto_on)

# ---------------------------------------------------------------------------
# Auto-advance timer — ticks the page every ~1s while enabled, advancing to
# the next step once the configured interval has elapsed. Stops on its own
# after Step 4 rather than looping, so an unattended kiosk doesn't restart
# without a deliberate click.
# ---------------------------------------------------------------------------
if st.session_state["auto_advance_enabled"] and step < 4:
    elapsed = time.time() - st.session_state.get("step_started_at", time.time())
    remaining = interval - elapsed
    if remaining <= 0:
        _go_next()
        st.rerun()
    else:
        st.caption(f"⏱ Auto-advancing in {remaining:.0f}s — untick Auto-advance to pause.")
        time.sleep(min(1.0, remaining))
        st.rerun()
elif st.session_state["auto_advance_enabled"] and step == 4:
    st.caption("✓ Presentation complete — click Restart to run it again.")