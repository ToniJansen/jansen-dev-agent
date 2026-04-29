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

import base64

import subprocess

import plotly.graph_objects as go
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
    needs_fixes = 0
    merged_prs: list[dict] = []

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

        if pr.get("merged_at"):
            merged_prs.append(pr)
        else:
            body = pr.get("body") or ""
            if "NEEDS FIXES" in body or "❌" in body:
                needs_fixes += 1

    days_sorted = sorted(prs_by_day)

    return {
        "total_prs": len(prs),
        "py_count": py_count,
        "sql_count": sql_count,
        "total_critical": total_c,
        "total_warning": total_w,
        "total_info": total_i,
        "needs_fixes": needs_fixes,
        "approved": len(merged_prs),
        "merged_prs": merged_prs,
        "days": days_sorted,
        "prs_per_day": [prs_by_day[d] for d in days_sorted],
        "prs": prs,
    }


# ── Chart generation ───────────────────────────────────────────────────────

def _chart_png_b64(days: list[str], counts: list[int]) -> str:
    labels = [d[5:] for d in days[-14:]]  # "2026-04-29" → "04-29"
    values = counts[-14:]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color="#3b82f6",
        marker_line_width=0,
    ))
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#6b7280", size=11),
        margin=dict(l=50, r=20, t=10, b=60),
        height=240,
        yaxis=dict(gridcolor="#f3f4f6", tickformat="d", showline=False),
        xaxis=dict(gridcolor="#f3f4f6", showline=False),
        showlegend=False,
        bargap=0.3,
    )
    img_bytes = fig.to_image(format="png", width=1000, height=240, scale=2)
    subprocess.run(["pkill", "-f", "kaleido/executable"], capture_output=True)
    return base64.b64encode(img_bytes).decode()


# ── HTML report ────────────────────────────────────────────────────────────

def _build_html(m: dict, repo: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    chart_b64 = _chart_png_b64(m["days"], m["prs_per_day"])

    rows = ""
    for pr in sorted(m["prs"], key=lambda p: p["created_at"], reverse=True)[:20]:
        date = pr["created_at"][:10]
        if pr.get("merged_at"):
            status = "✅ Merged"
        elif "NEEDS FIXES" in (pr.get("body") or "") or "❌" in (pr.get("body") or ""):
            status = "❌ Needs fixes"
        else:
            status = "🔄 Open"
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

    merged_rows = ""
    for pr in sorted(m["merged_prs"], key=lambda p: p["merged_at"], reverse=True)[:20]:
        date = pr["merged_at"][:10]
        c, w, i = _parse_findings(pr.get("body") or "")
        findings = f"🔴 {c}C &nbsp;🟡 {w}W &nbsp;🔵 {i}I"
        ft = _file_type(pr["title"])
        url = pr["html_url"]
        short_title = pr["title"].replace("[Agent] ", "")[:55]
        merged_rows += f"""
        <tr>
          <td>{date}</td>
          <td><a href="{url}" target="_blank">{short_title}</a></td>
          <td><span class="badge badge-{ft.lower()}">{ft}</span></td>
          <td style="font-size:.8rem">{findings}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>jansen_dev_agent — Metrics</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: #f9fafb; color: #111827; min-height: 100vh; padding: 2rem; }}
    .report-header {{ margin-bottom: 2rem; }}
    .report-header .eyebrow {{ font-size: .75rem; font-weight: 700; color: #2563eb;
                               text-transform: uppercase; letter-spacing: .12em;
                               margin-bottom: .35rem; }}
    h1 {{ font-size: 1.8rem; font-weight: 800; color: #111827; margin-bottom: .3rem; }}
    .sub {{ color: #6b7280; font-size: .875rem; margin-bottom: 0; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
              gap: 1rem; margin-bottom: 2rem; page-break-inside: avoid; }}
    .card {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
             padding: 1.25rem; text-align: center;
             box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
    .card .val {{ font-size: 2.4rem; font-weight: 800; line-height: 1; }}
    .card .lbl {{ font-size: .78rem; color: #9ca3af; margin-top: .4rem; text-transform: uppercase;
                  letter-spacing: .06em; }}
    .red   {{ color: #dc2626; }}
    .yellow{{ color: #d97706; }}
    .blue  {{ color: #2563eb; }}
    .green {{ color: #16a34a; }}
    .slate {{ color: #374151; }}
    .section {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
                padding: 1.5rem; margin-bottom: 2rem; page-break-inside: avoid;
                box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
    .section h2 {{ font-size: .8rem; font-weight: 700; margin-bottom: 1.25rem;
                   color: #9ca3af; text-transform: uppercase; letter-spacing: .1em; }}
    .chart-wrap {{ max-width: 100%; overflow: hidden; background: #fff;
                   border-radius: 8px; }}
    .before-after {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
    .ba-box {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px;
               padding: 1.25rem; text-align: center; }}
    .ba-box .big {{ font-size: 3rem; font-weight: 800; }}
    .ba-box .desc {{ font-size: .85rem; color: #6b7280; margin-top: .5rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .875rem; }}
    th {{ text-align: left; padding: .6rem .75rem; color: #6b7280; font-weight: 600;
          border-bottom: 2px solid #f3f4f6; }}
    td {{ padding: .6rem .75rem; border-bottom: 1px solid #f3f4f6; color: #374151; }}
    td a {{ color: #2563eb; text-decoration: none; }}
    td a:hover {{ text-decoration: underline; }}
    .badge {{ display: inline-block; padding: .2rem .6rem; border-radius: 99px;
              font-size: .72rem; font-weight: 600; }}
    .badge-python {{ background: #eff6ff; color: #1d4ed8; }}
    .badge-sql    {{ background: #fefce8; color: #a16207; }}
    .badge-other  {{ background: #f0fdf4; color: #166534; }}
    .repo-link {{ color: #6b7280; font-size: .85rem; }}
    .repo-link a {{ color: #2563eb; }}
  </style>
</head>
<body>
  <div class="report-header">
    <div class="eyebrow">GitHub Repository Report</div>
    <h1>Agent PR Activity — {repo.split("/")[-1]}</h1>
    <p class="sub">
      <a class="repo-link" href="https://github.com/{repo}" target="_blank">github.com/{repo}</a>
      &nbsp;·&nbsp; Generated: {now}
    </p>
  </div>

  <div class="cards">
    <div class="card"><div class="val slate">{m['total_prs']}</div>
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
      <img src="data:image/png;base64,{chart_b64}" style="width:100%;border-radius:8px;"/>
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
    <h2>Fixes Applied — Merged PRs ✅</h2>
    <table>
      <thead><tr><th>Merged</th><th>File</th><th>Type</th><th>Issues Fixed</th></tr></thead>
      <tbody>{merged_rows}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>All Recent PRs</h2>
    <table>
      <thead><tr><th>Date</th><th>PR</th><th>Type</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

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
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(f"file://{html_path.absolute()}", wait_until="domcontentloaded")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
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
