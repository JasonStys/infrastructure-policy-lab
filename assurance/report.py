"""Escaped scriptless offline assurance reports with no raw plan values. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: render — line 22
# parameter: report — line 22
# variable: rows — line 24
# variable: key — line 28
# variable: row — line 31
# definition: export — line 42
# parameter: directory — line 42
# parameter: report — line 42
# END CODE MAP

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from assurance.io import canonical, new_directory


def render(report: dict[str, Any]) -> str:
    """Render inert HTML using escaped findings only; deny external content, scripts, forms and frames."""
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row[key]))}</td>"
            for key in ("address", "control", "status", "message")
        )
        + "</tr>"
        for row in report["findings"]
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'; frame-src \'none\'"><title>Infrastructure Policy Lab</title></head><body><main><h1>Infrastructure Policy Lab</h1><p>Created by <a href="https://github.com/JasonStys" rel="noreferrer">Jason Stys</a> · <a href="https://www.linkedin.com/in/jason-stys-31b30b351/" rel="noreferrer">Contact</a></p><p>Offline selected-control evidence, not deployment authorization.</p><p>'
        + html.escape(canonical(report["counts"]))
        + "</p><table><caption>Plan findings</caption><thead><tr><th>Resource</th><th>Control</th><th>Status</th><th>Review guidance</th></tr></thead><tbody>"
        + rows
        + "</tbody></table></main></body></html>\n"
    )


def export(report: dict[str, Any], directory: Path) -> None:
    """Write a new private evidence directory, preserving prior outputs and partial failures for review."""
    new_directory(directory)
    (directory / "report.json").write_text(canonical(report) + "\n", encoding="utf-8")
    (directory / "report.html").write_text(render(report), encoding="utf-8")
