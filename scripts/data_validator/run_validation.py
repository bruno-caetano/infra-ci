"""
Runs content validation on collection CSVs found in the changed files list.
Assumes pre_validate.py has already checked file structure and naming.

Usage: python run_validation.py <changed_files_list>
  where <changed_files_list> is a text file with one file path per line.
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VALIDATE_SCRIPT = SCRIPT_DIR / "validate_csv.py"
CONFIG_PATH = SCRIPT_DIR.parent / "config.json"

with open(CONFIG_PATH) as f:
    KNOWN_PLATFORMS = json.load(f)["platforms"]

DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"
PLATFORM_GROUP = '|'.join(KNOWN_PLATFORMS)

COLLECTION_REGEX = re.compile(
    rf"^({PLATFORM_GROUP})_{DATE_PATTERN}_{DATE_PATTERN}\.csv$"
)


def extract_platform(file_path: Path) -> str | None:
    """
    Extracts the platform name from the parent folder.
    e.g. 'instagram_2026-03-02_2026-03-08' -> 'instagram'
    """
    parent_name = file_path.parent.name
    prefix = parent_name.split("_")[0].lower()
    if prefix in KNOWN_PLATFORMS:
        return prefix
    return None


def is_collection_csv(file_path: Path) -> bool:
    """Checks if the file is a collection CSV."""
    return COLLECTION_REGEX.match(file_path.name.lower()) is not None


def run_validation(changed_files_path: Path) -> bool:
    if not changed_files_path.exists():
        print("No changed files list found.")
        return True

    lines = changed_files_path.read_text().strip().splitlines()
    changed_files = [Path(line.strip()) for line in lines if line.strip()]

    collection_csvs = [f for f in changed_files if is_collection_csv(f)]

    print(f"[DEBUG] cwd: {os.getcwd()}")
    print(f"[DEBUG] VALIDATE_SCRIPT: {VALIDATE_SCRIPT}")
    print(f"[DEBUG] VALIDATE_SCRIPT exists: {VALIDATE_SCRIPT.exists()}")
    print(f"[DEBUG] Total changed files: {len(changed_files)}")
    print(f"[DEBUG] Collection CSVs: {len(collection_csvs)}")

    if not collection_csvs:
        print("No collection CSVs to validate.")
        return True

    all_passed = True

    for csv_file in collection_csvs:
        platform = extract_platform(csv_file)
        resolved = csv_file.resolve()

        print(f"[DEBUG] csv_file (raw): {csv_file}")
        print(f"[DEBUG] csv_file (resolved): {resolved}")
        print(f"[DEBUG] csv_file.exists(): {csv_file.exists()}")
        print(f"[DEBUG] platform: {platform}")

        if not csv_file.exists():
            print(f"[SKIP] File not found: {csv_file}")
            continue

        print(f"\n{'=' * 60}")
        print(f"[RUN] {csv_file.name} -> --platform {platform}")
        print(f"{'=' * 60}")

        cmd = [sys.executable, str(VALIDATE_SCRIPT), str(resolved), "--platform", platform]
        print(f"[DEBUG] Command: {' '.join(cmd)}")

        result = subprocess.run(cmd)

        if result.returncode != 0:
            all_passed = False

    return all_passed


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <changed_files_list>")
        sys.exit(1)

    changed_files_path = Path(sys.argv[1])
    success = run_validation(changed_files_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
