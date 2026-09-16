"""Tests for modules.components."""

from __future__ import annotations

import pandas as pd

from modules.analysis import (
    compute_elevation_stats,
    compute_slope_stats,
    simulate_road_construction,
)
from modules.components import render_engineering_summary
from modules.terrain_model import generate_tin


def test_render_engineering_summary_full(sample_survey_df: pd.DataFrame) -> None:
    """Test rendering summary with valid elevation, slope, and road simulation."""
    elev = compute_elevation_stats(sample_survey_df)
    tin, error = generate_tin(sample_survey_df)
    assert tin is not None
    assert error is None
    slope = compute_slope_stats(sample_survey_df, tin)
    sim = simulate_road_construction(sample_survey_df, tin, road_elevation=55.0)

    # Should execute without throwing errors
    render_engineering_summary(elev, slope, sim, font_size="1.3rem")


def test_render_engineering_summary_empty(empty_df: pd.DataFrame) -> None:
    """Test rendering summary when no data is provided."""
    elev = compute_elevation_stats(empty_df)
    slope = compute_slope_stats(empty_df, None)

    # Should safely display fallback text without exception
    render_engineering_summary(elev, slope, None)
