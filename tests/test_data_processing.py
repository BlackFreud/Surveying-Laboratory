"""Tests for modules.data_processing."""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from modules.data_processing import (
    MAX_SURVEY_POINTS,
    REQUIRED_COLUMNS,
    load_csv_points,
    load_manual_points,
    summarize_points,
    validate_points,
)


class TestLoadManualPoints:
    def test_drops_blank_rows(self) -> None:
        df = pd.DataFrame(
            {
                "Point": ["P1", None, "P2"],
                "Easting": [100.0, None, 200.0],
                "Northing": [100.0, None, 200.0],
                "Elevation": [50.0, None, 55.0],
            }
        )
        result = load_manual_points(df)
        assert len(result) == 2
        assert list(result["Point"]) == ["P1", "P2"]

    def test_strips_whitespace(self) -> None:
        df = pd.DataFrame(
            {
                "Point": ["  P1  ", "P2 "],
                "Easting": [100.0, 200.0],
                "Northing": [100.0, 200.0],
                "Elevation": [50.0, 55.0],
            }
        )
        result = load_manual_points(df)
        assert list(result["Point"]) == ["P1", "P2"]

    def test_coerces_non_numeric(self) -> None:
        df = pd.DataFrame(
            {
                "Point": ["P1"],
                "Easting": ["abc"],
                "Northing": [100.0],
                "Elevation": [50.0],
            }
        )
        result = load_manual_points(df)
        assert pd.isna(result.iloc[0]["Easting"])

    def test_empty_input(self) -> None:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        result = load_manual_points(df)
        assert result.empty
        assert list(result.columns) == REQUIRED_COLUMNS

    def test_adds_missing_columns(self) -> None:
        df = pd.DataFrame({"Point": ["P1"], "Easting": [100.0]})
        result = load_manual_points(df)
        assert "Northing" in result.columns
        assert "Elevation" in result.columns


class TestLoadCsvPoints:
    def _make_csv(self, content: str) -> io.BytesIO:
        return io.BytesIO(content.encode("utf-8"))

    def test_valid_csv(self) -> None:
        csv = self._make_csv("Point,Easting,Northing,Elevation\nP1,100,200,50\n")
        df, error = load_csv_points(csv)
        assert error is None
        assert len(df) == 1
        assert df.iloc[0]["Point"] == "P1"

    def test_missing_columns(self) -> None:
        csv = self._make_csv("Point,X,Y,Z\nP1,100,200,50\n")
        _df, error = load_csv_points(csv)
        assert error is not None
        assert "missing" in error.lower()

    def test_row_count_limit(self) -> None:
        header = "Point,Easting,Northing,Elevation\n"
        rows = "".join(f"P{i},{i},{i},{i}\n" for i in range(MAX_SURVEY_POINTS + 1))
        csv = self._make_csv(header + rows)
        _df, error = load_csv_points(csv)
        assert error is not None
        assert "exceeds" in error.lower()

    def test_bad_csv(self) -> None:
        csv = self._make_csv("not,a,valid\x00csv")
        df, error = load_csv_points(csv)
        # Should not raise; returns an error message
        assert df.empty or error is not None


class TestValidatePoints:
    def test_valid_data(self, sample_survey_df: pd.DataFrame) -> None:
        issues = validate_points(sample_survey_df)
        assert issues == []

    def test_empty_dataframe(self, empty_df: pd.DataFrame) -> None:
        issues = validate_points(empty_df)
        assert len(issues) == 1
        assert "no survey points" in issues[0].lower()

    def test_missing_values(self) -> None:
        df = pd.DataFrame(
            {
                "Point": ["P1", "P2"],
                "Easting": [100.0, np.nan],
                "Northing": [100.0, 200.0],
                "Elevation": [50.0, 55.0],
            }
        )
        issues = validate_points(df)
        assert any("missing" in i.lower() or "invalid" in i.lower() for i in issues)

    def test_duplicate_point_ids(self) -> None:
        df = pd.DataFrame(
            {
                "Point": ["P1", "P1", "P2"],
                "Easting": [100.0, 200.0, 300.0],
                "Northing": [100.0, 200.0, 300.0],
                "Elevation": [50.0, 55.0, 60.0],
            }
        )
        issues = validate_points(df)
        assert any("duplicate" in i.lower() for i in issues)


class TestSummarizePoints:
    def test_normal(self, sample_survey_df: pd.DataFrame) -> None:
        summary = summarize_points(sample_survey_df)
        assert summary["total_points"] == 5
        assert summary["min_elevation"] == 50.0
        assert summary["max_elevation"] == 60.0

    def test_empty(self, empty_df: pd.DataFrame) -> None:
        summary = summarize_points(empty_df)
        assert summary["total_points"] == 0
        assert summary["min_elevation"] is None
