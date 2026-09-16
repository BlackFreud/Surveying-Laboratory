"""
contour.py

Generates engineering contour maps from the terrain surface by
interpolating the irregular TIN onto a regular grid.
"""

from __future__ import annotations

from typing import TypedDict

import numpy as np
import numpy.typing as npt
import pandas as pd
import streamlit as st
from scipy.interpolate import griddata


class ContourGrid(TypedDict, total=False):
    """Interpolated elevation grid with computed contour levels."""

    grid_x: npt.NDArray[np.float64] | None
    grid_y: npt.NDArray[np.float64] | None
    grid_z: npt.NDArray[np.float64] | None
    levels: npt.NDArray[np.float64] | None
    n_lines: int
    error: str | None


@st.cache_data(show_spinner=False)
def generate_contour_grid(
    df: pd.DataFrame,
    interval: float,
    resolution: int = 100,
) -> ContourGrid:
    """
    Interpolate survey points onto a regular grid and compute contour levels.

    Args:
        df: DataFrame with columns Point, Easting, Northing, Elevation.
        interval: contour interval in meters (e.g. 0.5, 1.0, 2.0, 5.0).
        resolution: number of grid cells along each axis.

    Returns:
        ContourGrid with keys: grid_x (1D), grid_y (1D), grid_z (2D),
        levels (1D array), n_lines (int), error (str or None).
        If error is set, other fields may be empty/None.
    """
    result: ContourGrid = {
        "grid_x": None,
        "grid_y": None,
        "grid_z": None,
        "levels": None,
        "n_lines": 0,
        "error": None,
    }

    if df is None or df.empty or len(df) < 3:
        result["error"] = "At least 3 survey points are required to generate contours."
        return result

    x = df["Easting"].to_numpy()
    y = df["Northing"].to_numpy()
    z = df["Elevation"].to_numpy()

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    if x_min == x_max or y_min == y_max:
        result["error"] = (
            "Survey points must span both Easting and Northing to generate "
            "a contour map (points cannot all share the same X or Y)."
        )
        return result

    grid_x = np.linspace(x_min, x_max, resolution)
    grid_y = np.linspace(y_min, y_max, resolution)
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)

    grid_z = griddata((x, y), z, (mesh_x, mesh_y), method="linear")

    elev_min = float(np.nanmin(grid_z))
    elev_max = float(np.nanmax(grid_z))

    if elev_max - elev_min < interval:
        result["error"] = (
            f"Elevation range ({elev_min:.2f}\u2013{elev_max:.2f} m) is "
            f"smaller than the selected {interval} m interval, so no "
            f"contour lines can be drawn. Try a smaller interval."
        )
        result["grid_x"] = grid_x
        result["grid_y"] = grid_y
        result["grid_z"] = grid_z
        return result

    start = np.floor(elev_min / interval) * interval
    end = np.ceil(elev_max / interval) * interval
    levels = np.arange(start, end + interval, interval)

    result.update(
        {
            "grid_x": grid_x,
            "grid_y": grid_y,
            "grid_z": grid_z,
            "levels": levels,
            "n_lines": len(levels),
            "error": None,
        }
    )
    return result
