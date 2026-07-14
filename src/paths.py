"""Path resolution for the research (paper) layer.

This repository holds the papers and the chart-production code that turns the
outputs of the data and analysis repositories into paper figures and tables. It
depends on two companion repositories:

- **nfs_data** — the aggregated database and datasets. Override with the
  ``NFS_DATA`` environment variable; defaults to a sibling ``../nfs_data``.
- **nfs_analysis** — the model outputs under its ``results/``. Override with the
  ``NFS_ANALYSIS`` environment variable; defaults to a sibling ``../nfs_analysis``.

``REPO_ROOT`` is this repository; regenerated figures and tables go under it.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _sibling(env: str, name: str) -> Path:
    val = os.environ.get(env)
    if val:
        return Path(val).expanduser().resolve()
    return (REPO_ROOT.parent / name).resolve()


DATA_ROOT = _sibling("NFS_DATA", "nfs_data")
ANALYSIS_ROOT = _sibling("NFS_ANALYSIS", "nfs_analysis")

PROC = DATA_ROOT / "data" / "processed"
DB_PATH = PROC / "fire_risk.duckdb"
CORE_DB = PROC / "fire_risk_core.duckdb"
LOOKUPS_DB = PROC / "fire_risk_lookups.duckdb"
ANALYSIS_RESULTS = ANALYSIS_ROOT / "results"
