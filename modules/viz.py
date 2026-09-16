"""
viz.py

Shared Plotly chart builders for the DTM Simulator, plus the brand design
tokens (colors sampled from the UM / CEE seals) used consistently across
every page. Centralizing this avoids duplicating chart-construction code
between the Terrain, Contour, Analysis, and Scenario Simulation pages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go

if TYPE_CHECKING:
    from modules.analysis import CutFillTriangle
    from modules.contour import ContourGrid
    from modules.terrain_model import SurfaceMesh

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
MAROON = "#AE2431"
GOLD = "#F2C230"
TERRACOTTA = "#963C2D"
PAPER = "#FAF7F2"
INK = "#2B1A19"
MUTED = "#6B5E58"
MUTED_LIGHT = "#9C9088"
BORDER = "#E5DFD5"
DISABLED = "#C9BFB4"

SLOPE_GROUP_COLORS = {
    "A": "#4A7856",
    "B": "#6E8F4E",
    "C": "#D99A2B",
    "D": "#C67C3E",
    "E": "#963C2D",
    "F": "#7A1F2B",
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
CHART_MARGIN = {"l": 10, "r": 10, "t": 10, "b": 10}


def _triangulation_edges(
    mesh: SurfaceMesh,
) -> tuple[list[float | None], list[float | None]]:
    """Build the (x, y) line-segment arrays (with None breaks) that draw
    every triangle edge in a TIN, for a 2D triangulation overlay."""
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for tri in mesh["triangles"]:
        pts = [tri[0], tri[1], tri[2], tri[0]]  # close the triangle
        for i in range(3):
            edge_x.extend([mesh["x"][pts[i]], mesh["x"][pts[i + 1]], None])
            edge_y.extend([mesh["y"][pts[i]], mesh["y"][pts[i + 1]], None])
    return edge_x, edge_y


def build_terrain_2d_figure(
    mesh: SurfaceMesh,
    survey_df: pd.DataFrame,
) -> go.Figure:
    """2D scatter of survey points colored by elevation, with the TIN
    triangulation edges overlaid. Used on the Terrain Surface Generation page."""
    edge_x, edge_y = _triangulation_edges(mesh)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line={"color": "lightgray", "width": 1},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=mesh["x"],
            y=mesh["y"],
            mode="markers",
            marker={
                "size": 8,
                "color": mesh["z"],
                "colorscale": BRAND_COLORSCALE,
                "colorbar": {"title": "Elev (m)"},
                "showscale": True,
            },
            text=survey_df["Point"],
            hovertemplate="Point %{text}<br>E: %{x}<br>N: %{y}<extra></extra>",
            name="Elevation Points",
        )
    )
    fig.update_layout(
        xaxis_title="Easting",
        yaxis_title="Northing",
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
    )
    return fig


def build_terrain_3d_figure(
    mesh: SurfaceMesh,
    show_colorbar: bool = True,
    road_plane_elevation: float | None = None,
) -> go.Figure:
    """3D mesh surface of the terrain. Used on both the Terrain Surface
    Generation page and the Scenario Simulation page (with an optional
    translucent road plane overlaid at `road_plane_elevation`)."""
    fig = go.Figure()
    fig.add_trace(
        go.Mesh3d(
            x=mesh["x"],
            y=mesh["y"],
            z=mesh["z"],
            i=mesh["triangles"][:, 0],
            j=mesh["triangles"][:, 1],
            k=mesh["triangles"][:, 2],
            intensity=mesh["z"],
            colorscale=BRAND_COLORSCALE,
            colorbar={"title": "Elev (m)"} if show_colorbar else None,
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
                i=[0, 0],
                j=[1, 2],
                k=[2, 3],
                color=TERRACOTTA,
                opacity=0.35,
                name="Road Plane",
            )
        )

    fig.update_layout(
        scene={
            "xaxis_title": "Easting",
            "yaxis_title": "Northing",
            "zaxis_title": "Elevation",
        },
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        showlegend=False,
    )
    return fig


def build_contour_figure(
    grid: ContourGrid,
    interval: float,
    survey_df: pd.DataFrame | None = None,
) -> go.Figure:
    """Filled contour map (color elevation map + labeled contour lines) from
    an interpolated grid. Used standalone on the Contour Generation page, and
    as the base layer for the Drainage Direction visualization (which adds
    its own arrow/markers on top of the returned figure)."""
    levels = grid.get("levels")
    start_level = float(levels[0]) if levels is not None and len(levels) > 0 else 0.0
    end_level = float(levels[-1]) if levels is not None and len(levels) > 0 else 0.0

    fig = go.Figure(
        data=go.Contour(
            x=grid.get("grid_x"),
            y=grid.get("grid_y"),
            z=grid.get("grid_z"),
            colorscale=BRAND_COLORSCALE,
            contours={
                "start": start_level,
                "end": end_level,
                "size": interval,
                "showlabels": True,
                "labelfont": {"size": 10, "color": INK},
            },
            colorbar={"title": "Elev (m)"},
            line_smoothing=0.85,
        )
    )
    if survey_df is not None:
        fig.add_trace(
            go.Scatter(
                x=survey_df["Easting"],
                y=survey_df["Northing"],
                mode="markers+text",
                marker={
                    "size": 6,
                    "color": INK,
                    "line": {"color": "white", "width": 1},
                },
                text=survey_df["Point"],
                textposition="top center",
                textfont={"size": 9},
                name="Survey Points",
            )
        )
    fig.update_layout(
        xaxis_title="Easting",
        yaxis_title="Northing",
        height=550 if survey_df is None else CHART_HEIGHT,
        margin=CHART_MARGIN,
    )
    return fig


def build_cutfill_figure(triangles: list[CutFillTriangle]) -> go.Figure:
    """2D plan-view cut/fill map: TIN triangles colored maroon (cut) or
    gold (fill) based on their relation to the proposed road elevation.

    Uses two traces total (one cut, one fill) with ``None``-separated
    polygon paths instead of one trace per triangle, so the chart stays
    responsive even with thousands of triangles.
    """
    cut_x: list[float | None] = []
    cut_y: list[float | None] = []
    fill_x: list[float | None] = []
    fill_y: list[float | None] = []

    for tri in triangles:
        # Close the polygon and append a None separator
        xs = tri["x"] + [tri["x"][0], None]
        ys = tri["y"] + [tri["y"][0], None]
        if tri["type"] == "cut":
            cut_x.extend(xs)
            cut_y.extend(ys)
        else:
            fill_x.extend(xs)
            fill_y.extend(ys)

    fig = go.Figure()

    if cut_x:
        fig.add_trace(
            go.Scatter(
                x=cut_x,
                y=cut_y,
                mode="lines",
                fill="toself",
                line={"color": "white", "width": 0.5},
                fillcolor=MAROON,
                opacity=0.85,
                name="Cut",
                hoverinfo="skip",
            )
        )
    if fill_x:
        fig.add_trace(
            go.Scatter(
                x=fill_x,
                y=fill_y,
                mode="lines",
                fill="toself",
                line={"color": "white", "width": 0.5},
                fillcolor=GOLD,
                opacity=0.85,
                name="Fill",
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        xaxis_title="Easting",
        yaxis_title="Northing",
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )
    return fig
