"""
viz.py

Shared Plotly chart builders for the DTM Simulator, plus the brand design
tokens (colors sampled from the UM / CEE seals) used consistently across
every page. Centralizing this avoids duplicating chart-construction code
between the Terrain, Contour, Analysis, and Scenario Simulation pages.
"""

from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
MAROON = "#AE2431"
GOLD = "#F2C230"
TERRACOTTA = "#963C2D"
PAPER = "#FAF7F2"
INK = "#2B1A19"

SLOPE_GROUP_COLORS = {
    "A": "#4A7856", "B": "#6E8F4E", "C": "#D99A2B",
    "D": "#C67C3E", "E": "#963C2D", "F": "#7A1F2B",
}

# Sequential colorscale used across all elevation visualizations, derived
# from the brand palette (pale paper -> gold -> terracotta -> maroon) instead
# of a generic default, so every chart reads as part of the same identity.
BRAND_COLORSCALE = [
    [0.0, "#FAF3E6"],
    [0.3, "#F2C230"],
    [0.6, "#C67C3E"],
    [0.8, "#963C2D"],
    [1.0, "#6B1520"],
]

CHART_HEIGHT = 450
CHART_MARGIN = dict(l=10, r=10, t=10, b=10)


def _triangulation_edges(mesh: dict) -> tuple[list, list]:
    """Build the (x, y) line-segment arrays (with None breaks) that draw
    every triangle edge in a TIN, for a 2D triangulation overlay."""
    edge_x, edge_y = [], []
    for tri in mesh["triangles"]:
        pts = list(tri) + [tri[0]]  # close the triangle
        for i in range(3):
            edge_x += [mesh["x"][pts[i]], mesh["x"][pts[i + 1]], None]
            edge_y += [mesh["y"][pts[i]], mesh["y"][pts[i + 1]], None]
    return edge_x, edge_y


def build_terrain_2d_figure(mesh: dict, survey_df: pd.DataFrame) -> go.Figure:
    """2D scatter of survey points colored by elevation, with the TIN
    triangulation edges overlaid. Used on the Terrain Surface Generation page."""
    edge_x, edge_y = _triangulation_edges(mesh)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="lightgray", width=1),
            hoverinfo="skip", showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=mesh["x"], y=mesh["y"], mode="markers",
            marker=dict(
                size=8, color=mesh["z"], colorscale=BRAND_COLORSCALE,
                colorbar=dict(title="Elev (m)"), showscale=True,
            ),
            text=survey_df["Point"],
            hovertemplate="Point %{text}<br>E: %{x}<br>N: %{y}<extra></extra>",
            name="Elevation Points",
        )
    )
    fig.update_layout(
        xaxis_title="Easting", yaxis_title="Northing",
        height=CHART_HEIGHT, margin=CHART_MARGIN,
    )
    return fig


def build_terrain_3d_figure(
    mesh: dict,
    show_colorbar: bool = True,
    road_plane_elevation: Optional[float] = None,
) -> go.Figure:
    """3D mesh surface of the terrain. Used on both the Terrain Surface
    Generation page and the Scenario Simulation page (with an optional
    translucent road plane overlaid at `road_plane_elevation`)."""
    fig = go.Figure()
    fig.add_trace(
        go.Mesh3d(
            x=mesh["x"], y=mesh["y"], z=mesh["z"],
            i=mesh["triangles"][:, 0], j=mesh["triangles"][:, 1], k=mesh["triangles"][:, 2],
            intensity=mesh["z"], colorscale=BRAND_COLORSCALE,
            colorbar=dict(title="Elev (m)") if show_colorbar else None,
            showscale=show_colorbar,
            name="Terrain",
        )
    )

    if road_plane_elevation is not None:
        x, y = mesh["x"], mesh["y"]
        fig.add_trace(
            go.Mesh3d(
                x=[x.min(), x.max(), x.max(), x.min()],
                y=[y.min(), y.min(), y.max(), y.max()],
                z=[road_plane_elevation] * 4,
                i=[0, 0], j=[1, 2], k=[2, 3],
                color=TERRACOTTA, opacity=0.35, name="Road Plane",
            )
        )

    fig.update_layout(
        scene=dict(xaxis_title="Easting", yaxis_title="Northing", zaxis_title="Elevation"),
        height=CHART_HEIGHT, margin=CHART_MARGIN, showlegend=False,
    )
    return fig


def build_contour_figure(grid: dict, interval: float, survey_df: Optional[pd.DataFrame] = None) -> go.Figure:
    """Filled contour map (color elevation map + labeled contour lines) from
    an interpolated grid. Used standalone on the Contour Generation page, and
    as the base layer for the Drainage Direction visualization (which adds
    its own arrow/markers on top of the returned figure)."""
    fig = go.Figure(
        data=go.Contour(
            x=grid["grid_x"], y=grid["grid_y"], z=grid["grid_z"],
            colorscale=BRAND_COLORSCALE,
            contours=dict(
                start=float(grid["levels"][0]), end=float(grid["levels"][-1]),
                size=interval, showlabels=True, labelfont=dict(size=10, color=INK),
            ),
            colorbar=dict(title="Elev (m)"),
            line_smoothing=0.85,
        )
    )
    if survey_df is not None:
        fig.add_trace(
            go.Scatter(
                x=survey_df["Easting"], y=survey_df["Northing"],
                mode="markers+text",
                marker=dict(size=6, color=INK, line=dict(color="white", width=1)),
                text=survey_df["Point"], textposition="top center",
                textfont=dict(size=9),
                name="Survey Points",
            )
        )
    fig.update_layout(
        xaxis_title="Easting", yaxis_title="Northing",
        height=550 if survey_df is None else CHART_HEIGHT,
        margin=CHART_MARGIN,
    )
    return fig


def build_cutfill_figure(triangles: list) -> go.Figure:
    """2D plan-view cut/fill map: each TIN triangle filled maroon (cut) or
    gold (fill) depending on its relation to the proposed road elevation.
    Used on the Scenario Simulation page."""
    fig = go.Figure()
    shown_cut, shown_fill = False, False

    for tri in triangles:
        is_cut = tri["type"] == "cut"
        color = MAROON if is_cut else GOLD
        show_legend = (is_cut and not shown_cut) or (not is_cut and not shown_fill)
        if is_cut:
            shown_cut = True
        else:
            shown_fill = True

        fig.add_trace(
            go.Scatter(
                x=tri["x"] + [tri["x"][0]], y=tri["y"] + [tri["y"][0]],
                mode="lines", fill="toself",
                line=dict(color="white", width=0.5),
                fillcolor=color, opacity=0.85,
                name="Cut" if is_cut else "Fill",
                legendgroup=tri["type"], showlegend=show_legend,
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        xaxis_title="Easting", yaxis_title="Northing",
        height=CHART_HEIGHT, margin=CHART_MARGIN,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig