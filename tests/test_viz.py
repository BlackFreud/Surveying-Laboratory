"""Tests for modules.viz."""

from __future__ import annotations

import pandas as pd

from modules.analysis import simulate_road_construction
from modules.contour import generate_contour_grid
from modules.terrain_model import build_surface_mesh, generate_tin
from modules.viz import (
    build_contour_figure,
    build_cutfill_figure,
    build_terrain_2d_figure,
    build_terrain_3d_figure,
)


def test_build_terrain_figures(sample_survey_df: pd.DataFrame) -> None:
    """Verify 2D and 3D terrain Plotly figure construction."""
    tin, error = generate_tin(sample_survey_df)
    assert tin is not None
    assert error is None
    mesh = build_surface_mesh(sample_survey_df, tin)

    fig_2d = build_terrain_2d_figure(mesh, sample_survey_df)
    assert fig_2d is not None
    assert len(fig_2d.data) >= 2

    fig_3d = build_terrain_3d_figure(mesh, show_colorbar=True, road_plane_elevation=55.0)
    assert fig_3d is not None
    assert len(fig_3d.data) == 2


def test_build_contour_figure(sample_survey_df: pd.DataFrame) -> None:
    """Verify contour figure generation."""
    grid = generate_contour_grid(sample_survey_df, interval=1.0)
    assert grid["error"] is None

    fig = build_contour_figure(grid, interval=1.0, survey_df=sample_survey_df)
    assert fig is not None
    assert len(fig.data) >= 1


def test_build_cutfill_figure(sample_survey_df: pd.DataFrame) -> None:
    """Verify batched cut/fill figure generation creates at most 2 traces."""
    tin, error = generate_tin(sample_survey_df)
    assert tin is not None
    assert error is None
    sim = simulate_road_construction(sample_survey_df, tin, road_elevation=55.0)

    fig = build_cutfill_figure(sim["triangles"])
    assert fig is not None
    # Maximum 2 traces: one for cut, one for fill
    assert len(fig.data) <= 2
