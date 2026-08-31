"""
analysis.py

Engineering analysis: elevation stats, slope classification,
and drainage direction, derived from survey points and the TIN.

Status: PHASE 4 implementation.
"""

import math
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay

# ---------------------------------------------------------------------------
# Philippine standard reference values
# ---------------------------------------------------------------------------
# Bureau of Soils and Water Management (BSWM) slope classification, used
# nationwide in Philippine land and geohazard evaluation.
BSWM_SLOPE_GROUPS = [
    {"group": "A", "range": "0-2%", "name": "Nearly level"},
    {"group": "B", "range": "2-6%", "name": "Gently sloping"},
    {"group": "C", "range": "6-12%", "name": "Sloping"},
    {"group": "D", "range": "12-20%", "name": "Moderately steep"},
    {"group": "E", "range": "20-30%", "name": "Steep"},
    {"group": "F", "range": "30-45%+", "name": "Very steep"},
]

# DPWH (Department of Public Works and Highways) reference embankment slope
# ratios (Horizontal:Vertical), for informational comparison only -- this
# tool models the road as a level plane and does not compute embankment
# side-slope geometry.
DPWH_MIN_FILL_SLOPE = "1.5 : 1 (H:V)"
DPWH_CUT_SLOPE_SOFT_ROCK = "0.5:1 to 1:1 (H:V)"
DPWH_CUT_SLOPE_HARD_ROCK = "0.25:1 to 0.5:1 (H:V)"

# PRS92 (Philippine Reference System 1992) UTM-based zones, used for
# engineering survey and topographic mapping.
PRS92_ZONES = {
    "Zone I (Palawan, W. Mindanao)": 117,
    "Zone II (W. Visayas, Mindoro)": 119,
    "Zone III (Luzon, Manila)": 121,
    "Zone IV (Bicol, E. Visayas)": 123,
    "Zone V (Mindanao)": 125,
}


def compute_elevation_stats(df: pd.DataFrame) -> dict:
    """
    Returns highest/lowest point info and elevation difference.

    dict keys:
        highest_point, highest_elevation,
        lowest_point, lowest_elevation,
        elevation_difference
    """
    if df is None or df.empty:
        return {
            "highest_point": None, "highest_elevation": None,
            "lowest_point": None, "lowest_elevation": None,
            "elevation_difference": None,
        }

    high_row = df.loc[df["Elevation"].idxmax()]
    low_row = df.loc[df["Elevation"].idxmin()]

    return {
        "highest_point": high_row["Point"],
        "highest_elevation": float(high_row["Elevation"]),
        "lowest_point": low_row["Point"],
        "lowest_elevation": float(low_row["Elevation"]),
        "elevation_difference": float(high_row["Elevation"] - low_row["Elevation"]),
    }


def classify_slope(slope_percent: float) -> dict:
    """
    Classify a slope percentage per the Philippine Bureau of Soils and Water
    Management (BSWM) slope grouping, used nationwide in Philippine land and
    geohazard evaluation. Returns the group letter, class name, and a note
    when the slope crosses the PD 705 threshold (>=18% is classified as
    forestland rather than alienable & disposable land under Philippine law
    -- informational only, not enforced by this tool).

    Bands:
        A  0-2%    Nearly level
        B  2-6%    Gently sloping
        C  6-12%   Sloping
        D  12-20%  Moderately steep
        E  20-30%  Steep
        F  30-45%+ Very steep
    """
    if slope_percent < 2:
        group, name = "A", "Nearly level"
    elif slope_percent < 6:
        group, name = "B", "Gently sloping"
    elif slope_percent < 12:
        group, name = "C", "Sloping"
    elif slope_percent < 20:
        group, name = "D", "Moderately steep"
    elif slope_percent < 30:
        group, name = "E", "Steep"
    else:
        group, name = "F", "Very steep"

    return {
        "group": group,
        "name": name,
        "label": f"{group} \u2014 {name}",
        "pd705_forestland": slope_percent >= 18,
    }


