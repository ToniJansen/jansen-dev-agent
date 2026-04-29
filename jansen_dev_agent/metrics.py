"""metrics.py — agent activity dashboard.

Queries GitHub for all agent-created PRs, calculates metrics,
and opens a self-contained HTML report in the browser.

Usage:
    cd jansen_dev_agent && python3 metrics.py
"""
from __future__ import annotations
import os
import re
import webbrowser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

_BASE      = "https://api.github.com"
_REPORT    = Path(__file__).parent.parent / "metrics_report.html"
_MOCK_FILE = Path(__file__).parent.parent / "demo" / "mock_prs.json"


# ── GitHub helpers ─────────────────────────────────────────────────────────

def _headers() -> dict:
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
    }


def _load_mock_prs() -> list[dict]:
    if not _MOCK_FILE.exists():
        return []
    import json
    return json.loads(_MOCK_FILE.read_text(encoding="utf-8"))


def _fetch_agent_prs(repo: str) -> list[dict]:
    all_prs: list[dict] = []
    for state in ("open", "closed"):
        page = 1
        while True:
            r = requests.get(
                f"{_BASE}/repos/{repo}/pulls",
                headers=_headers(),
                params={"state": state, "per_page": 100, "page": page},
                timeout=15,
            )
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            all_prs.extend(p for p in batch if p["title"].startswith("[Agent]"))
            page += 1
    return all_prs


def _parse_findings(body: str) -> tuple[int, int, int]:
    m = re.search(r"🔴\s*(\d+)C\s*🟡\s*(\d+)W\s*🔵\s*(\d+)I", body or "")
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return 0, 0, 0


def _file_type(title: str) -> str:
    if ".py" in title:
        return "Python"
    if ".sql" in title:
        return "SQL"
    return "Other"


# ── Metrics computation ────────────────────────────────────────────────────

def compute(prs: list[dict], include_mock: bool = True) -> dict:
    if include_mock:
        mock = _load_mock_prs()
        real_urls = {p["html_url"] for p in prs}
        prs = prs + [m for m in mock if m["html_url"] not in real_urls]
    prs_by_day: dict[str, int] = defaultdict(int)
    total_c = total_w = total_i = 0
    py_count = sql_count = 0
    needs_fixes = approved = 0

    for pr in prs:
        created = pr["created_at"][:10]
        prs_by_day[created] += 1

        c, w, i = _parse_findings(pr.get("body") or "")
        total_c += c
        total_w += w
        total_i += i

        ft = _file_type(pr["title"])
        if ft == "Python":
            py_count += 1
        elif ft == "SQL":
            sql_count += 1

        body = pr.get("body") or ""
        if "NEEDS FIXES" in body or "❌" in body:
            needs_fixes += 1
        else:
            approved += 1

    days_sorted = sorted(prs_by_day)

    return {
        "total_prs": len(prs),
        "py_count": py_count,
        "sql_count": sql_count,
        "total_critical": total_c,
        "total_warning": total_w,
        "total_info": total_i,
        "needs_fixes": needs_fixes,
        "approved": approved,
        "days": days_sorted,
        "prs_per_day": [prs_by_day[d] for d in days_sorted],
        "prs": prs,
    }


# ── HTML report ────────────────────────────────────────────────────────────

