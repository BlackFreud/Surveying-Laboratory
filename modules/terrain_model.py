"""
terrain_model.py

Generates the Triangulated Irregular Network (TIN) and terrain
surface from validated survey points.
"""

from __future__ import annotations

from typing import TypedDict

import numpy as np
import numpy.typing as npt
import pandas as pd
import streamlit as st
from scipy.spatial import Delaunay, QhullError


class SurfaceMesh(TypedDict):
    """Triangulated terrain surface data for 2D/3D plotting."""

    x: npt.NDArray[np.float64]
    y: npt.NDArray[np.float64]
    z: npt.NDArray[np.float64]
    triangles: npt.NDArray[np.intp]
    n_triangles: int


@st.cache_data(show_spinner=False)
def generate_tin(
    df: pd.DataFrame,
) -> tuple[Delaunay | None, str | None]:
    """
    Build a Delaunay triangulation (TIN) from survey points.

    Args:
        df: DataFrame with columns Point, Easting, Northing, Elevation.

    Returns:
        (tin, error_message)
        - tin: scipy.spatial.Delaunay object, or None if it could not be built.
        - error_message: None on success, otherwise a human-readable reason.
    """
    if df is None or df.empty:
        return None, "No survey points available."

    if len(df) < 3:
        return None, (
            f"At least 3 survey points are required to build a terrain "
            f"surface. Currently loaded: {len(df)}."
        )

    xy = df[["Easting", "Northing"]].to_numpy()

    try:
        tin = Delaunay(xy)
    except (QhullError, ValueError):
        # Most commonly: all points are collinear (degenerate geometry),
        # which Delaunay cannot triangulate. The underlying Qhull error is
        # a low-level geometry dump, not useful to an end user, so we
        # replace it with a plain-language explanation.
        return None, (
            "Could not build a terrain surface from these points. "
            "This usually happens when all points fall on a single line "
            "(no width or depth to the survey area), or when there aren't "
            "enough distinct Easting/Northing locations. Try adding points "
            "spread across at least two dimensions."
        )

    return tin, None


def build_surface_mesh(
    df: pd.DataFrame,
    tin: Delaunay,
) -> SurfaceMesh:
    """
    Package triangulation + elevation data for 2D/3D plotting.

    Returns a SurfaceMesh with:
        x, y, z        : coordinate arrays (Easting, Northing, Elevation)
        triangles      : (n_triangles, 3) array of point indices per triangle
        n_triangles    : triangle count
    """
    x = df["Easting"].to_numpy()
    y = df["Northing"].to_numpy()
    z = df["Elevation"].to_numpy()
    triangles = tin.simplices  # (n_triangles, 3) indices into x/y/z

    return {
        "x": x,
        "y": y,
        "z": z,
        "triangles": triangles,
        "n_triangles": len(triangles),
    }