def compute_slope_stats(df: pd.DataFrame, tin: Delaunay) -> dict:
    """
    Compute the area-weighted average slope (%) across all TIN triangles.

    For each triangle, fits the plane through its 3 vertices and derives
    slope (%) = tan(dip angle) * 100 from the plane's normal vector.
    Triangles are weighted by their planimetric (2D) area so that larger
    triangles contribute proportionally more to the average.

    Returns dict: average_slope_percent, classification, n_triangles, error
    """
    result = {"average_slope_percent": None, "classification": None, "n_triangles": 0, "error": None}

    if df is None or df.empty or tin is None:
        result["error"] = "No terrain surface available."
        return result

    x = df["Easting"].to_numpy()
    y = df["Northing"].to_numpy()
    z = df["Elevation"].to_numpy()

    total_weighted_slope = 0.0
    total_area = 0.0

    for tri in tin.simplices:
        p1 = np.array([x[tri[0]], y[tri[0]], z[tri[0]]])
        p2 = np.array([x[tri[1]], y[tri[1]], z[tri[1]]])
        p3 = np.array([x[tri[2]], y[tri[2]], z[tri[2]]])

        v1 = p2 - p1
        v2 = p3 - p1
        normal = np.cross(v1, v2)
        nx, ny, nz = normal

        # Planimetric (2D, X-Y projected) area of the triangle
        area = 0.5 * abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]))

        if area < 1e-9:
            continue  # degenerate sliver triangle, skip

        if abs(nz) < 1e-9:
            slope_percent = float("inf")  # vertical face, treat as extremely steep
        else:
            slope_percent = (math.sqrt(nx ** 2 + ny ** 2) / abs(nz)) * 100

        total_weighted_slope += slope_percent * area
        total_area += area

    if total_area == 0:
        result["error"] = "Could not compute slope (no valid triangle area)."
        return result

    avg_slope = total_weighted_slope / total_area
    classification = classify_slope(avg_slope)

    result.update({
        "average_slope_percent": avg_slope,
        "classification": classification["label"],
        "slope_group": classification["group"],
        "slope_name": classification["name"],
        "pd705_forestland": classification["pd705_forestland"],
        "n_triangles": len(tin.simplices),
        "error": None,
    })
    return result


def _azimuth_to_bearing(azimuth_deg: float) -> str:
    """Convert a 0-360 azimuth (0=North, clockwise) to quadrant bearing text."""
    az = azimuth_deg % 360
    if 0 <= az < 90:
        return f"N{az:.0f}°E"
    elif 90 <= az < 180:
        return f"S{180 - az:.0f}°E"
    elif 180 <= az < 270:
        return f"S{az - 180:.0f}°W"
    else:
        return f"N{360 - az:.0f}°W"


def compute_drainage_direction(df: pd.DataFrame) -> dict:
    """
    Estimate the potential drainage direction as a straight line from the
    highest elevation point to the lowest elevation point.

    Returns dict:
        high_point, low_point, bearing, distance,
        high_xy (Easting, Northing), low_xy (Easting, Northing)
    """
    if df is None or df.empty:
        return {}

    high_row = df.loc[df["Elevation"].idxmax()]
    low_row = df.loc[df["Elevation"].idxmin()]

    dx = low_row["Easting"] - high_row["Easting"]
    dy = low_row["Northing"] - high_row["Northing"]

    distance = math.sqrt(dx ** 2 + dy ** 2)
    azimuth = math.degrees(math.atan2(dx, dy))  # 0=North, clockwise

    return {
        "high_point": high_row["Point"],
        "low_point": low_row["Point"],
        "high_elevation": float(high_row["Elevation"]),
        "low_elevation": float(low_row["Elevation"]),
        "bearing": _azimuth_to_bearing(azimuth),
        "distance": distance,
        "high_xy": (float(high_row["Easting"]), float(high_row["Northing"])),
        "low_xy": (float(low_row["Easting"]), float(low_row["Northing"])),
    }


def simulate_road_construction(df: pd.DataFrame, tin: Delaunay, road_elevation: float) -> dict:
    """
    Estimate cut/fill volumes for a proposed level road at `road_elevation`,
    using the average-end-area method over each TIN triangle: for each
    triangle, volume = planimetric_area * average(vertex_elevation - road_elevation).
    Positive contributes to cut (terrain above road), negative to fill
    (terrain below road). This is a planning-level approximation commonly
    used for grid/TIN-based earthwork estimates, not a certified quantity
    survey.

    Returns dict:
        cut_volume, fill_volume, net_cut (cut - fill; negative = net fill),
        cut_area, fill_area, triangles (list of dicts with vertices + type
        for visualization), error
    """
    result = {
        "cut_volume": None, "fill_volume": None, "net_cut": None,
        "cut_area": None, "fill_area": None, "triangles": [], "error": None,
    }

    if df is None or df.empty or tin is None:
        result["error"] = "No terrain surface available."
        return result

    x = df["Easting"].to_numpy()
    y = df["Northing"].to_numpy()
    z = df["Elevation"].to_numpy()

    cut_volume = 0.0
    fill_volume = 0.0
    cut_area = 0.0
    fill_area = 0.0
    triangles = []

    for tri in tin.simplices:
        xs = [x[tri[0]], x[tri[1]], x[tri[2]]]
        ys = [y[tri[0]], y[tri[1]], y[tri[2]]]
        zs = [z[tri[0]], z[tri[1]], z[tri[2]]]

        area = 0.5 * abs(
            (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        )
        if area < 1e-9:
            continue

        avg_diff = sum(zi - road_elevation for zi in zs) / 3.0
        volume = area * avg_diff

        if avg_diff >= 0:
            cut_volume += volume
            cut_area += area
            tri_type = "cut"
        else:
            fill_volume += abs(volume)
            fill_area += area
            tri_type = "fill"

        triangles.append({"x": xs, "y": ys, "type": tri_type})

    result.update({
        "cut_volume": cut_volume,
        "fill_volume": fill_volume,
        "net_cut": cut_volume - fill_volume,
        "cut_area": cut_area,
        "fill_area": fill_area,
        "triangles": triangles,
        "error": None,
    })
    return result