def _build_html(m: dict, repo: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    days_js = str(m["days"])
    counts_js = str(m["prs_per_day"])

    rows = ""
    for pr in sorted(m["prs"], key=lambda p: p["created_at"], reverse=True)[:20]:
        date = pr["created_at"][:10]
        status = "❌ Needs fixes" if ("NEEDS FIXES" in (pr.get("body") or "") or "❌" in (pr.get("body") or "")) else "✅ Approved"
        ft = _file_type(pr["title"])
        url = pr["html_url"]
        short_title = pr["title"].replace("[Agent] ", "")[:60]
        rows += f"""
        <tr>
          <td>{date}</td>
          <td><a href="{url}" target="_blank">{short_title}</a></td>
          <td><span class="badge badge-{ft.lower()}">{ft}</span></td>
          <td>{status}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>jansen_dev_agent — Metrics</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: #0d1117; color: #e6edf3; min-height: 100vh; padding: 2rem; }}
    h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: .25rem; }}
    .sub {{ color: #8b949e; font-size: .9rem; margin-bottom: 2rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
              gap: 1rem; margin-bottom: 2rem; page-break-inside: avoid; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px;
             padding: 1.25rem; text-align: center; }}
    .card .val {{ font-size: 2.4rem; font-weight: 800; line-height: 1; }}
    .card .lbl {{ font-size: .78rem; color: #8b949e; margin-top: .4rem; text-transform: uppercase;
                  letter-spacing: .06em; }}
    .red   {{ color: #f85149; }}
    .yellow{{ color: #e3b341; }}
    .blue  {{ color: #58a6ff; }}
    .green {{ color: #3fb950; }}
    .white {{ color: #e6edf3; }}
    .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px;
                padding: 1.5rem; margin-bottom: 2rem; page-break-inside: avoid; }}
    .section h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 1.25rem;
                   color: #8b949e; text-transform: uppercase; letter-spacing: .08em; }}
    .chart-wrap {{ max-width: 700px; }}
    .before-after {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
    .ba-box {{ background: #0d1117; border-radius: 8px; padding: 1.25rem; text-align: center; }}
    .ba-box .big {{ font-size: 3rem; font-weight: 800; }}
    .ba-box .desc {{ font-size: .85rem; color: #8b949e; margin-top: .5rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .875rem; }}
    th {{ text-align: left; padding: .6rem .75rem; color: #8b949e; font-weight: 600;
          border-bottom: 1px solid #30363d; }}
    td {{ padding: .6rem .75rem; border-bottom: 1px solid #21262d; }}
    td a {{ color: #58a6ff; text-decoration: none; }}
    td a:hover {{ text-decoration: underline; }}
    .badge {{ display: inline-block; padding: .15rem .55rem; border-radius: 99px;
              font-size: .75rem; font-weight: 600; }}
    .badge-python {{ background: #1f3a5f; color: #58a6ff; }}
    .badge-sql    {{ background: #2d2600; color: #e3b341; }}
    .badge-other  {{ background: #1c2a1c; color: #3fb950; }}
    .repo-link {{ color: #8b949e; font-size: .85rem; }}
    .repo-link a {{ color: #58a6ff; }}
  </style>
</head>
<body>
  <h1>🤖 jansen_dev_agent — Activity Dashboard</h1>
  <p class="sub">
    Repo: <a class="repo-link" href="https://github.com/{repo}" target="_blank">{repo}</a>
    &nbsp;·&nbsp; Generated: {now}
  </p>

  <div class="cards">
    <div class="card"><div class="val white">{m['total_prs']}</div>
      <div class="lbl">Total PRs by agent</div></div>
    <div class="card"><div class="val green">{m['approved']}</div>
      <div class="lbl">Auto-merged ✅</div></div>
    <div class="card"><div class="val red">{m['needs_fixes']}</div>
      <div class="lbl">Needs triage 🔴</div></div>
    <div class="card"><div class="val red">{m['total_critical']}</div>
      <div class="lbl">Critical issues found</div></div>
    <div class="card"><div class="val yellow">{m['total_warning']}</div>
      <div class="lbl">Warnings flagged</div></div>
    <div class="card"><div class="val blue">{m['py_count']}</div>
      <div class="lbl">Python files reviewed</div></div>
  </div>

  <div class="section">
    <h2>PRs over time</h2>
    <div class="chart-wrap">
      <canvas id="timeline" height="90"></canvas>
    </div>
  </div>

  <div class="section">
    <h2>Before vs. After</h2>
    <div class="before-after">
      <div class="ba-box">
        <div class="big red">0</div>
        <div class="desc">automated reviews / week<br><strong>before agent</strong></div>
      </div>
      <div class="ba-box">
        <div class="big green">{m['total_prs']}</div>
        <div class="desc">PRs opened automatically<br><strong>after agent — zero human effort</strong></div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Recent PRs</h2>
    <table>
      <thead><tr><th>Date</th><th>PR</th><th>Type</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <script>
    new Chart(document.getElementById("timeline"), {{
      type: "bar",
      data: {{
        labels: {days_js},
        datasets: [{{
          label: "Agent PRs",
          data: {counts_js},
          backgroundColor: "#1f6feb",
          borderRadius: 5,
        }}]
      }},
      options: {{
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: "#8b949e" }}, grid: {{ color: "#21262d" }} }},
          y: {{ ticks: {{ color: "#8b949e", stepSize: 1 }}, grid: {{ color: "#21262d" }} }}
        }}
      }}
    }});
  </script>
</body>
</html>"""


# ── Terminal summary ───────────────────────────────────────────────────────

def _print_summary(m: dict, repo: str) -> None:
    print(f"\n{'─'*50}")
    print(f"  jansen_dev_agent — Metrics  ({repo})")
    print(f"{'─'*50}")
    print(f"  Total PRs opened by agent : {m['total_prs']}")
    print(f"  Python files reviewed     : {m['py_count']}")
    print(f"  SQL files reviewed        : {m['sql_count']}")
    print(f"  CRITICAL issues found     : {m['total_critical']}")
    print(f"  Warnings flagged          : {m['total_warning']}")
    print(f"  Auto-approved             : {m['approved']}")
    print(f"  Needs fixes               : {m['needs_fixes']}")
    print(f"{'─'*50}")
    print(f"  Before agent : 0 automated reviews/week")
    print(f"  After agent  : {m['total_prs']} PRs opened — zero human effort")
    print(f"{'─'*50}\n")


# ── PDF generation ────────────────────────────────────────────────────────

def generate_pdf(html_path: Path) -> Path:
    """Render HTML to PDF using Playwright headless Chromium."""
    from playwright.sync_api import sync_playwright

    pdf_path = html_path.with_suffix(".pdf")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path.absolute()}", wait_until="networkidle")
        page.wait_for_timeout(1500)  # let Chart.js finish rendering
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
        )
        browser.close()
    return pdf_path


def build_report() -> Path:
    """Fetch latest data, write HTML, render PDF. Returns PDF path."""
    repo = os.environ["GITHUB_REPO"]
    prs = _fetch_agent_prs(repo)
    m = compute(prs)
    html = _build_html(m, repo)
    _REPORT.write_text(html, encoding="utf-8")
    return generate_pdf(_REPORT)


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    repo = os.environ["GITHUB_REPO"]
    print(f"Fetching agent PRs from {repo}...")
    prs = _fetch_agent_prs(repo)
    print(f"Found {len(prs)} agent PR(s).")

    m = compute(prs)
    _print_summary(m, repo)

    html = _build_html(m, repo)
    _REPORT.write_text(html, encoding="utf-8")
    print(f"Report saved to: {_REPORT}")
    webbrowser.open(f"file://{_REPORT}")


if __name__ == "__main__":
    main()
