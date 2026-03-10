import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

COLETAS_DIR = "coletas"
CONFIG_PATH = Path(__file__).parent.parent / "config.json"

with open(CONFIG_PATH) as f:
    PLATFORMS = json.load(f)["platforms"]


def next_week_range():
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    monday = today + timedelta(days=days_until_monday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def next_week_number():
    highest = 0
    if not os.path.isdir(COLETAS_DIR):
        return highest + 1
    for entry in os.listdir(COLETAS_DIR):
        match = re.match(r"semana(\d+)-", entry)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def create_structure():
    monday, sunday = next_week_range()
    week_num = next_week_number()

    week_folder = f"semana{week_num:02d}-{monday.isoformat()}_{sunday.isoformat()}"
    week_path = os.path.join(COLETAS_DIR, week_folder)

    for platform in PLATFORMS:
        platform_path = os.path.join(week_path, platform)
        os.makedirs(platform_path, exist_ok=True)
        gitkeep = os.path.join(platform_path, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, "w").close()

    print(f"Created: {week_path}")
    print(f"  Period: {monday.isoformat()} to {sunday.isoformat()}")
    print(f"  Platforms: {', '.join(PLATFORMS)}")


if __name__ == "__main__":
    create_structure()
