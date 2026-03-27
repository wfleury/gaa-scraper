#!/usr/bin/env python3
"""
Generate a static HTML dashboard from competition baselines.

Reads the JSON baselines saved by the competition monitor and produces
a single ``dashboard/index.html`` showing:
  - Upcoming Ballincollig fixtures across all competitions
  - Recent results
  - League tables with Ballincollig highlighted

Run after the competition monitor:
    python generate_dashboard.py
"""

import json
import os
from datetime import datetime
from html import escape

from competition_monitor.config import (
    AGE_GROUPS, BASELINE_DIR, CLUB_NAME, COMPETITIONS, competition_url,
)

DASHBOARD_DIR = "dashboard"
OUTPUT_FILE = os.path.join(DASHBOARD_DIR, "index.html")


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------

def _load_baselines():
    """Load all competition baselines and return {comp_name: baseline}."""
    baselines = {}
    for comp_name in COMPETITIONS:
        safe = comp_name.lower().replace(" ", "_").replace("/", "_")
        path = os.path.join(BASELINE_DIR, f"{safe}.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    baselines[comp_name] = json.load(f)
            except (json.JSONDecodeError, ValueError):
                pass
    return baselines


def _is_ours(match):
    """True if Ballincollig is home or away."""
    name = CLUB_NAME.lower()
    return (name in match.get("home", "").lower() or
            name in match.get("away", "").lower())


def _parse_date(date_str):
    """Try to parse a date string into a datetime for sorting."""
    for fmt in ("%d/%m/%Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.max


# ------------------------------------------------------------------
# HTML generation
# ------------------------------------------------------------------

_CSS = """\
:root {
  --primary: #1a5632;
  --primary-light: #e8f5e9;
  --accent: #ffc107;
  --bg: #f5f5f5;
  --card: #ffffff;
  --text: #212121;
  --muted: #757575;
  --border: #e0e0e0;
  --highlight: #fff8e1;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.5;
  max-width: 960px; margin: 0 auto; padding: 16px;
}
h1 { color: var(--primary); margin-bottom: 4px; font-size: 1.6em; }
.subtitle { color: var(--muted); font-size: 0.9em; margin-bottom: 20px; }
h2 { color: var(--primary); margin: 24px 0 12px; font-size: 1.25em;
     border-bottom: 2px solid var(--primary); padding-bottom: 4px; }
h3 { color: var(--primary); margin: 16px 0 8px; font-size: 1.05em; }
.card { background: var(--card); border-radius: 8px; padding: 16px;
        margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
th { background: var(--primary); color: white; text-align: left;
     padding: 8px 10px; font-weight: 600; }
td { padding: 6px 10px; border-bottom: 1px solid var(--border); }
tr.ours { background: var(--highlight); font-weight: 600; }
tr:hover { background: var(--primary-light); }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px;
         font-size: 0.75em; font-weight: 600; }
.badge-win { background: #c8e6c9; color: #2e7d32; }
.badge-loss { background: #ffcdd2; color: #c62828; }
.badge-draw { background: #fff9c4; color: #f57f17; }
.badge-postponed { background: #e0e0e0; color: #616161; }
.badge-upcoming { background: #bbdefb; color: #1565c0; }
a { color: var(--primary); }
.fixture-grid { display: grid; gap: 8px; }
.fixture-row { display: grid; grid-template-columns: 90px 1fr 60px;
               gap: 8px; align-items: center; padding: 6px 0;
               border-bottom: 1px solid var(--border); }
.fixture-date { font-weight: 600; font-size: 0.85em; }
.fixture-teams { }
.fixture-time { text-align: right; font-size: 0.85em; color: var(--muted); }
.empty { color: var(--muted); font-style: italic; padding: 12px 0; }
.tabs { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 16px; }
.tab { padding: 6px 14px; border-radius: 20px; cursor: pointer;
       border: 1px solid var(--border); background: var(--card);
       font-size: 0.85em; transition: all 0.2s; }
.tab.active { background: var(--primary); color: white; border-color: var(--primary); }
.tab-content { display: none; }
.tab-content.active { display: block; }
@media (max-width: 600px) {
  body { padding: 10px; }
  .fixture-row { grid-template-columns: 70px 1fr 50px; }
}
"""

_JS = """\
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.tabs').forEach(function(tabs) {
    var contents = tabs.parentElement.querySelectorAll('.tab-content');
    tabs.querySelectorAll('.tab').forEach(function(tab) {
      tab.addEventListener('click', function() {
        tabs.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
        contents.forEach(function(c) { c.classList.remove('active'); });
        tab.classList.add('active');
        var target = tab.getAttribute('data-target');
        var el = document.getElementById(target);
        if (el) el.classList.add('active');
      });
    });
  });
});
"""


def _gaa_total(score_str):
    try:
        g, p = score_str.split("-")
        return int(g) * 3 + int(p)
    except (ValueError, AttributeError):
        return 0


def _result_badge(match):
    hs = _gaa_total(match.get("home_score", "0-0"))
    aws = _gaa_total(match.get("away_score", "0-0"))
    is_home = CLUB_NAME.lower() in match.get("home", "").lower()
    ours = hs if is_home else aws
    theirs = aws if is_home else hs
    if ours > theirs:
        return '<span class="badge badge-win">W</span>'
    elif ours < theirs:
        return '<span class="badge badge-loss">L</span>'
    return '<span class="badge badge-draw">D</span>'


def _render_fixtures(fixtures):
    """Render a list of upcoming fixtures as HTML."""
    our = [f for f in fixtures if _is_ours(f)]
    our.sort(key=lambda f: _parse_date(f.get("date", "")))
    if not our:
        return '<p class="empty">No upcoming fixtures.</p>'
    rows = []
    for f in our:
        postponed = f.get("postponed")
        time_str = '<span class="badge badge-postponed">Postponed</span>' if postponed else escape(f.get("time", ""))
        rows.append(
            f'<div class="fixture-row">'
            f'<div class="fixture-date">{escape(f.get("date", ""))}</div>'
            f'<div class="fixture-teams">{escape(f["home"])} vs {escape(f["away"])}</div>'
            f'<div class="fixture-time">{time_str}</div>'
            f'</div>'
        )
    return '<div class="fixture-grid">' + "\n".join(rows) + '</div>'


def _render_results(results):
    """Render a list of results as HTML."""
    our = [r for r in results if _is_ours(r)]
    our.sort(key=lambda r: _parse_date(r.get("date", "")), reverse=True)
    if not our:
        return '<p class="empty">No results yet.</p>'
    rows = []
    for r in our:
        badge = _result_badge(r)
        rows.append(
            f'<div class="fixture-row">'
            f'<div class="fixture-date">{escape(r.get("date", ""))}</div>'
            f'<div class="fixture-teams">'
            f'{escape(r["home"])} {escape(r.get("home_score",""))} - '
            f'{escape(r.get("away_score",""))} {escape(r["away"])}'
            f'</div>'
            f'<div class="fixture-time">{badge}</div>'
            f'</div>'
        )
    return '<div class="fixture-grid">' + "\n".join(rows) + '</div>'


def _render_table(table):
    """Render a league table as an HTML table."""
    if not table:
        return '<p class="empty">No league table available.</p>'
    html = (
        '<table><thead><tr>'
        '<th>#</th><th>Team</th><th>Pld</th>'
        '<th>W</th><th>D</th><th>L</th>'
        '<th>PD</th><th>Pts</th>'
        '</tr></thead><tbody>'
    )
    for row in table:
        cls = ' class="ours"' if CLUB_NAME.lower() in row.get("team", "").lower() else ""
        html += (
            f'<tr{cls}>'
            f'<td>{row.get("position","")}</td>'
            f'<td>{escape(row.get("team",""))}</td>'
            f'<td>{row.get("played","")}</td>'
            f'<td>{row.get("won","")}</td>'
            f'<td>{row.get("drawn","")}</td>'
            f'<td>{row.get("lost","")}</td>'
            f'<td>{row.get("pd","")}</td>'
            f'<td>{row.get("pts","")}</td>'
            f'</tr>'
        )
    html += '</tbody></table>'
    return html


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def generate():
    baselines = _load_baselines()
    if not baselines:
        print("No baselines found — run the competition monitor first.")
        return

    now = datetime.now().strftime("%d %b %Y %H:%M")

    # Group competitions by age group
    by_age = {}
    for comp_name, comp_config in COMPETITIONS.items():
        ag = comp_config.get("age_group", "other")
        by_age.setdefault(ag, []).append((comp_name, comp_config))

    # Build the age group tabs + content
    age_labels = {"u13": "U13", "u14": "U14", "u15": "U15",
                  "u16": "U16", "minor": "Minor"}

    tabs_html = '<div class="tabs">'
    content_html = ""
    first = True
    for ag_key in ["u13", "u14", "u15", "u16", "minor"]:
        comps = by_age.get(ag_key, [])
        if not comps:
            continue
        label = age_labels.get(ag_key, ag_key.upper())
        active = " active" if first else ""
        tab_id = f"ag-{ag_key}"
        tabs_html += f'<div class="tab{active}" data-target="{tab_id}">{label}</div>'

        section = f'<div id="{tab_id}" class="tab-content{active}">'
        for comp_name, comp_config in comps:
            baseline = baselines.get(comp_name)
            url = competition_url(comp_config)
            section += f'<h3><a href="{url}" target="_blank">{escape(comp_name)}</a></h3>'
            section += '<div class="card">'
            if baseline:
                fixtures = list(baseline.get("fixtures", {}).values())
                results = list(baseline.get("results", {}).values())
                table = baseline.get("table", [])

                section += '<h3>Upcoming</h3>'
                section += _render_fixtures(fixtures)
                section += '<h3>Results</h3>'
                section += _render_results(results)
                section += '<h3>Table</h3>'
                section += _render_table(table)
            else:
                section += '<p class="empty">No data yet — waiting for first monitor run.</p>'
            section += '</div>'
        section += '</div>'
        content_html += section
        first = False

    tabs_html += '</div>'

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{CLUB_NAME} GAA – Competition Dashboard</title>
<style>{_CSS}</style>
</head>
<body>
<h1>{CLUB_NAME} GAA</h1>
<p class="subtitle">Competition Dashboard &mdash; updated {now}</p>
{tabs_html}
{content_html}
<script>{_JS}</script>
</body>
</html>
"""
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written to {OUTPUT_FILE}")


if __name__ == "__main__":
    generate()
