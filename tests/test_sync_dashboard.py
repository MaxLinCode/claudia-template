import datetime
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import sync_dashboard  # noqa: E402


class SyncDashboardTests(unittest.TestCase):
    def test_parse_tracker_rows_ignores_headers_and_invalid_dates(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = Path(tmp_dir) / "tracker.md"
            tracker.write_text(
                "\n".join(
                    [
                        "| Date | Status | Note |",
                        "| :--- | :---: | :--- |",
                        "| 2026-03-09 | ✅ | kept it simple |",
                        "| invalid-date | ❌ | skipped parse |",
                        "| 2026-03-10 | ⏸️ | travel |",
                    ]
                ),
                encoding="utf-8",
            )

            rows = sync_dashboard.parse_tracker_rows(tracker)

        self.assertEqual(["2026-03-09", "2026-03-10"], [row["date_str"] for row in rows])

    def test_skip_carries_heatmap_momentum(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_habits_dir = sync_dashboard.HABITS_DIR
            try:
                habits_dir = Path(tmp_dir) / "habits"
                habit_dir = habits_dir / "mobility"
                habit_dir.mkdir(parents=True)
                today = datetime.date.today()
                two_days_ago = today - datetime.timedelta(days=2)
                yesterday = today - datetime.timedelta(days=1)
                (habit_dir / "tracker.md").write_text(
                    "\n".join(
                        [
                            "| Date | Status | Note |",
                            "| :--- | :---: | :--- |",
                            f"| {two_days_ago.isoformat()} | ✅ | day one |",
                            f"| {yesterday.isoformat()} | ✅ | day two |",
                            f"| {today.isoformat()} | ⏸️ | travel day |",
                        ]
                    ),
                    encoding="utf-8",
                )
                sync_dashboard.HABITS_DIR = habits_dir

                rows = sync_dashboard.build_habit_rows(["mobility"])
            finally:
                sync_dashboard.HABITS_DIR = original_habits_dir

        momentum_by_date = {cell["date"]: cell["momentum"] for cell in rows[0]["week"]}
        self.assertEqual(2, momentum_by_date[today.isoformat()])

    def test_script_anchors_habits_dir_to_repo_root_when_run_from_tools_directory(self):
        code = (
            "import sync_dashboard\n"
            "from pathlib import Path\n"
            "print(sync_dashboard.HABITS_DIR == Path.cwd().parent / 'habits')\n"
        )

        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT / "tools",
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual("True", result.stdout.strip())

    def test_system_streak_uses_any_logged_activity_by_day(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_habits_dir = sync_dashboard.HABITS_DIR
            try:
                habits_dir = Path(tmp_dir) / "habits"
                habit_dir = habits_dir / "journal"
                habit_dir.mkdir(parents=True)
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                (habit_dir / "tracker.md").write_text(
                    "\n".join(
                        [
                            "| Date | Status | Note |",
                            "| :--- | :---: | :--- |",
                            f"| {yesterday.isoformat()} | ❌ | still logged |",
                            f"| {today.isoformat()} | ✅ | showed up |",
                        ]
                    ),
                    encoding="utf-8",
                )
                sync_dashboard.HABITS_DIR = habits_dir

                streak = sync_dashboard.calculate_system_streak(["journal"])
            finally:
                sync_dashboard.HABITS_DIR = original_habits_dir

        self.assertEqual(2, streak)


if __name__ == "__main__":
    unittest.main()
