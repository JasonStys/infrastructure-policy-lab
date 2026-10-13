"""End-to-end command exits, report escaping/no-overwrite, cost and comparison flows. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_cli_assess — line 56
# parameter: capsys — line 56
# parameter: code — line 56
# parameter: name — line 56
# definition: test_module_subprocess — line 62
# variable: result — line 64
# definition: test_cli_cost_compare — line 76
# parameter: capsys — line 76
# definition: test_cli_errors — line 92
# parameter: capsys — line 92
# parameter: tmp_path — line 92
# variable: bad — line 94
# variable: text — line 97
# definition: test_reports — line 104
# parameter: capsys — line 104
# parameter: tmp_path — line 104
# variable: directory — line 106
# variable: report — line 108
# variable: source — line 110
# variable: before — line 113
# definition: test_html_injection — line 118
# parameter: plan — line 118
# parameter: tmp_path — line 118
# variable: report — line 120
# variable: source — line 124
# END CODE MAP

import json
import subprocess
import sys
from pathlib import Path

import pytest

from assurance.cli import main
from assurance.io import canonical, read
from assurance.plan import load
from assurance.policy import assess
from assurance.report import export, render
from scripts.fixtures import ROOT


@pytest.mark.parametrize(
    "name,code",
    [
        ("healthy", 0),
        ("insecure", 1),
        ("unknown", 1),
        ("destructive", 1),
        ("drifted", 1),
        ("unsupported", 1),
    ],
)
def test_cli_assess(name: str, code: int, capsys: pytest.CaptureFixture) -> None:
    """Exit status and JSON allowed flag agree for independently labeled public-safe scenarios."""
    assert main(["assess", str(ROOT / "examples" / f"{name}.json")]) == code
    assert json.loads(capsys.readouterr().out)["allowed"] == (code == 0)


def test_module_subprocess() -> None:
    """Actual python -m assurance executes without IDE, activation, AWS account or network."""
    result = subprocess.run(
        [sys.executable, "-m", "assurance", "assess", str(ROOT / "examples/healthy.json")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["allowed"]
    assert not result.stderr


def test_cli_cost_compare(capsys: pytest.CaptureFixture) -> None:
    """Cost and comparison expose deterministic JSON, with nonzero changed-evidence exits."""
    assert main(["cost", str(ROOT / "examples/cost.json")]) == 0
    assert json.loads(capsys.readouterr().out)["total_usd"] == "1.55"
    assert (
        main(["compare", str(ROOT / "examples/healthy.json"), str(ROOT / "examples/insecure.json")])
        == 1
    )
    assert len(json.loads(capsys.readouterr().out)["changes"]) == 2
    assert (
        main(["compare", str(ROOT / "examples/healthy.json"), str(ROOT / "examples/healthy.json")])
        == 0
    )
    assert not json.loads(capsys.readouterr().out)["changes"]


def test_cli_errors(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Errors never echo private input contents, real identifiers or local filesystem paths."""
    bad = tmp_path / "private-name.json"
    bad.write_text('{"secret":"PRIVATE-SENTINEL"}')
    assert main(["assess", str(bad)]) == 2
    text = capsys.readouterr().err
    assert "PRIVATE-SENTINEL" not in text and str(bad) not in text
    assert main(["assess", str(tmp_path / "missing")]) == 2
    bad.write_bytes(b"\xff")
    assert main(["assess", str(bad)]) == 2


def test_reports(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """New-dir HTML/JSON exports agree, remain scriptless and cannot overwrite earlier evidence."""
    directory = tmp_path / "report"
    assert main(["assess", str(ROOT / "examples/insecure.json"), "--out", str(directory)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert read(directory / "report.json") == report
    source = (directory / "report.html").read_text()
    assert "<script" not in source and "default-src 'none'" in source
    assert "Jason Stys" in source and "Plan findings" in source
    before = (directory / "report.json").read_bytes()
    assert main(["assess", str(ROOT / "examples/healthy.json"), "--out", str(directory)]) == 2
    assert (directory / "report.json").read_bytes() == before


def test_html_injection(plan: dict, tmp_path: Path) -> None:
    """Renderer independently escapes hostile finding values even if caller did not use plan token validation."""
    report = assess(load(plan))
    report["findings"][0]["message"] = (
        '<img src="https://example.invalid/tracker" onerror="alert(1)">'
    )
    source = render(report)
    assert "&lt;img" in source and "<img" not in source
    export(report, tmp_path / "safe")
    assert canonical(read(tmp_path / "safe/report.json")) == canonical(report)
