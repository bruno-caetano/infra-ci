"""
Uploads CSV and TXT files from coletas/ to Cloudinary and outputs
a JSON mapping of public_id -> secure_url for index generation.

Required env vars:
  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
"""

import json
import os
import sys
from pathlib import Path

import cloudinary
import cloudinary.uploader

COLETAS_DIR = Path("coletas")


def configure():
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        print("ERROR: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET must be set.")
        sys.exit(1)

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
    )


def collect_files():
    return [
        f for f in COLETAS_DIR.rglob("*")
        if f.is_file() and f.name != ".gitkeep" and f.suffix in (".csv", ".txt")
    ]


def upload_files(files):
    uploaded = []
    for file_path in sorted(files):
        rel = file_path.relative_to(COLETAS_DIR)
        folder = f"coletas/{str(rel.parent)}"
        filename = rel.stem

        result = cloudinary.uploader.upload(
            str(file_path),
            resource_type="raw",
            folder=folder,
            public_id=filename,
            use_filename=True,
            unique_filename=False,
            overwrite=True,
        )

        entry = {
            "file": str(rel),
            "public_id": result["public_id"],
            "url": result["secure_url"],
        }
        uploaded.append(entry)
        print(f"[UPLOADED] {rel} -> {result['secure_url']}")

    return uploaded


def main():
    configure()

    files = collect_files()
    if not files:
        print("No files to upload.")
        return

    print(f"Found {len(files)} file(s) to upload.\n")
    uploaded = upload_files(files)

    output_path = Path("uploaded_files.json")
    output_path.write_text(json.dumps(uploaded, indent=2))
    print(f"\nDone. Wrote {len(uploaded)} entries to {output_path}")


if __name__ == "__main__":
    main()
