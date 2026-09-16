"""Tests for modules.samples."""

from __future__ import annotations

from modules.samples import SAMPLE_DATASETS


def test_sample_datasets_validity() -> None:
    """Verify all configured sample datasets exist on disk and have metadata."""
    assert len(SAMPLE_DATASETS) >= 3
    for sample in SAMPLE_DATASETS:
        assert sample["label"]
        assert sample["description"]
        assert sample["path"].exists()
        assert sample["path"].suffix == ".csv"
