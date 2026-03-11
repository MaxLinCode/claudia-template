# Claudia — AI Habit Coach Template

A habit tracking system powered by an AI accountability partner. Works out of the box with **Cursor**, **Claude Code**, and **Codex**. Open the project and start chatting — your coach will guide you through logging habits, reflecting on patterns, and maintaining streaks.

## Supported Tools

| Tool | Config File | Ready |
| :--- | :--- | :---: |
| [Cursor](https://cursor.com) | `.cursor/rules/context.md` | ✅ |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `CLAUDE.md` | ✅ |
| [Codex](https://openai.com/index/introducing-codex/) | `AGENTS.md` | ✅ |

## How It Works

1. **Open this project** in Cursor, Claude Code, or Codex.
2. Your coach reads the dashboard, asks about your day, and logs your habits.
3. After habit updates, the coach runs `python3 tools/sync_dashboard.py` to regenerate the dashboard views.

## Project Structure

```
habits/
├── dashboard.md              # Auto-generated overview of all habits
├── dashboard.html            # Auto-generated visual dashboard
├── journal/                  # Daily journal habit
│   ├── context.md            # Rules and interaction protocols
│   ├── tracker.md            # Date/status log
│   └── entries/              # Individual journal entries (by month)
├── leetcode/                 # Coding interview practice
│   ├── context.md
│   └── tracker.md
├── job-search/               # Job-search momentum habit
│   ├── context.md
│   ├── tracker.md
│   └── journal.md
└── stretch-rehab/            # Mobility and rehab work
    ├── context.md
    ├── tracker.md
    └── journal.md
tools/
├── dashboard_renderer.py     # Renders the HTML dashboard
├── quotes_library.py         # Daily quote rotation
├── serve_dashboard.py        # Local preview server
└── sync_dashboard.py         # Syncs tracker data → dashboard files
CLAUDE.md                     # Agent rules for Claude Code
AGENTS.md                     # Agent rules for Codex
.cursor/rules/context.md      # Agent rules for Cursor
```

## Adding a New Habit (You can just ask AI to do this)

1. Create a folder under `habits/` (e.g. `habits/meditation/`).
2. Add a `context.md` defining the habit's purpose, frequency, and rules.
3. Add an empty `tracker.md` with the table header:
   ```
   | Date | Status | Note |
   | :--- | :---: | :--- |
   ```
4. Optionally add a `journal.md` for freeform notes.
5. Tell your coach about the new habit — it will pick it up automatically.

## Status Key

- ✅ Done
- ❌ Missed
- ⏸️ Skipped (e.g. rest day, sick)

## Customization

- **Agent persona:** Edit `CLAUDE.md`, `AGENTS.md`, or `.cursor/rules/context.md` (depending on your tool) to change the coach's tone, philosophy, or interaction style.
- **Habit rules:** Each habit's `context.md` controls how the agent interacts with that specific habit (frequency, backup protocols, coaching output, etc.).
- **Dashboard sync:** Run `python3 tools/sync_dashboard.py` after tracker changes, or let your coaching agent do it for you.
- **Dashboard preview:** Run `python3 tools/serve_dashboard.py` and open `http://localhost:8000/habits/dashboard.html`.
