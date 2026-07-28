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
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path
import logging
import json
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DATA_DIR = PROJECT_ROOT / "data" / "output"
LOG_DIR = OUTPUT_DATA_DIR / "logs"

FREQUENCY_FILE = RAW_DATA_DIR / "freMTPL2freq.pq"
SEVERITY_FILE = RAW_DATA_DIR / "freMTPL2sev.pq"
MANIFEST_FILE = RAW_DATA_DIR / "source_manifest.json"

METADATA_OUTPUT_FILE = OUTPUT_DATA_DIR / "ingestion_metadata.json"
INGESTION_LOG_FILE = LOG_DIR / "ingestion.log"
PIPELINE_RUNS_FILE = OUTPUT_DATA_DIR / "pipeline_runs.jsonl"

EXPECTED_FREQUENCY_COLUMNS: tuple[str, ...] = (
    "IDpol",
    "ClaimNb",
    "Exposure",
    "Area",
    "VehPower",
    "VehAge",
    "DrivAge",
    "BonusMalus",
    "VehBrand",
    "VehGas",
    "Density",
    "Region",
)

EXPECTED_SEVERITY_COLUMNS: tuple[str, ...] = (
    "IDpol",
    "ClaimAmount",
)

EXPECTED_FREQUENCY_DTYPES: dict[str, str] = {
    "IDpol": "float64",
    "ClaimNb": "uint8",
    "Exposure": "float64",
    "Area": "category",
    "VehPower": "uint8",
    "VehAge": "uint8",
    "DrivAge": "uint8",
    "BonusMalus": "uint8",
    "VehBrand": "category",
    "VehGas": "object",
    "Density": "float64",
    "Region": "category",
}

EXPECTED_SEVERITY_DTYPES: dict[str, str] = {
    "IDpol": "float64",
    "ClaimAmount": "float64",
}

def check_required_paths() -> tuple[bool, bool]:
    """Check bootstrap paths and local raw-data files separately."""

    try:
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        raw_data_directory_ready = True
    except OSError:
        raw_data_directory_ready = False

    manifest_available = MANIFEST_FILE.is_file()

    local_data_files = {
        "Frequency file": FREQUENCY_FILE,
        "Severity file": SEVERITY_FILE,
    }

    local_data_files_available = True

    raw_dir_status = "OK" if raw_data_directory_ready else "ERROR"
    manifest_status = "OK" if manifest_available else "MISSING"

    print(f"{'Raw data directory':<20}: {raw_dir_status}")
    print(f"{'Manifest file':<20}: {manifest_status}")

    for label, file_path in local_data_files.items():
        status = "OK" if file_path.is_file() else "MISSING"
        print(f"{label:<20}: {status}")

        if not file_path.is_file():
            local_data_files_available = False

    bootstrap_paths_valid = (
        raw_data_directory_ready
        and manifest_available
    )

    return bootstrap_paths_valid, local_data_files_available

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
    
