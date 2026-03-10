"""
Pre-validation script that checks file structure and naming conventions
for files inside coletas/ platform folders.

Only the following files are allowed inside platform folders:
  - {platform}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv  (collection)
  - registro_{platform}_{YYYY-MM-DD}_{YYYY-MM-DD}.csv  (log)
  - *.txt  (notes)

Usage: python pre_validate.py <changed_files_list>
  where <changed_files_list> is a text file with one file path per line.
"""

import json
import re
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

with open(CONFIG_PATH) as f:
    KNOWN_PLATFORMS = json.load(f)["platforms"]

DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"
PLATFORM_GROUP = '|'.join(KNOWN_PLATFORMS)

COLLECTION_REGEX = re.compile(
    rf"^({PLATFORM_GROUP})_{DATE_PATTERN}_{DATE_PATTERN}\.csv$"
)
REGISTRO_REGEX = re.compile(
    rf"^registro_({PLATFORM_GROUP})_{DATE_PATTERN}_{DATE_PATTERN}\.csv$"
)
PLATFORM_FOLDER_NAMES = set(KNOWN_PLATFORMS)


def extract_folder_platform(file_path: Path) -> str | None:
    """Extracts the platform name from the parent folder name."""
    parent_name = file_path.parent.name.lower()
    if parent_name in PLATFORM_FOLDER_NAMES:
        return parent_name
    return None


def extract_file_platform(file_path: Path) -> str | None:
    """
    Extracts the platform name from the file name.
    e.g. 'instagram_2026-03-02_2026-03-08.csv' -> 'instagram'
         'registro_telegram_2026-03-02_2026-03-08.csv' -> 'telegram'
    """
    name = file_path.name.lower()
    match = COLLECTION_REGEX.match(name)
    if match:
        return match.group(1)
    match = REGISTRO_REGEX.match(name)
    if match:
        return match.group(1)
    return None


def is_inside_platform_folder(file_path: Path) -> bool:
    """Checks if the file is inside a recognized platform folder."""
    return file_path.parent.name.lower() in PLATFORM_FOLDER_NAMES


def classify_file(file_path: Path) -> str:
    """
    Classifies a file inside a platform folder.
    Returns: 'collection', 'registro', 'txt', or 'invalid'
    """
    name = file_path.name.lower()

    if name.endswith(".txt"):
        return "txt"
    if COLLECTION_REGEX.match(name):
        return "collection"
    if REGISTRO_REGEX.match(name):
        return "registro"
    return "invalid"


def pre_validate(changed_files_path: Path) -> bool:
    if not changed_files_path.exists():
        print("No changed files list found.")
        return True

    lines = changed_files_path.read_text().strip().splitlines()
    changed_files = [Path(line.strip()) for line in lines if line.strip()]

    if not changed_files:
        print("No files changed in this PR.")
        return True

    all_passed = True

    for file_path in changed_files:
        if not is_inside_platform_folder(file_path):
            print(f"[SKIP] Not inside a platform folder: {file_path}")
            continue

        file_type = classify_file(file_path)
        folder_platform = extract_folder_platform(file_path)

        if file_type == "invalid":
            print(f"[FAIL] File not allowed: {file_path.name}")
            print(f"  Allowed patterns inside platform folders:")
            print(f"    - {{platform}}_YYYY-MM-DD_YYYY-MM-DD.csv (collection)")
            print(f"    - registro_{{platform}}_YYYY-MM-DD_YYYY-MM-DD.csv (log)")
            print(f"    - *.txt (notes)")
            all_passed = False
            continue

        if file_type in ("collection", "registro"):
            file_platform = extract_file_platform(file_path)
            if file_platform and file_platform != folder_platform:
                print(f"[FAIL] Platform mismatch: '{file_path.name}' is in folder '{file_path.parent.name}'")
                print(f"  File platform: {file_platform}")
                print(f"  Folder platform: {folder_platform}")
                all_passed = False
                continue

        print(f"[OK] {file_path.name} ({file_type})")

    return all_passed


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <changed_files_list>")
        sys.exit(1)

    changed_files_path = Path(sys.argv[1])
    success = pre_validate(changed_files_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
