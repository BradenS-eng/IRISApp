"""Local paths for the Ti-PG radiator-fin manuscript analysis archive.

No experimental data or manuscript spreadsheet is distributed with this
repository.  Set the two environment variables below before running a script:

IRISAPP_TIPG_DATA_ROOT: directory containing experiment folders (IRIS-TF-###)
IRISAPP_TIPG_WORKBOOK:  path to IRIS_effective_kin_data.xlsx
"""

import os
from pathlib import Path


ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ARCHIVE_ROOT / "outputs"


def _required_path(variable: str) -> Path:
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(
            f"Set {variable} to the required local input path before running this script."
        )
    path = Path(value).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"{variable} does not exist: {path}")
    return path


def data_root() -> Path:
    """Return the local directory containing IRIS-TF experiment folders."""
    return _required_path("IRISAPP_TIPG_DATA_ROOT")


def workbook_path() -> Path:
    """Return the local effective-conductivity workbook."""
    return _required_path("IRISAPP_TIPG_WORKBOOK")


def output_path(filename: str) -> Path:
    """Create and return a data-free output path within this archive."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR / filename
