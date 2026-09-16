"""components.py

Reusable Streamlit UI components shared across pages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from modules.analysis import BSWM_SLOPE_GROUPS
from modules.viz import MAROON, MUTED, SLOPE_GROUP_COLORS

if TYPE_CHECKING:
    from modules.analysis import ElevationStats, RoadSimResult, SlopeStats


def render_engineering_summary(
    elev: ElevationStats,
    slope: SlopeStats,
    sim: RoadSimResult | None = None,
    *,
    font_size: str = "1.4rem",
) -> None:
    """Render the three-column Elevation / Slope / Volume summary.

    Args:
        elev: Result from compute_elevation_stats().
        slope: Result from compute_slope_stats().
        sim: Optional result from simulate_road_construction().
        font_size: CSS font-size for the hero metric values.
    """
    col_e, col_s, col_v = st.columns(3)

    with col_e:
        st.markdown("**Elevation**")
        diff_text = (
            f"{elev['elevation_difference']:.2f} m"
            if elev["elevation_difference"] is not None
            else "N/A"
        )
        # SAFETY: HTML is entirely server-generated; no user input is interpolated.
        st.markdown(
            f'<span style=\'font-family:"IBM Plex Mono",monospace;'
            f"font-size:{font_size};color:{MAROON};'>"
            f"{diff_text}</span> relief",
            unsafe_allow_html=True,
        )
        if (
            elev["lowest_elevation"] is not None
            and elev["highest_elevation"] is not None
        ):
            st.caption(
                f"{elev['lowest_elevation']:.2f} \u2013 "
                f"{elev['highest_elevation']:.2f} m"
            )
        else:
            st.caption("No elevation data")

    with col_s:
        st.markdown("**Slope**")
        if slope.get("error"):
            st.caption(slope["error"])
        else:
            badge_color = SLOPE_GROUP_COLORS[slope["slope_group"]]
            # SAFETY: HTML is entirely server-generated.
            st.markdown(
                f'<span style=\'font-family:"IBM Plex Mono",monospace;'
                f"font-size:{font_size};color:{MAROON};'>"
                f"{slope['average_slope_percent']:.1f}%</span> "
                f"<span class='slope-badge' style='background-color:"
                f"{badge_color};font-size:0.75rem;'>"
                f"{slope['classification']}</span>",
                unsafe_allow_html=True,
            )

            bands = " &middot; ".join(
                f"{b['group']} {b['range']}" for b in BSWM_SLOPE_GROUPS
            )
            st.markdown(
                f"<div style='color:{MUTED};font-size:0.8em;margin-top:6px;'>{bands}</div>",
                unsafe_allow_html=True,
            )

            if slope.get("pd705_forestland"):
                st.caption(
                    "ℹ️ Under Philippine law (PD 705), slopes of 18% or greater are classified "
                    "as forestland rather than alienable & disposable land — informational context only."
                )

    with col_v:
        if sim is not None and sim.get("error") is None:
            net_cut = sim.get("net_cut")
            cut_vol = sim.get("cut_volume")
            fill_vol = sim.get("fill_volume")
            if net_cut is not None and cut_vol is not None and fill_vol is not None:
                st.markdown("**Volume (at midpoint road elevation)**")
                net_label = "Net Cut" if net_cut >= 0 else "Net Fill"
                # SAFETY: HTML is entirely server-generated.
                st.markdown(
                    f'<span style=\'font-family:"IBM Plex Mono",monospace;'
                    f"font-size:{font_size};color:{MAROON};'>"
                    f"{abs(net_cut):.0f} m\u00b3</span> {net_label}",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Cut {cut_vol:.0f} m\u00b3 \u00b7 Fill {fill_vol:.0f} m\u00b3"
                )
