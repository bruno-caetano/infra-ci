"""
Updates coletas_index.md with links to uploaded files on Cloudinary.
Reads uploaded_files.json (output from upload_to_cloudinary.py) and
merges new entries into the existing index, organized by week and platform.

Usage: python scripts/update_coletas_index.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

INDEX_PATH = Path("coletas_index.md")
UPLOADED_JSON = Path("uploaded_files.json")

WEEK_REGEX = re.compile(r"(semana\d+-\d{4}-\d{2}-\d{2}_\d{4}-\d{2}-\d{2})")
DATE_DISPLAY = re.compile(r"semana(\d+)-(\d{4})-(\d{2})-(\d{2})_(\d{4})-(\d{2})-(\d{2})")


def format_week_header(week_folder):
    match = DATE_DISPLAY.match(week_folder)
    if not match:
        return week_folder
    num, y1, m1, d1, y2, m2, d2 = match.groups()
    return f"Semana {int(num):02d} - {d1}/{m1}/{y1} a {d2}/{m2}/{y2}"


def parse_existing_index():
    """Parse existing index to preserve previously uploaded entries."""
    entries = defaultdict(dict)

    if not INDEX_PATH.exists():
        return entries

    content = INDEX_PATH.read_text()
    current_week = None
    current_platform = None

    for line in content.splitlines():
        week_match = re.search(r"<!--\s*week:([\w\-]+)\s*-->", line)
        if week_match:
            current_week = week_match.group(1)
            continue

        platform_match = re.search(r"<!--\s*platform:(\w+)\s*-->", line)
        if platform_match and current_week:
            current_platform = platform_match.group(1)
            continue

        link_match = re.search(r"- \[(.+?)\]\((.+?)\)", line)
        if link_match and current_week and current_platform:
            filename = link_match.group(1)
            url = link_match.group(2)
            key = f"{current_week}/{current_platform}/{filename}"
            entries[current_week].setdefault(current_platform, {})[filename] = url

    return entries


def merge_new_entries(entries, uploaded):
    """Merge newly uploaded files into existing entries."""
    for item in uploaded:
        file_parts = Path(item["file"]).parts
        if len(file_parts) < 2:
            continue

        week_folder = file_parts[0]
        platform = file_parts[1]
        filename = file_parts[-1]

        entries[week_folder].setdefault(platform, {})[filename] = item["url"]

    return entries


def generate_markdown(entries):
    """Generate the full index markdown."""
    lines = [
        "# Coletas - Índice de Arquivos",
        "",
        "Arquivos enviados para o Cloudinary, organizados por semana e plataforma.",
        "",
    ]

    for week_folder in sorted(entries.keys(), reverse=True):
        header = format_week_header(week_folder)
        lines.append(f"## {header}")
        lines.append(f"<!-- week:{week_folder} -->")
        lines.append("")

        platforms = entries[week_folder]
        for platform in sorted(platforms.keys()):
            lines.append(f"### {platform.capitalize()}")
            lines.append(f"<!-- platform:{platform} -->")
            files = platforms[platform]
            for filename in sorted(files.keys()):
                url = files[filename]
                lines.append(f"- [{filename}]({url})")
            lines.append("")

    return "\n".join(lines)


def main():
    if not UPLOADED_JSON.exists():
        print("No uploaded_files.json found. Nothing to update.")
        return

    uploaded = json.loads(UPLOADED_JSON.read_text())
    if not uploaded:
        print("No uploaded files. Nothing to update.")
        return

    entries = parse_existing_index()
    entries = merge_new_entries(entries, uploaded)

    markdown = generate_markdown(entries)
    INDEX_PATH.write_text(markdown)

    print(f"Updated {INDEX_PATH} with {len(uploaded)} new file(s).")


if __name__ == "__main__":
    main()
