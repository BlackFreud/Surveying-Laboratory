"""Tests for modules.terrain_model."""

from __future__ import annotations

import pandas as pd
from scipy.spatial import Delaunay

from modules.terrain_model import build_surface_mesh, generate_tin


class TestGenerateTin:
    def test_valid_triangulation(self, sample_survey_df: pd.DataFrame) -> None:
        tin, error = generate_tin(sample_survey_df)
        assert error is None
        assert isinstance(tin, Delaunay)

    def test_too_few_points(self, two_point_df: pd.DataFrame) -> None:
        tin, error = generate_tin(two_point_df)
        assert tin is None
        assert error is not None
        assert "at least 3" in error.lower()

    def test_empty_dataframe(self, empty_df: pd.DataFrame) -> None:
        tin, error = generate_tin(empty_df)
        assert tin is None
        assert error is not None

    def test_none_input(self) -> None:
        tin, _error = generate_tin(None)
        assert tin is None

    def test_collinear_points(self, collinear_df: pd.DataFrame) -> None:
        tin, error = generate_tin(collinear_df)
        assert tin is None
        assert error is not None
        assert "could not build" in error.lower()


class TestBuildSurfaceMesh:
    def test_mesh_structure(self, sample_survey_df: pd.DataFrame) -> None:
        tin, _ = generate_tin(sample_survey_df)
        assert tin is not None
        mesh = build_surface_mesh(sample_survey_df, tin)
        assert len(mesh["x"]) == 5
        assert len(mesh["y"]) == 5
        assert len(mesh["z"]) == 5
        assert mesh["n_triangles"] > 0
        assert mesh["triangles"].shape[1] == 3