def load_source_manifest() -> dict:
    """Load the source manifest containing raw-data provenance information."""

    with MANIFEST_FILE.open("r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)

def build_ingestion_metadata(
    frequency_metadata: dict,
    severity_metadata: dict,
    source_manifest: dict,
) -> dict:
    """Combine dataset metadata with source and ingestion-run information."""

    source_datasets = {
        dataset["dataset_name"]: dataset
        for dataset in source_manifest["datasets"]
    }

    return {
        "ingestion_run_utc": datetime.now(timezone.utc).isoformat(),
        "source_information": {
            "retrieval_date": source_manifest["retrieval_date"],
            "retrieval_method": source_manifest["retrieval_method"],
            "api_status": source_manifest["api_status"],
        },
        "datasets": [
            {
                **frequency_metadata,
                **source_datasets["freMTPL2freq"],
            },
            {
                **severity_metadata,
                **source_datasets["freMTPL2sev"],
            },
        ],
    }

def save_ingestion_metadata(metadata: dict) -> None:
    """Save ingestion metadata as a readable UTF-8 JSON file."""

    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with METADATA_OUTPUT_FILE.open("w", encoding="utf-8") as metadata_file:
        json.dump(
            metadata,
            metadata_file,
            indent=2,
            ensure_ascii=False,
        )
        metadata_file.write("\n")

def validate_saved_metadata(expected_metadata: dict) -> bool:
    """Validate that the saved JSON contains the expected metadata."""

    with METADATA_OUTPUT_FILE.open("r", encoding="utf-8") as metadata_file:
        saved_metadata = json.load(metadata_file)

    metadata_matches = saved_metadata == expected_metadata

    status = "PASS" if metadata_matches else "FAIL"
    print(f"Metadata JSON validation: {status}")

    return metadata_matches
def validate_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    expected_columns: tuple[str, ...],
) -> bool:
    """Validate column names and column order for a dataset."""

    actual_columns = tuple(dataframe.columns)

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
    ]

    order_matches = actual_columns == expected_columns

    schema_is_valid = (
        not missing_columns
        and not unexpected_columns
        and order_matches
    )

    status = "PASS" if schema_is_valid else "FAIL"

    print(f"{dataset_name} schema validation: {status}")

    if missing_columns:
        print(f"  Missing columns: {missing_columns}")

    if unexpected_columns:
        print(f"  Unexpected columns: {unexpected_columns}")

    if not order_matches:
        print("  Column order does not match the expected schema.")

    return schema_is_valid

def validate_dtypes(
    dataset_name: str,
    dataframe: pd.DataFrame,
    expected_dtypes: dict[str, str],
) -> bool:
    """Validate the raw data types of all expected dataset columns."""

    dtype_mismatches = {}

    for column, expected_dtype in expected_dtypes.items():
        actual_dtype = str(dataframe[column].dtype)

        if actual_dtype != expected_dtype:
            dtype_mismatches[column] = {
                "expected": expected_dtype,
                "actual": actual_dtype,
            }

    dtypes_are_valid = not dtype_mismatches
    status = "PASS" if dtypes_are_valid else "FAIL"

    print(f"{dataset_name} data type validation: {status}")

    for column, mismatch in dtype_mismatches.items():
        print(
            f"  {column}: "
            f"expected={mismatch['expected']}, "
            f"actual={mismatch['actual']}"
        )

    return dtypes_are_valid
    
def validate_dataset_schema(
    dataset_name: str,
    dataframe: pd.DataFrame,
    expected_columns: tuple[str, ...],
    expected_dtypes: dict[str, str],
) -> bool:
    """Validate the complete raw schema of a dataset."""

    columns_are_valid = validate_columns(
        dataset_name=dataset_name,
        dataframe=dataframe,
        expected_columns=expected_columns,
    )

    dtypes_are_valid = validate_dtypes(
        dataset_name=dataset_name,
        dataframe=dataframe,
        expected_dtypes=expected_dtypes,
    )

    schema_is_valid = columns_are_valid and dtypes_are_valid
    status = "PASS" if schema_is_valid else "FAIL"

    print(f"{dataset_name} overall schema validation: {status}")

    return schema_is_valid

