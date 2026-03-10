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


def month_folder(start_date):
    return start_date.strftime("%m-%Y")


def next_week_number():
    highest = 0
    if not os.path.isdir(COLETAS_DIR):
        return highest + 1
    for month in os.listdir(COLETAS_DIR):
        month_path = os.path.join(COLETAS_DIR, month)
        if not os.path.isdir(month_path):
            continue
        for week in os.listdir(month_path):
            match = re.match(r"Semana(\d+)-", week)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def create_structure():
    monday, sunday = next_week_range()
    month = month_folder(monday)
    week_num = next_week_number()

    week_folder = f"Semana{week_num:02d}-{monday.isoformat()}_{sunday.isoformat()}"
    week_path = os.path.join(COLETAS_DIR, month, week_folder)

    for platform in PLATFORMS:
        platform_folder = f"{platform}_{monday.isoformat()}_{sunday.isoformat()}"
        platform_path = os.path.join(week_path, platform_folder)
        os.makedirs(platform_path, exist_ok=True)
        gitkeep = os.path.join(platform_path, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, "w").close()

    print(f"Created: {week_path}")
    print(f"  Period: {monday.isoformat()} to {sunday.isoformat()}")
    print(f"  Platforms: {', '.join(PLATFORMS)}")


if __name__ == "__main__":
    create_structure()
