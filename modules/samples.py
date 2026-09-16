"""
samples.py

Registry of bundled sample survey datasets, shared by the Exhibit Dashboard
and Presentation Mode so both pages offer the same choices.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

DATA_DIR = Path(__file__).parent.parent / "data"


class SampleDataset(TypedDict):
    """Metadata and filesystem path for a bundled survey dataset."""

    label: str
    path: Path
    description: str


SAMPLE_DATASETS: list[SampleDataset] = [
    {
        "label": "Sample 1 \u2014 Hill, Ridge & Valley",
        "path": DATA_DIR / "sample_1_hill_ridge_valley.csv",
        "description": "63 points \u00b7 27 m relief \u00b7 moderate slope with a drainage valley",
    },
    {
        "label": "Sample 2 \u2014 Flat Building Site",
        "path": DATA_DIR / "sample_2_flat_building_site.csv",
        "description": "64 points \u00b7 6 m relief \u00b7 gently sloping, near-level lot",
    },
    {
        "label": "Sample 3 \u2014 Steep Hillside",
        "path": DATA_DIR / "sample_3_steep_hillside.csv",
        "description": "72 points \u00b7 79 m relief \u00b7 very steep terrain for a dramatic cut/fill demo",
    },
    {
        "label": "Sample 4 \u2014 UM Matina Campus",
        "path": DATA_DIR / "sample_4_um_matina_campus.csv",
        "description": "625 points \u00b7 32 m relief \u00b7 large real-campus grid survey",
    },
    {
        "label": "Sample 5 \u2014 Sample Number 5",
        "path": DATA_DIR / "sample_5_random_elevation.csv",
        "description": "625 points \u00b7 32 m relief \u00b7 large real-campus grid survey",
    }
]

# Validate that all bundled sample files exist at import time so a
# missing file surfaces immediately rather than on first user click.
for _ds in SAMPLE_DATASETS:
    if not _ds["path"].exists():
        raise FileNotFoundError(f"Bundled sample dataset not found: {_ds['path']}")
