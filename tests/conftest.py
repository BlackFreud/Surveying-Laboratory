"""Shared pytest fixtures for DTM Simulator tests."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_survey_df() -> pd.DataFrame:
    """A small valid survey DataFrame (5 points forming a simple slope)."""
    return pd.DataFrame(
        {
            "Point": ["P1", "P2", "P3", "P4", "P5"],
            "Easting": [100.0, 200.0, 200.0, 100.0, 150.0],
            "Northing": [100.0, 100.0, 200.0, 200.0, 150.0],
            "Elevation": [50.0, 55.0, 60.0, 52.0, 57.0],
        }
    )


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """An empty DataFrame with the correct columns."""
    return pd.DataFrame(columns=["Point", "Easting", "Northing", "Elevation"])


@pytest.fixture
def two_point_df() -> pd.DataFrame:
    """A DataFrame with only 2 points (too few for triangulation)."""
    return pd.DataFrame(
        {
            "Point": ["P1", "P2"],
            "Easting": [100.0, 200.0],
            "Northing": [100.0, 200.0],
            "Elevation": [50.0, 60.0],
        }
    )


@pytest.fixture
def collinear_df() -> pd.DataFrame:
    """Three collinear points that cannot be triangulated."""
    return pd.DataFrame(
        {
            "Point": ["P1", "P2", "P3"],
            "Easting": [100.0, 200.0, 300.0],
            "Northing": [100.0, 100.0, 100.0],
            "Elevation": [50.0, 55.0, 60.0],
        }
    )


@pytest.fixture
def flat_df() -> pd.DataFrame:
    """Four points at the same elevation (flat terrain)."""
    return pd.DataFrame(
        {
            "Point": ["P1", "P2", "P3", "P4"],
            "Easting": [100.0, 200.0, 200.0, 100.0],
            "Northing": [100.0, 100.0, 200.0, 200.0],
            "Elevation": [50.0, 50.0, 50.0, 50.0],
        }
    )