def configure_logging() -> logging.Logger:
    """Configure console and file logging for the ingestion pipeline."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(
                INGESTION_LOG_FILE,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return logging.getLogger("ingestion")

def determine_data_source(
    required_paths_valid: bool,
    raw_files_not_empty: bool,
    file_sizes_match: bool,
    hashes_match: bool,
) -> str:
    """Determine whether verified local files can be used."""

    local_files_are_verified = all(
        [
            required_paths_valid,
            raw_files_not_empty,
            file_sizes_match,
            hashes_match,
        ]
    )

    if local_files_are_verified:
        return "VERIFIED_LOCAL_FILES"

    return "OPENML_REQUIRED"

def download_missing_raw_files(
    source_manifest: dict,
    logger: logging.Logger,
) -> bool:
    """Download missing raw datasets from the URLs stored in the manifest."""

    all_downloads_successful = True

    for dataset in source_manifest["datasets"]:
        dataset_name = dataset["dataset_name"]
        source_url = dataset["source_url"]
        target_file = PROJECT_ROOT / dataset["local_file"]

        if target_file.is_file():
            logger.info(
                "Local raw file already exists. Download skipped: %s",
                dataset_name,
            )
            continue

        temporary_file = target_file.with_suffix(
            target_file.suffix + ".part"
        )

        logger.warning(
            "Downloading missing raw dataset: %s",
            dataset_name,
        )

        try:
            target_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with urlopen(source_url, timeout=120) as response:
                with temporary_file.open("wb") as output_file:
                    while chunk := response.read(1024 * 1024):
                        output_file.write(chunk)

            temporary_file.replace(target_file)

            logger.info(
                "Raw dataset downloaded successfully: %s",
                dataset_name,
            )

        except (HTTPError, URLError, TimeoutError, OSError):
            logger.exception(
                "Raw dataset download failed: %s",
                dataset_name,
            )

            if temporary_file.exists():
                temporary_file.unlink()

            all_downloads_successful = False

    return all_downloads_successful

def append_pipeline_run_record(
    run_record: dict[str, object],
) -> None:
    """Append one ingestion run record to the JSONL history file."""

    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with PIPELINE_RUNS_FILE.open(
        "a",
        encoding="utf-8",
    ) as pipeline_runs_file:
        pipeline_runs_file.write(
            json.dumps(
                run_record,
                ensure_ascii=False,
            )
            + "\n"
        )

if __name__ == "__main__":
    logger = configure_logging()
    logger.info("Ingestion pipeline started.")
    print(f"Project root:   {PROJECT_ROOT}")
    print(f"Raw data dir:   {RAW_DATA_DIR}")
    print(f"Frequency file: {FREQUENCY_FILE}")
    print(f"Severity file:  {SEVERITY_FILE}")
    print(f"Manifest file:  {MANIFEST_FILE}")
    print(f"Metadata output: {METADATA_OUTPUT_FILE}")
    print(f"Ingestion log:  {INGESTION_LOG_FILE}")
    print(f"Pipeline runs:  {PIPELINE_RUNS_FILE}")
    
    print("\nRequired path check:")

    (
        bootstrap_paths_valid,
        local_data_files_available,
    ) = check_required_paths()

    required_paths_valid = (
        bootstrap_paths_valid
        and local_data_files_available
    )

    if not bootstrap_paths_valid:
        logger.error(
            "Raw-data directory or source manifest is unavailable. "
            "Pipeline stopped."
        )
        raise SystemExit(1)

    try:
        source_manifest = load_source_manifest()
    except json.JSONDecodeError:
        logger.exception(
            "Source manifest contains invalid JSON."
        )
        raise SystemExit(1)
    except OSError:
        logger.exception(
            "Source manifest could not be read."
        )
        raise SystemExit(1)

    if not local_data_files_available:
        logger.warning(
            "Local raw-data files are missing. "
            "OpenML download will be attempted."
        )

        downloads_successful = download_missing_raw_files(
            source_manifest=source_manifest,
            logger=logger,
        )

        if not downloads_successful:
            logger.error(
                "One or more raw datasets could not be downloaded."
            )
            raise SystemExit(2)

        (
            bootstrap_paths_valid,
            local_data_files_available,
        ) = check_required_paths()

        required_paths_valid = (
            bootstrap_paths_valid
            and local_data_files_available
        )

        if not local_data_files_available:
            logger.error(
                "Raw-data files are still missing after download."
            )
            raise SystemExit(2)
    
    print("\nRaw file size check:")
    raw_files_not_empty = check_raw_files_not_empty()
    
    print("\nManifest file size check:")
    file_sizes_match = check_file_sizes_against_manifest()
    
    print("\nManifest SHA256 check:")
    hashes_match = check_sha256_against_manifest()
    
    data_source = determine_data_source(
        required_paths_valid=required_paths_valid,
        raw_files_not_empty=raw_files_not_empty,
        file_sizes_match=file_sizes_match,
        hashes_match=hashes_match,
    )

    print(f"\nData source decision: {data_source}")
    logger.info("Data source decision: %s", data_source)
    
    print("\nLoading raw datasets:")

    try:
        frequency_df, severity_df = load_raw_datasets()
    except Exception:
        logger.exception("Failed to load raw Parquet datasets.")
        raise SystemExit(1)

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
    

    print("\nSource manifest information:")
    print(f"Retrieval date:   {source_manifest['retrieval_date']}")
    print(f"Retrieval method: {source_manifest['retrieval_method']}")
    print(f"Dataset entries:  {len(source_manifest['datasets'])}")
    
    ingestion_metadata = build_ingestion_metadata(
        frequency_metadata=frequency_metadata,
        severity_metadata=severity_metadata,
        source_manifest=source_manifest,
    )

    print("\nCombined ingestion metadata:")
    print(f"Run time UTC:   {ingestion_metadata['ingestion_run_utc']}")
    print(f"Dataset count:  {len(ingestion_metadata['datasets'])}")

    for dataset in ingestion_metadata["datasets"]:
        print(
            f"- {dataset['dataset_name']}: "
            f"{dataset['row_count']:,} rows, "
            f"{dataset['column_count']} columns"
        )
            
    try:
            save_ingestion_metadata(ingestion_metadata)
    except OSError:
        logger.exception(
            "Ingestion metadata could not be written."
        )
        raise SystemExit(1)

    print(f"\nMetadata saved to: {METADATA_OUTPUT_FILE}")

    print("\nValidating saved metadata:")

    try:
        metadata_json_valid = validate_saved_metadata(
            ingestion_metadata
        )
    except json.JSONDecodeError:
        logger.exception(
            "Saved ingestion metadata contains invalid JSON."
        )
        raise SystemExit(1)
    except OSError:
        logger.exception(
            "Saved ingestion metadata could not be read."
        )
        raise SystemExit(1)
    
    print("\nComplete schema validation:")

    frequency_schema_valid = validate_dataset_schema(
        dataset_name="freMTPL2freq",
        dataframe=frequency_df,
        expected_columns=EXPECTED_FREQUENCY_COLUMNS,
        expected_dtypes=EXPECTED_FREQUENCY_DTYPES,
    )

    severity_schema_valid = validate_dataset_schema(
        dataset_name="freMTPL2sev",
        dataframe=severity_df,
        expected_columns=EXPECTED_SEVERITY_COLUMNS,
        expected_dtypes=EXPECTED_SEVERITY_DTYPES,
    )
    
    pipeline_success = all(
        [
            required_paths_valid,
            raw_files_not_empty,
            file_sizes_match,
            hashes_match,
            metadata_json_valid,
            frequency_schema_valid,
            severity_schema_valid,
        ]
    )

    pipeline_status = "PASS" if pipeline_success else "FAIL"
    
    run_record = {
        "run_utc": ingestion_metadata["ingestion_run_utc"],
        "pipeline_status": pipeline_status,
        "data_source": data_source,
        "frequency_row_count": len(frequency_df),
        "severity_row_count": len(severity_df),
        "validations": {
            "required_paths_valid": required_paths_valid,
            "raw_files_not_empty": raw_files_not_empty,
            "file_sizes_match": file_sizes_match,
            "hashes_match": hashes_match,
            "metadata_json_valid": metadata_json_valid,
            "frequency_schema_valid": frequency_schema_valid,
            "severity_schema_valid": severity_schema_valid,
        },
    }
    
    try:
        append_pipeline_run_record(run_record)
    except OSError:
        logger.exception(
            "Pipeline run record could not be written."
        )
        raise SystemExit(1)

    logger.info(
        "Pipeline run record appended to: %s",
        PIPELINE_RUNS_FILE,
    )
    
    logger.info(
        "Validation summary | "
        "required_paths=%s | "
        "raw_files_not_empty=%s | "
        "file_sizes_match=%s | "
        "hashes_match=%s | "
        "metadata_json_valid=%s | "
        "frequency_schema_valid=%s | "
        "severity_schema_valid=%s",
        required_paths_valid,
        raw_files_not_empty,
        file_sizes_match,
        hashes_match,
        metadata_json_valid,
        frequency_schema_valid,
        severity_schema_valid,
    )

    print("\nFinal ingestion result:")
    print(f"Ingestion pipeline status: {pipeline_status}")

    if pipeline_success:
        logger.info("Ingestion pipeline completed successfully.")
    else:
        logger.error("Ingestion pipeline failed.")
        raise SystemExit(1)