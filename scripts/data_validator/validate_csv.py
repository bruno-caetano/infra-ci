"""
Validates a CSV file containing social media posts against defined SQL schemas.
Usage: python validatecsv.py <file_path> --platform <platform_name>
"""

import csv
import sys
import argparse
from pathlib import Path


try:
    import schemas
except ImportError:
    print("Error: 'schemas.py' module not found. Please ensure it is in the same directory.")
    sys.exit(1)




## TODO: Should extract content validation code from file handling
## code and move it into a library function
def validate_csv_file(file_path: Path, platform: str, ignore: list) -> bool:
    """
    Orchestrates the validation process.
    Returns: True if valid, False if errors were found.
    """
    print(f"[*] Starting validation...")
    print(f"[*] Target File: {file_path.name}")
    print(f"[*] Platform Schema: {platform.upper()}")

    all_file_errors = []

    try:
        # 'utf-8-sig' handles the BOM if the CSV was exported from Excel
        with file_path.open(mode='r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)

            # Header Validation
            if not reader.fieldnames:
                print("CRITICAL: The file appears to be empty or has no header.")
                return False

            header_errors, header_warnings = schemas.validate_header(reader.fieldnames, platform)
            if header_errors:
                print("\n[!] CRITICAL HEADER ERRORS:")
                print(f"\n[!] Found {len(header_errors)} errors.")
                for err in header_errors:
                    print(f"    - {err}")
            if header_warnings:
                print("\n[!] HEADER WARNINGS:")
                print(f"\n[!] Found {len(header_warnings)} warnings.")
                for err in header_warnings:
                    print(f"    - {err}")

            # Row Validation
            row_idx = 1 # Header is row 1
            min_timestamps = schemas.min_datetime_dict()
            max_timestamps = schemas.max_datetime_dict()
            for row in reader:
                row_idx += 1
                row_errors = []

                # Composition: Base Validation + Platform Validation
                # Checks schema definitions
                row_errors, tstamps = schemas.validate_row(row, platform, ignore)
                for tag in tstamps:
                    curr_val = tstamps[tag]
                    min_timestamps[tag] = min(curr_val, min_timestamps[tag])
                    max_timestamps[tag] = max(curr_val, max_timestamps[tag])
                if row_errors:
                    for err in row_errors:
                        all_file_errors.append(f"Line {row_idx}: {err}")
            if min_timestamps:
                print("RANGES FOR DATETIME COLUMNS:")
            else:
                print("WARNING: Did not find any timestamp columns!")
            for tag in min_timestamps:
                print(f"{tag}\n\tmin value: {min_timestamps[tag]}\n\tmax_value: {max_timestamps[tag]}")
    except Exception as e:
        print(f"\n[!] Unexpected error while reading file: {e}")
        raise e
        return False

    # Final Report
    print("-" * 60)
    if not all_file_errors:
        return True
    else:
        print(f"FAILURE: Found {len(all_file_errors)} issues.")
        print("-" * 60)
        # Limit printed errors to avoid flooding console if file is huge
        max_display_errors = 50
        for i, err in enumerate(all_file_errors):
            if i >= max_display_errors:
                print(f"... and {len(all_file_errors) - max_display_errors} more errors.")
                break
            print(f" [x] {err}")
        return False

def main():
    # Argument Parser Configuration
    parser = argparse.ArgumentParser(
        description="Validate social media post CSVs against SQL constraints.",
        epilog="Example: python validatecsv.py data/youtube_upload.csv --platform youtube"
    )

    # Positional argument: The file path
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the input CSV file."
    )

    # Named argument: The platform (required)
    # We fetch available keys from schemas.py to show them in help message
    available_platforms = list(schemas.PLATFORM_SCHEMAS.keys())
    parser.add_argument(
        "--platform", "-p",
        type=str,
        required=True,
        choices=available_platforms,
        help=f"Target platform schema. Choices: {', '.join(available_platforms)}"
    )


    parser.add_argument('-i', '--ignore',
        type=str,
        required=False,
        action="append",
        default=[],
        help=f"Ignores a column while checking for errors. Useful for filtering results. To ignore multiple columns, use: '-i col1 -i col2'.")

    # Parse arguments
    args = parser.parse_args()

    # Pre-validation checks
    if not args.file_path.exists():
        print(f"Error: The file '{args.file_path}' does not exist.")
        sys.exit(1)

    if not args.file_path.is_file():
        print(f"Error: '{args.file_path}' is not a file.")
        sys.exit(1)

    is_valid = validate_csv_file(args.file_path, args.platform, args.ignore)

    # Exit with status code (0 for success, 1 for failure)
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
