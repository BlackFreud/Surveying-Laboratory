"""Tests for modules.analysis."""

from __future__ import annotations

import pandas as pd
import pytest
from scipy.spatial import Delaunay, QhullError

from modules.analysis import (
    _azimuth_to_bearing,
    classify_slope,
    compute_drainage_direction,
    compute_elevation_stats,
    compute_slope_stats,
    simulate_road_construction,
)


class TestClassifySlope:
    """Test BSWM slope classification at every boundary."""

    @pytest.mark.parametrize(
        "slope, expected_group",
        [
            (0.0, "A"),
            (1.9, "A"),
            (2.0, "B"),
            (5.9, "B"),
            (6.0, "C"),
            (11.9, "C"),
            (12.0, "D"),
            (19.9, "D"),
            (20.0, "E"),
            (29.9, "E"),
            (30.0, "F"),
            (100.0, "F"),
        ],
    )
    def test_group_boundaries(self, slope: float, expected_group: str) -> None:
        result = classify_slope(slope)
        assert result["group"] == expected_group

    def test_pd705_below_threshold(self) -> None:
        result = classify_slope(17.9)
        assert result["pd705_forestland"] is False

    def test_pd705_at_threshold(self) -> None:
        result = classify_slope(18.0)
        assert result["pd705_forestland"] is True

    def test_label_format(self) -> None:
        result = classify_slope(5.0)
        assert "B" in result["label"]
        assert "Gently sloping" in result["label"]


class TestAzimuthToBearing:
    """Test all four quadrant conversions."""

    @pytest.mark.parametrize(
        "azimuth, expected",
        [
            (0, "N0\u00b0E"),
            (45, "N45\u00b0E"),
            (90, "S90\u00b0E"),
            (135, "S45\u00b0E"),
            (180, "S0\u00b0W"),
            (225, "S45\u00b0W"),
            (270, "N90\u00b0W"),
            (315, "N45\u00b0W"),
        ],
    )
    def test_quadrant(self, azimuth: float, expected: str) -> None:
        assert _azimuth_to_bearing(azimuth) == expected


class TestComputeElevationStats:
    def test_normal(self, sample_survey_df: pd.DataFrame) -> None:
        stats = compute_elevation_stats(sample_survey_df)
        assert stats["highest_elevation"] == 60.0
        assert stats["lowest_elevation"] == 50.0
        assert stats["elevation_difference"] == 10.0

    def test_empty(self, empty_df: pd.DataFrame) -> None:
        stats = compute_elevation_stats(empty_df)
        assert stats["highest_elevation"] is None


class TestComputeSlopeStats:
    def test_flat_terrain(self, flat_df: pd.DataFrame) -> None:
        tin, _ = generate_tin_uncached(flat_df)
        slope = compute_slope_stats(flat_df, tin)
        assert slope["error"] is None
        assert slope["average_slope_percent"] == pytest.approx(0.0, abs=0.01)
        assert slope["slope_group"] == "A"

    def test_sloped_terrain(self, sample_survey_df: pd.DataFrame) -> None:
        tin, _ = generate_tin_uncached(sample_survey_df)
        slope = compute_slope_stats(sample_survey_df, tin)
        assert slope["error"] is None
        assert slope["average_slope_percent"] is not None
        assert slope["average_slope_percent"] > 0

    def test_none_tin(self, sample_survey_df: pd.DataFrame) -> None:
        slope = compute_slope_stats(sample_survey_df, None)
        assert slope["error"] is not None


class TestComputeDrainageDirection:
    def test_has_bearing(self, sample_survey_df: pd.DataFrame) -> None:
        result = compute_drainage_direction(sample_survey_df)
        assert "bearing" in result
        assert "distance" in result
        assert result["high_elevation"] > result["low_elevation"]

    def test_empty(self, empty_df: pd.DataFrame) -> None:
        result = compute_drainage_direction(empty_df)
        assert result == {}


class TestSimulateRoadConstruction:
    def test_midpoint_road(self, sample_survey_df: pd.DataFrame) -> None:
        tin, _ = generate_tin_uncached(sample_survey_df)
        mid = (50.0 + 60.0) / 2
        result = simulate_road_construction(sample_survey_df, tin, mid)
        assert result["error"] is None
        assert result["cut_volume"] is not None and result["cut_volume"] >= 0
        assert result["fill_volume"] is not None and result["fill_volume"] >= 0

    def test_road_above_all(self, sample_survey_df: pd.DataFrame) -> None:
        tin, _ = generate_tin_uncached(sample_survey_df)
        result = simulate_road_construction(sample_survey_df, tin, 100.0)
        assert result["cut_volume"] == pytest.approx(0.0)
        assert result["fill_volume"] is not None and result["fill_volume"] > 0

    def test_road_below_all(self, sample_survey_df: pd.DataFrame) -> None:
        tin, _ = generate_tin_uncached(sample_survey_df)
        result = simulate_road_construction(sample_survey_df, tin, 0.0)
        assert result["fill_volume"] == pytest.approx(0.0)
        assert result["cut_volume"] is not None and result["cut_volume"] > 0


def generate_tin_uncached(
    df: pd.DataFrame | None,
) -> tuple[Delaunay | None, str | None]:
    """Generate TIN without Streamlit caching (for test context)."""

    if df is None or df.empty or len(df) < 3:
        return None, "Too few points"
    xy = df[["Easting", "Northing"]].to_numpy()
    try:
        return Delaunay(xy), None
    except (QhullError, ValueError):
        return None, "Could not triangulate"
