"""
samples.py

Registry of bundled sample survey datasets, shared by the Exhibit Dashboard
and Presentation Mode so both pages offer the same choices.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

SAMPLE_DATASETS = [
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
]