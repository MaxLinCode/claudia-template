#!/usr/bin/env python3

import datetime
import os

try:
    from dashboard_renderer import render_dashboard_html
except ModuleNotFoundError:
    from tools.dashboard_renderer import render_dashboard_html

# Configuration
HABITS_DIR = "habits"
DASHBOARD_FILE = os.path.join(HABITS_DIR, "dashboard.md")
DASHBOARD_HTML_FILE = os.path.join(HABITS_DIR, "dashboard.html")

HABIT_EMOJIS = {
    "journal": "📝",
    "stretch-rehab": "🧘",
    "leetcode": "💻",
    "job-search": "💼",
}


def parse_tracker_rows(tracker_path):
    if not os.path.exists(tracker_path):
        return []

    rows = []
    with open(tracker_path, "r", encoding="utf-8") as file_obj:
        for line in file_obj:
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue

            cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
            if len(cells) < 2:
                continue

            date_cell = cells[0]
            status_cell = cells[1]
            note_cell = cells[2] if len(cells) > 2 else ""

            if date_cell.lower() == "date" and status_cell.lower() == "status":
                continue

            if set(date_cell) <= {":", "-"} and set(status_cell) <= {":", "-"}:
                continue

            try:
                row_date = datetime.datetime.strptime(date_cell, "%Y-%m-%d").date()
            except ValueError:
                continue

            rows.append(
                {
                    "date": row_date,
                    "date_str": date_cell,
                    "status": status_cell,
                    "note": note_cell,
                }
            )

    rows.sort(key=lambda row: row["date"])
    return rows


def get_habit_status(habit_path):
    tracker_path = os.path.join(habit_path, "tracker.md")

    if not os.path.exists(tracker_path):
        return {"streak": 0, "last_date": "N/A", "status": "N/A"}

    data_rows = parse_tracker_rows(tracker_path)
    if not data_rows:
        return {"streak": 0, "last_date": "None", "status": "New"}

    streak = 0
    for row in reversed(data_rows):
        status_icon = row["status"]
        if "✅" in status_icon:
            streak += 1
        elif "⏸️" in status_icon:
            continue
        else:
            break

    last_row = data_rows[-1]
    return {
        "streak": streak,
        "last_date": last_row["date_str"],
        "status": last_row["status"],
    }


def calculate_system_streak(habits):
    all_dates = set()

    for habit in habits:
        tracker_path = os.path.join(HABITS_DIR, habit, "tracker.md")
        for row in parse_tracker_rows(tracker_path):
            all_dates.add(row["date"])

    if not all_dates:
        return 0

    today = datetime.date.today()
    last_active_date = None
    if today in all_dates:
        last_active_date = today
    elif (today - datetime.timedelta(days=1)) in all_dates:
        last_active_date = today - datetime.timedelta(days=1)

    if not last_active_date:
        return 0

    current_streak = 0
    check_date = last_active_date
    while check_date in all_dates:
        current_streak += 1
        check_date -= datetime.timedelta(days=1)

    return current_streak


def build_habit_rows(habits):
    rows = []
    today = datetime.date.today()
    week_dates = [today - datetime.timedelta(days=offset) for offset in range(6, -1, -1)]

    for habit in sorted(habits):
        habit_path = os.path.join(HABITS_DIR, habit)
        stats = get_habit_status(habit_path)
        tracker_rows = parse_tracker_rows(os.path.join(habit_path, "tracker.md"))
        tracker_by_date = {row["date"]: row for row in tracker_rows}
        momentum_by_date = {}
        running_momentum = 0

        for tracker_row in tracker_rows:
            status = tracker_row["status"]
            if "✅" in status:
                running_momentum = min(running_momentum + 1, 7)
            elif "⏸️" in status:
                running_momentum = 0
            else:
                running_momentum = 0

            momentum_by_date[tracker_row["date"]] = running_momentum

        habit_name = habit.replace("-", " ").title()
        emoji = HABIT_EMOJIS.get(habit, "📌")
        rows.append(
            {
                "name": habit_name,
                "display_name": f"{emoji} {habit_name}",
                "slug": habit,
                "streak": stats["streak"],
                "last_date": stats["last_date"],
                "last_date_display": format_display_date(stats["last_date"]),
                "status": stats["status"],
                "week": [
                    {
                        "date": day.isoformat(),
                        "label": day.strftime("%a"),
                        "status": tracker_by_date.get(day, {}).get("status", ""),
                        "momentum": momentum_by_date.get(day, 0),
                    }
                    for day in week_dates
                ],
            }
        )

    return rows


def format_display_date(date_str):
    if date_str in {"None", "N/A"}:
        return date_str

    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return date_str

    return f"{date_obj.month}-{date_obj.day}"


def generate_dashboard():
    if not os.path.exists(HABITS_DIR):
        os.makedirs(HABITS_DIR)

    habits = [name for name in os.listdir(HABITS_DIR) if os.path.isdir(os.path.join(HABITS_DIR, name))]
    last_sync = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_streak = calculate_system_streak(habits)
    habit_rows = build_habit_rows(habits)

    streak_banner = f"## ⚡ Consistency: {system_streak} Days"
    if system_streak > 7:
        streak_banner += " (On Fire! 🔥)"

    dashboard_content = [
        "# 📊 Life Dashboard\n",
        streak_banner + "\n",
        f"*Last Sync: {last_sync}*\n",
        "| Habit | Current Streak | Last Logged | Latest Status |",
        "| :--- | :---: | :--- | :---: |",
    ]

    for row in habit_rows:
        streak_display = f"🔥 {row['streak']}" if row["streak"] > 3 else str(row["streak"])
        dashboard_content.append(
            f"| **{row['display_name']}** | {streak_display} | {row['last_date_display']} | {row['status']} |"
        )

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(dashboard_content))

    with open(DASHBOARD_HTML_FILE, "w", encoding="utf-8") as file_obj:
        file_obj.write(render_dashboard_html(system_streak, last_sync, habit_rows))

    print("Dashboard updated successfully.")


if __name__ == "__main__":
    generate_dashboard()
