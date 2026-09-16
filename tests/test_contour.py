"""Tests for modules.contour."""

from __future__ import annotations

import pandas as pd

from modules.contour import generate_contour_grid


class TestGenerateContourGrid:
    def test_valid_contour(self, sample_survey_df: pd.DataFrame) -> None:
        grid = generate_contour_grid(sample_survey_df, interval=1.0)
        assert grid["error"] is None
        assert grid["n_lines"] > 0
        assert grid["grid_x"] is not None
        assert grid["grid_z"] is not None
        assert grid["grid_z"].shape == (100, 100)

    def test_too_few_points(self, two_point_df: pd.DataFrame) -> None:
        grid = generate_contour_grid(two_point_df, interval=1.0)
        assert grid["error"] is not None

    def test_interval_larger_than_range(self, sample_survey_df: pd.DataFrame) -> None:
        grid = generate_contour_grid(sample_survey_df, interval=999.0)
        assert grid["error"] is not None
        assert "smaller" in grid["error"].lower() or "interval" in grid["error"].lower()

    def test_custom_resolution(self, sample_survey_df: pd.DataFrame) -> None:
        grid = generate_contour_grid(sample_survey_df, interval=1.0, resolution=50)
        assert grid["error"] is None
        assert grid["grid_z"] is not None
        assert grid["grid_z"].shape == (50, 50)

    def test_empty_input(self, empty_df: pd.DataFrame) -> None:
        grid = generate_contour_grid(empty_df, interval=1.0)
        assert grid["error"] is not None
