"""
Repeatable ingestion pipeline for the freMTPL2 insurance datasets.

Responsibilities
----------------
1. Retrieve the frequency and severity datasets from OpenML.
2. Preserve the raw datasets without business transformations.
3. Reuse verified local raw files when the OpenML service is unavailable.
4. Record dataset metadata such as version, load time, row count,
   column names and source information.
5. Validate the expected schema of both datasets.
6. Write structured INFO, WARNING and ERROR log messages.
7. Record the result of each ingestion run.
8. Produce an identical raw-data result when executed repeatedly.

This module is responsible only for data ingestion.
Data cleaning, aggregation, feature engineering and modelling
must not be performed here.
"""
import pandas as pd
from pathlib import Path
import json
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

FREQUENCY_FILE = RAW_DATA_DIR / "freMTPL2freq.pq"
SEVERITY_FILE = RAW_DATA_DIR / "freMTPL2sev.pq"
MANIFEST_FILE = RAW_DATA_DIR / "source_manifest.json"

def check_required_paths() -> bool:
    """Check whether all required raw-data paths are available."""

    required_paths = {
        "Raw data directory": RAW_DATA_DIR,
        "Frequency file": FREQUENCY_FILE,
        "Severity file": SEVERITY_FILE,
        "Manifest file": MANIFEST_FILE,
    }

    all_paths_exist = True

    for label, path in required_paths.items():
        status = "OK" if path.exists() else "MISSING"
        print(f"{label:<20}: {status}")

        if not path.exists():
            all_paths_exist = False

    return all_paths_exist

def check_raw_files_not_empty() -> bool:
    """Check whether the required raw-data files contain data."""

    required_files = {
        "Frequency file": FREQUENCY_FILE,
        "Severity file": SEVERITY_FILE,
        "Manifest file": MANIFEST_FILE,
    }

    all_files_not_empty = True

    for label, file_path in required_files.items():
        file_size = file_path.stat().st_size
        status = "OK" if file_size > 0 else "EMPTY"

        print(f"{label:<20}: {status} ({file_size:,} bytes)")

        if file_size == 0:
            all_files_not_empty = False

    return all_files_not_empty

def check_file_sizes_against_manifest() -> bool:
    """Compare actual raw-file sizes with the values stored in the manifest."""

    with MANIFEST_FILE.open("r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    all_sizes_match = True

    for dataset in manifest["datasets"]:
        dataset_name = dataset["dataset_name"]
        relative_file_path = dataset["local_file"]
        expected_size = dataset["file_size_bytes"]

        actual_file_path = PROJECT_ROOT / relative_file_path
        actual_size = actual_file_path.stat().st_size

        status = "MATCH" if actual_size == expected_size else "MISMATCH"

        print(
            f"{dataset_name:<15}: {status} "
            f"(expected={expected_size:,}, actual={actual_size:,})"
        )

        if actual_size != expected_size:
            all_sizes_match = False

    return all_sizes_match

def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA256 hash of a file without loading it fully into memory."""

    sha256_hash = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

def check_sha256_against_manifest() -> bool:
    """Compare actual SHA256 hashes with the values stored in the manifest."""

    with MANIFEST_FILE.open("r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    all_hashes_match = True

    for dataset in manifest["datasets"]:
        dataset_name = dataset["dataset_name"]
        relative_file_path = dataset["local_file"]
        expected_hash = dataset["sha256"]

        actual_file_path = PROJECT_ROOT / relative_file_path
        actual_hash = calculate_sha256(actual_file_path)

        status = "MATCH" if actual_hash == expected_hash else "MISMATCH"

        print(f"{dataset_name:<15}: {status}")

        if actual_hash != expected_hash:
            all_hashes_match = False

    return all_hashes_match

def load_raw_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the verified raw Parquet datasets without modifying them."""

    frequency_df = pd.read_parquet(
        FREQUENCY_FILE,
        engine="fastparquet",
    )

    severity_df = pd.read_parquet(
        SEVERITY_FILE,
        engine="fastparquet",
    )

    return frequency_df, severity_df

def build_dataset_metadata(
    dataset_name: str,
    dataframe: pd.DataFrame,
    file_path: Path,
) -> dict:
    """Create basic metadata for a loaded raw dataset."""

    return {
        "dataset_name": dataset_name,
        "file_name": file_path.name,
        "row_count": len(dataframe),
        "column_count": dataframe.shape[1],
        "columns": dataframe.columns.tolist(),
        "dtypes": {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        },
    }

if __name__ == "__main__":
    print(f"Project root:   {PROJECT_ROOT}")
    print(f"Raw data dir:   {RAW_DATA_DIR}")
    print(f"Frequency file: {FREQUENCY_FILE}")
    print(f"Severity file:  {SEVERITY_FILE}")
    print(f"Manifest file:  {MANIFEST_FILE}")
    
    print("\nRequired path check:")
    check_required_paths()
    
    print("\nRaw file size check:")
    check_raw_files_not_empty()
    
    print("\nManifest file size check:")
    check_file_sizes_against_manifest()
    
    print("\nManifest SHA256 check:")
    check_sha256_against_manifest()
    
    print("\nLoading raw datasets:")

    frequency_df, severity_df = load_raw_datasets()

    print(f"Frequency shape: {frequency_df.shape}")
    print(f"Severity shape:  {severity_df.shape}")
    
    frequency_metadata = build_dataset_metadata(
        dataset_name="freMTPL2freq",
        dataframe=frequency_df,
        file_path=FREQUENCY_FILE,
    )

    severity_metadata = build_dataset_metadata(
        dataset_name="freMTPL2sev",
        dataframe=severity_df,
        file_path=SEVERITY_FILE,
    )

    print("\nFrequency metadata:")
    print(frequency_metadata)

    print("\nSeverity metadata:")
    print(severity_metadata)