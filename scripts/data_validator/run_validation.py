"""
Wrapper script that reads a list of changed CSV files, infers the platform
from the parent folder name, and runs validatecsv.py for each file.

Usage: python run_validation.py <changed_files_list>
  where <changed_files_list> is a text file with one CSV path per line.
"""

import json
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VALIDATE_SCRIPT = SCRIPT_DIR / "validate_csv.py"
CONFIG_PATH = SCRIPT_DIR.parent / "config.json"

with open(CONFIG_PATH) as f:
    KNOWN_PLATFORMS = json.load(f)["platforms"]


def extract_platform(csv_path: Path) -> str | None:
    """
    Extracts the platform name from the parent folder.
    e.g. 'instagram_2026-03-02_2026-03-08' -> 'instagram'
    """
    parent_name = csv_path.parent.name
    prefix = parent_name.split("_")[0].lower()
    if prefix in KNOWN_PLATFORMS:
        return prefix
    return None


def run_validation(changed_files_path: Path) -> bool:
    if not changed_files_path.exists():
        print("No changed files list found.")
        return True

    lines = changed_files_path.read_text().strip().splitlines()
    csv_files = [Path(line.strip()) for line in lines if line.strip().endswith(".csv")]

    if not csv_files:
        print("No CSV files changed in this PR.")
        return True

    all_passed = True

    for csv_file in csv_files:
        platform = extract_platform(csv_file)

        if platform is None:
            print(f"[SKIP] Could not detect platform for: {csv_file}")
            continue

        if not csv_file.exists():
            print(f"[SKIP] File not found: {csv_file}")
            continue

        print(f"\n{'=' * 60}")
        print(f"[RUN] {csv_file.name} -> --platform {platform}")
        print(f"{'=' * 60}")

        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), str(csv_file), "--platform", platform],
            cwd=str(SCRIPT_DIR),
        )

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
