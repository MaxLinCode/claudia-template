import datetime
import html


def render_dashboard_html(system_streak, last_sync, habit_rows, daily_quote):
    streak_value = str(system_streak)
    today_str = datetime.date.today().isoformat()
    completed_today = sum(1 for row in habit_rows if row["last_date"] == today_str and "✅" in row["status"])
    touched_today = sum(1 for row in habit_rows if row["last_date"] == today_str)
    top_streak = max((row["streak"] for row in habit_rows), default=0)
    recent_wins = [row for row in habit_rows if row["last_date"] == today_str and "✅" in row["status"]]
    week_header_days = habit_rows[0]["week"] if habit_rows else []
    habit_cards = []
    table_rows = []
    heatmap_rows = []

    for row in habit_rows:
        streak_display = f"🔥 {row['streak']}" if row["streak"] > 3 else str(row["streak"])
        status_class = (
            "status-done" if "✅" in row["status"]
            else "status-paused" if "⏸️" in row["status"]
            else "status-missed" if "❌" in row["status"]
            else "status-new"
        )
        safe_name = html.escape(row["display_name"])
        safe_last_date = html.escape(row["last_date_display"])
        safe_status = html.escape(row["status"])
        activity_note = (
            "Completed today" if row["last_date"] == today_str and "✅" in row["status"]
            else "Updated today" if row["last_date"] == today_str
            else "No update today"
        )
        activity_class = "habit-note-good" if activity_note == "Completed today" else "habit-note-neutral"

        habit_cards.append(
            f"""
            <article class="habit-card">
              <div class="habit-card-topline">
                <span class="habit-kicker">{safe_last_date}</span>
                <span class="status-pill {status_class}">{safe_status}</span>
              </div>
              <h2>{safe_name}</h2>
              <p class="habit-note {activity_class}">{html.escape(activity_note)}</p>
              <dl>
                <div>
                  <dt>Streak</dt>
                  <dd>{html.escape(streak_display)}</dd>
                </div>
                <div>
                  <dt>Last Logged</dt>
                  <dd>{safe_last_date}</dd>
                </div>
              </dl>
            </article>
            """
        )

        table_rows.append(
            f"""
            <tr>
              <td>{safe_name}</td>
              <td>{html.escape(streak_display)}</td>
              <td>{safe_last_date}</td>
              <td><span class="status-pill {status_class}">{safe_status}</span></td>
            </tr>
            """
        )

        week_cells = []
        for day in row["week"]:
            day_status = day["status"]
            momentum = day["momentum"]

            if "✅" in day_status and momentum > 0:
                week_class = f"heat-{momentum}"
            elif "⏸️" in day_status:
                week_class = "heat-paused"
            elif "❌" in day_status:
                week_class = "heat-missed"
            else:
                week_class = "heat-0"

            week_cells.append(
                f"""
                <div class="week-cell-group">
                  <div class="heat-cell {week_class}" title="{html.escape(day['label'])} {html.escape(day['date'])}: {html.escape(day_status or 'No entry')}"></div>
                </div>
                """
            )

        heatmap_rows.append(
            f"""
            <div class="weekly-row">
              <span class="weekly-label">{safe_name}</span>
              {''.join(week_cells)}
            </div>
            """
        )

    wins_markup = (
        "<ul class=\"wins-list\">"
        + "".join(
            f"<li><strong>{html.escape(row['display_name'])}</strong><span class=\"status-pill status-done\">✅ Today</span></li>"
            for row in recent_wins
        )
        + "</ul>"
        if recent_wins
        else "<p class=\"wins-empty\">No completed habits logged today yet. The next update can change the shape of the board fast.</p>"
    )
    week_header_markup = "".join(
        f'<span title="{html.escape(day["date"])}">{html.escape(day["label"][0])}</span>'
        for day in week_header_days
    )
    quote_text = html.escape(daily_quote["text"])
    quote_author = html.escape(daily_quote["author"])

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="dashboard-last-sync" content="{html.escape(last_sync)}" />
    <title>Life Dashboard</title>
    <style>
      :root {{
        --bg: #f5f7fb;
        --bg-2: #eef2f7;
        --panel: rgba(255, 255, 255, 0.78);
        --panel-strong: rgba(255, 255, 255, 0.92);
        --ink: #111827;
        --muted: #667085;
        --muted-2: #98a2b3;
        --line: rgba(17, 24, 39, 0.08);
        --accent: #5b7cfa;
        --done: #027a48;
        --paused: #b54708;
        --missed: #b42318;
        --new: #475467;
        --heat-0: #e8edf5;
        --heat-1: #c9daff;
        --heat-2: #b7ceff;
        --heat-3: #9fc0ff;
        --heat-4: #7fa9ff;
        --heat-5: #6f94f5;
        --heat-6: #567adc;
        --heat-7: #3d5fc2;
        --heat-paused: #ece7d8;
        --heat-missed: #f2dddd;
        --shadow: 0 20px 60px rgba(15, 23, 42, 0.08);
        --radius-xl: 28px;
        --radius-lg: 22px;
        --radius-md: 16px;
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(91, 124, 250, 0.16), transparent 20%),
          radial-gradient(circle at top right, rgba(15, 23, 42, 0.06), transparent 24%),
          linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
      }}

      .shell {{
        max-width: 1280px;
        margin: 0 auto;
        padding: 28px 20px 56px;
      }}

      .topbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
      }}

      .brand {{
        display: flex;
        align-items: center;
        gap: 12px;
      }}

      .brand-mark {{
        width: 12px;
        height: 12px;
        border-radius: 999px;
        background: linear-gradient(135deg, var(--accent) 0%, #7dd3fc 100%);
        box-shadow: 0 0 0 8px rgba(91, 124, 250, 0.08);
      }}

      .brand-copy {{
        display: flex;
        flex-direction: column;
        gap: 3px;
      }}

      .brand-copy strong {{
        font-size: 0.9rem;
        letter-spacing: -0.01em;
      }}

      .brand-copy span,
      .sync-meta {{
        color: var(--muted);
        font-size: 0.9rem;
      }}

      .hero {{
        background: var(--panel-strong);
        border: 1px solid var(--line);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow);
        padding: 28px;
        backdrop-filter: blur(18px);
      }}

      .eyebrow {{
        margin: 0 0 8px;
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }}

      h1 {{
        margin: 0;
        max-width: 12ch;
        font-size: clamp(2.2rem, 6vw, 4.2rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
      }}

      .hero-copy {{
        display: flex;
        justify-content: space-between;
        gap: 24px;
        margin-top: 18px;
      }}

      .hero-copy p {{
        margin: 0;
        max-width: 62ch;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
      }}

      .quote-kicker {{
        margin-bottom: 14px;
        color: var(--accent);
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.16em;
      }}

      .quote-mark {{
        color: var(--ink);
      }}

      .daily-quote {{
        margin-top: 24px;
        padding: 24px 28px 22px;
        border-top: 1px solid var(--line);
        text-align: center;
      }}

      .daily-quote p {{
        margin: 0;
        color: var(--ink);
        font-size: clamp(1.2rem, 2.2vw, 1.75rem);
        line-height: 1.35;
        letter-spacing: -0.025em;
        font-weight: 500;
        max-width: 34ch;
        margin-inline: auto;
      }}

      .daily-quote cite {{
        display: block;
        margin-top: 14px;
        color: var(--muted);
        font-size: 0.85rem;
        font-style: normal;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
      }}

      .hero-grid {{
        display: grid;
        grid-template-columns: 1.4fr 1fr;
        gap: 18px;
        margin-top: 28px;
      }}

      .summary-strip {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
      }}

      .metric-panel,
      .wins-panel,
      .table-wrap,
      .habit-card,
      .heatmap-panel {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        backdrop-filter: blur(16px);
      }}

      .metric-panel,
      .wins-panel,
      .heatmap-panel {{
        padding: 20px;
      }}

      .metric-label {{
        color: var(--muted-2);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }}

      .metric-value {{
        margin: 10px 0 0;
        font-size: clamp(2rem, 4vw, 2.6rem);
        font-weight: 700;
        letter-spacing: -0.04em;
      }}

      .metric-subtle,
      .meta {{
        margin-top: 8px;
        color: var(--muted);
        font-size: 0.95rem;
      }}

      .section-title {{
        margin: 30px 0 14px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted-2);
      }}

      .content-grid {{
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 18px;
        margin-top: 22px;
      }}

      .habit-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }}

      .habit-card {{
        padding: 20px;
      }}

      .habit-card-topline {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        margin-bottom: 14px;
      }}

      .habit-kicker {{
        color: var(--muted-2);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
      }}

      .habit-card h2 {{
        margin: 0;
        font-size: 1.1rem;
        letter-spacing: -0.02em;
      }}

      .habit-note {{
        margin: 8px 0 0;
        font-size: 0.95rem;
      }}

      .habit-note-good {{
        color: var(--done);
      }}

      .habit-note-neutral {{
        color: var(--muted);
      }}

      .habit-card dl {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 0;
      }}

      .habit-card dt {{
        color: var(--muted-2);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}

      .habit-card dd {{
        margin: 6px 0 0;
        font-size: 1.05rem;
        font-weight: 600;
      }}

      .wins-panel h2,
      .heatmap-panel h2 {{
        margin: 0;
        font-size: 0.95rem;
        letter-spacing: -0.02em;
      }}

      .wins-list {{
        margin: 18px 0 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 12px;
      }}

      .wins-list li {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        padding: 12px 14px;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        background: rgba(255, 255, 255, 0.5);
      }}

      .wins-list strong {{
        font-size: 0.95rem;
      }}

      .wins-empty,
      .heatmap-panel p {{
        margin-top: 18px;
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.5;
      }}

      .weekly-header {{
        display: grid;
        grid-template-columns: 150px repeat(7, 14px);
        gap: 10px;
        align-items: end;
        margin-top: 18px;
        margin-bottom: 10px;
      }}

      .weekly-header span {{
        font-size: 0.72rem;
        color: var(--muted-2);
        text-align: center;
      }}

      .weekly-header .weekly-spacer {{
        text-align: left;
      }}

      .weekly-grid {{
        display: grid;
        gap: 12px;
      }}

      .weekly-row {{
        display: grid;
        grid-template-columns: 150px repeat(7, 14px);
        gap: 10px;
        align-items: center;
      }}

      .weekly-label {{
        font-size: 0.93rem;
      }}

      .week-cell-group {{
        display: flex;
        align-items: center;
        justify-content: center;
      }}

      .heat-cell {{
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid rgba(17, 24, 39, 0.04);
      }}

      .heat-0 {{ background: var(--heat-0); }}
      .heat-1 {{ background: var(--heat-1); }}
      .heat-2 {{ background: var(--heat-2); }}
      .heat-3 {{ background: var(--heat-3); }}
      .heat-4 {{ background: var(--heat-4); }}
      .heat-5 {{ background: var(--heat-5); }}
      .heat-6 {{ background: var(--heat-6); }}
      .heat-7 {{ background: var(--heat-7); }}
      .heat-paused {{ background: var(--heat-paused); }}
      .heat-missed {{ background: var(--heat-missed); }}

      .table-wrap {{
        overflow: hidden;
      }}

      table {{
        width: 100%;
        border-collapse: collapse;
      }}

      th, td {{
        text-align: left;
        padding: 14px 16px;
        border-bottom: 1px solid var(--line);
      }}

      th {{
        font-size: 0.76rem;
        color: var(--muted-2);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        background: rgba(248, 250, 252, 0.9);
      }}

      tr:last-child td {{
        border-bottom: none;
      }}

      .status-pill {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 0.82rem;
        font-weight: 700;
        background: #eef2ff;
      }}

      .status-done {{
        color: var(--done);
        background: rgba(2, 122, 72, 0.12);
      }}

      .status-paused {{
        color: var(--paused);
        background: rgba(181, 71, 8, 0.12);
      }}

      .status-missed {{
        color: var(--missed);
        background: rgba(180, 35, 24, 0.12);
      }}

      .status-new {{
        color: var(--new);
        background: rgba(71, 84, 103, 0.12);
      }}

      @media (max-width: 980px) {{
        .hero-copy,
        .hero-grid,
        .content-grid,
        .summary-strip,
        .habit-grid,
        .weekly-row {{
          display: grid;
          grid-template-columns: 1fr;
        }}
      }}

      @media (max-width: 720px) {{
        .table-wrap {{
          overflow-x: auto;
        }}

        .topbar {{
          flex-direction: column;
          align-items: flex-start;
        }}

        .heatmap-panel {{
          overflow-x: auto;
        }}

        .weekly-header,
        .weekly-row {{
          min-width: 318px;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <div class="topbar">
        <div class="brand">
          <div class="brand-mark"></div>
          <div class="brand-copy">
            <strong>Life Dashboard</strong>
            <span>Personal operating system</span>
          </div>
        </div>
        <div class="sync-meta">Last sync: {html.escape(last_sync)}</div>
      </div>

      <section class="hero">
        <p class="eyebrow">Daily Overview</p>
        <h1>Today is either on track or it isn't.</h1>
        <div class="hero-copy">
          <p>
            A calm, fast read on where the day stands. This dashboard is generated from your habit trackers,
            so the board stays aligned with the markdown source of truth without extra upkeep.
          </p>
        </div>
        <div class="daily-quote" id="daily-quote">
          <div class="quote-kicker">Daily Focus</div>
          <p><span class="quote-mark">"</span>{quote_text}<span class="quote-mark">"</span></p>
          <cite>- {quote_author}</cite>
        </div>

        <div class="hero-grid">
          <div class="summary-strip">
            <section class="metric-panel">
              <div class="metric-label">Done Today</div>
              <div class="metric-value">{completed_today}</div>
              <div class="metric-subtle">{touched_today} habits touched today</div>
            </section>
            <section class="metric-panel">
              <div class="metric-label">Best Streak</div>
              <div class="metric-value">{top_streak}</div>
              <div class="metric-subtle">Current strongest line</div>
            </section>
            <section class="metric-panel">
              <div class="metric-label">Consistency</div>
              <div class="metric-value">{html.escape(streak_value)}</div>
              <div class="metric-subtle">Overall momentum</div>
            </section>
          </div>

          <section class="wins-panel">
            <h2>Recent Wins</h2>
            {wins_markup}
          </section>
        </div>
      </section>

      <section class="content-grid">
        <div>
          <h2 class="section-title">Habit Cards</h2>
          <section class="habit-grid">
            {''.join(habit_cards)}
          </section>
        </div>
        <div>
          <h2 class="section-title">Consistency Map</h2>
          <section class="heatmap-panel">
            <h2>Streak Intensity</h2>
            <p>
              A weekly contribution-style view of each habit over the last seven days. Darker blocks mean stronger streak momentum.
            </p>
            <div class="weekly-header">
              <span class="weekly-spacer"></span>
              {week_header_markup}
            </div>
            <div class="weekly-grid">
              {''.join(heatmap_rows)}
            </div>
          </section>
        </div>
      </section>

      <h2 class="section-title">Tracker Table</h2>
      <section class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Habit</th>
              <th>Current Streak</th>
              <th>Last Logged</th>
              <th>Latest Status</th>
            </tr>
          </thead>
          <tbody>
            {''.join(table_rows)}
          </tbody>
        </table>
      </section>
    </main>
    <script>
      const currentLastSync = document
        .querySelector('meta[name="dashboard-last-sync"]')
        ?.getAttribute('content');
      async function checkForDashboardUpdate() {{
        try {{
          const response = await fetch(`${{window.location.pathname}}?ts=${{Date.now()}}`, {{
            cache: 'no-store',
          }});
          const text = await response.text();
          const match = text.match(/<meta name="dashboard-last-sync" content="([^"]+)"/);
          const latestLastSync = match?.[1];

          if (latestLastSync && currentLastSync && latestLastSync !== currentLastSync) {{
            window.location.reload();
          }}
        }} catch (_error) {{
          // Ignore polling failures when the page is opened from the filesystem.
        }}
      }}

      window.setInterval(checkForDashboardUpdate, 15000);
    </script>
  </body>
</html>
"""
