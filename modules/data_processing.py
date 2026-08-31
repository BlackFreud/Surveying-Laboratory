"""
data_processing.py

Handles survey point input, validation, and summary statistics
for the Digital Terrain Model Simulator.

Status: PHASE 1 implementation.
"""

import pandas as pd
import numpy as np

REQUIRED_COLUMNS = ["Point", "Easting", "Northing", "Elevation"]


def load_manual_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean up a DataFrame produced by the manual-entry data editor.

    - Drops fully empty rows (user left a blank row in the editor).
    - Strips whitespace from Point labels.
    - Coerces Easting/Northing/Elevation to numeric (invalid entries become NaN,
      which validate_points() will flag).

    Returns the cleaned DataFrame with columns: Point, Easting, Northing, Elevation.
    """
    df = df.copy()

    # Drop rows where every cell is empty/NaN (blank rows left in the editor)
    df = df.dropna(how="all")

    if df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Ensure all required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    df["Point"] = df["Point"].astype(str).str.strip()
    for col in ["Easting", "Northing", "Elevation"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[REQUIRED_COLUMNS].reset_index(drop=True)
    return df


def load_csv_points(uploaded_file) -> tuple[pd.DataFrame, str | None]:
    """
    Parse an uploaded CSV file of survey points.

    Expected columns: Point, Easting, Northing, Elevation

    Returns:
        (df, error_message)
        - df: parsed DataFrame (empty DataFrame if parsing failed)
        - error_message: None if parsing succeeded, otherwise a human-readable
          string explaining what went wrong.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return pd.DataFrame(columns=REQUIRED_COLUMNS), f"Could not read CSV file: {e}"

    df.columns = [str(c).strip() for c in df.columns]

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return (
            pd.DataFrame(columns=REQUIRED_COLUMNS),
            f"CSV is missing required column(s): {', '.join(missing_cols)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}",
        )

    df["Point"] = df["Point"].astype(str).str.strip()
    for col in ["Easting", "Northing", "Elevation"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[REQUIRED_COLUMNS].reset_index(drop=True)
    return df, None


def validate_points(df: pd.DataFrame) -> list[str]:
    """
    Validate survey points and return a list of human-readable issue
    descriptions. An empty list means the data is valid.

    Checks:
        - Missing values (NaN in Point, Easting, Northing, or Elevation)
        - Duplicate Point IDs
        - Invalid coordinates (non-numeric Easting/Northing/Elevation,
          which surface as NaN after coercion)
    """
    issues: list[str] = []

    if df.empty:
        issues.append("No survey points were provided.")
        return issues

    # Missing / invalid (non-numeric) values
    missing_mask = df[REQUIRED_COLUMNS].isna().any(axis=1)
    if missing_mask.any():
        bad_rows = df.index[missing_mask].tolist()
        row_labels = [f"row {i + 1}" for i in bad_rows]
        issues.append(
            f"Missing or invalid (non-numeric) values in {len(bad_rows)} "
            f"row(s): {', '.join(row_labels)}."
        )

    # Duplicate Point IDs (ignore blank labels, already caught above)
    non_blank = df[df["Point"].astype(str).str.len() > 0]
    dupes = non_blank["Point"][non_blank["Point"].duplicated(keep=False)]
    if not dupes.empty:
        dup_names = sorted(set(dupes.tolist()))
        issues.append(f"Duplicate point ID(s) found: {', '.join(dup_names)}.")

    return issues


def summarize_points(df: pd.DataFrame) -> dict:
    """
    Compute summary statistics for a validated set of survey points.

    Returns a dict with:
        total_points, min_elevation, max_elevation
    Returns None values if the DataFrame is empty or elevation has no
    valid numeric data.
    """
    if df.empty or df["Elevation"].dropna().empty:
        return {"total_points": 0, "min_elevation": None, "max_elevation": None}

    return {
        "total_points": len(df),
        "min_elevation": float(df["Elevation"].min()),
        "max_elevation": float(df["Elevation"].max()),
    }