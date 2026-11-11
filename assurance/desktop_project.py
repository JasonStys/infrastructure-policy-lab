"""Native selected-control, plan-comparison, exact-cost and digest-bound resource-review workflows. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 86
# variable: PRODUCT — line 87
# variable: PROFILE — line 87
# variable: TITLE — line 88
# variable: VERSION — line 88
# variable: COLUMNS — line 89
# variable: RESOURCES — line 90
# variable: name — line 92
# variable: MODES — line 94
# variable: REVIEW_MODE — line 102
# variable: CHOICES — line 103
# variable: ACTIVE_FIELDS — line 104
# variable: FIELDS — line 112
# variable: SCENARIOS — line 122
# variable: HELP — line 130
# definition: scenario — line 133
# parameter: name — line 133
# variable: value — line 137
# definition: text_bundle — line 161
# parameter: title — line 161
# parameter: value — line 161
# variable: raw — line 163
# variable: page — line 164
# definition: selected_receipt — line 176
# parameter: parameters — line 176
# parameter: state — line 176
# variable: identity — line 178
# variable: original_files — line 181
# variable: original — line 184
# variable: selected — line 185
# variable: plan — line 192
# variable: current — line 193
# variable: decisions — line 199
# variable: entry — line 200
# variable: files — line 201
# variable: prior — line 203
# variable: decisions — line 208
# variable: decisions — line 210
# variable: row — line 210
# definition: analyze — line 223
# parameter: parameters — line 224
# parameter: stage — line 224
# parameter: state — line 224
# variable: mode — line 227
# variable: output — line 227
# variable: result — line 229
# variable: result — line 238
# variable: plan — line 240
# variable: result — line 242
# variable: result — line 245
# variable: result — line 252
# variable: result — line 254
# variable: counts — line 257
# variable: summary — line 258
# variable: summary — line 260
# variable: summary — line 262
# variable: path — line 266
# definition: views — line 270
# parameter: files — line 270
# variable: result — line 273
# variable: row — line 278
# variable: result — line 283
# variable: address — line 290
# definition: cells — line 296
# parameter: row — line 296
# END CODE MAP

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any

from . import review
from .cost import estimate
from .desktop_io import Rejected, canonical, json_value, read_bytes
from .desktop_state import Workspace
from .io import read
from .plan import load
from .policy import assess, compare
from .report import export

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "infrastructure-policy-lab", "InfrastructurePolicyLab"
TITLE, VERSION = "Infrastructure Policy Workbench", "1.1.0"
COLUMNS = ("Resource / item", "Control / change", "Evidence / review reason", "State / amount")
RESOURCES = tuple(
    f"examples/{name}.json"
    for name in ("healthy", "insecure", "unknown", "destructive", "drifted", "unsupported", "cost")
) + ("notices.txt", "app.ico", "python314.dll")
MODES = (
    "Assess proposed plan",
    "Compare plan assessments",
    "Calculate supplied cost scenario",
    "Build resource change worklist",
    "Review selected resource",
    "Validate external review receipt",
)
REVIEW_MODE = MODES[4]
CHOICES = {"decision": ("acknowledged", "defer", "reject")}
ACTIVE_FIELDS = {
    MODES[0]: ("plan",),
    MODES[1]: ("plan", "before"),
    MODES[2]: ("scenario",),
    MODES[3]: ("plan",),
    MODES[4]: ("plan", "reviewer", "ticket", "decision", "reason"),
    MODES[5]: ("plan", "receipt"),
}
FIELDS = (
    ("plan", "Authorized Terraform JSON plan (offline only)", "file"),
    ("before", "Earlier Terraform JSON plan (comparison only)", "file"),
    ("scenario", "Supplied rates and quantities (cost JSON)", "file"),
    ("reviewer", "Reviewer reference (asserted, not authenticated)", "text"),
    ("ticket", "Change ticket reference", "text"),
    ("decision", "Resource review decision", "choice"),
    ("reason", "Specific resource review reason", "text"),
    ("receipt", "External digest-bound decisions JSON", "file"),
)
SCENARIOS = (
    "Fictional secure proposed resource worklist",
    "Fictional exposed network/storage",
    "Fictional plan assessment comparison",
    "Fictional destructive changes",
    "Illustrative supplied-rate monthly cost",
    "Fictional unresolved evidence",
)
HELP = "Choose an authorized exported Terraform JSON plan. This app never invokes Terraform, OPA, a shell, cloud APIs, apply or destroy. It analyzes only the original selected authored controls; UNKNOWN, REVIEW, FAIL and unsupported resources never become PASS by acknowledgement. Select an actual resource worklist row before recording its reasoned reviewer/ticket assertion; receipts are bound to the exact semantic plan and worklist, retain prior decisions, and cannot authorize deployment. Changed plans and stale receipts are refused. Cost uses explicit supplied decimal rates and exclusions, not live AWS prices or budget enforcement. No raw Terraform values are retained in exported findings. Prepared fictional files use the same controls and core. History/exports are plaintext OS-owner evidence, not multiuser identity or a security certification."


def scenario(name: str) -> dict[str, str]:
    """Prepare optional genuine project fixtures without running a plan, deployment or automatic review."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared scenario")
    value = {
        "mode": MODES[3],
        "plan": str(ROOT / "examples/healthy.json"),
        "before": str(ROOT / "examples/healthy.json"),
        "scenario": str(ROOT / "examples/cost.json"),
        "reviewer": "",
        "ticket": "",
        "decision": "acknowledged",
        "reason": "",
        "receipt": "",
    }
    if name == SCENARIOS[1]:
        value.update(mode=MODES[0], plan=str(ROOT / "examples/insecure.json"))
    elif name == SCENARIOS[2]:
        value.update(mode=MODES[1], plan=str(ROOT / "examples/insecure.json"))
    elif name == SCENARIOS[3]:
        value["plan"] = str(ROOT / "examples/destructive.json")
    elif name == SCENARIOS[4]:
        value["mode"] = MODES[2]
    elif name == SCENARIOS[5]:
        value.update(mode=MODES[0], plan=str(ROOT / "examples/unknown.json"))
    return value


def text_bundle(value: dict[str, Any], title: str) -> dict[str, bytes]:
    """Render comparison/cost metadata literally, with no raw plan input or executable HTML/URLs."""
    raw = canonical(value)
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;"><title>'
        + html.escape(title)
        + "</title><main><h1>"
        + html.escape(title)
        + "</h1><p>Created by Jason Stys. Offline metadata; no deployment authorization or live price claim.</p><pre>"
        + html.escape(raw.decode())
        + "</pre></main></html>"
    )
    return {"result.json": raw, "result.html": page.encode()}


def selected_receipt(state: Workspace, parameters: dict[str, str]) -> dict[str, Any]:
    """Bind a selected actual worklist row and cumulative decisions to a freshly checked current semantic plan."""
    identity = parameters.get("_run", "")
    if not identity.isdecimal() or len(identity) > 16 or int(identity) <= 0:
        raise Rejected("select a saved resource worklist before review")
    original_files = state.files(int(identity))
    if "review.json" not in original_files:
        raise Rejected("selected analysis is not a resource worklist")
    original = json_value(original_files["review.json"])
    selected = json_value(parameters.get("_row", "null").encode())
    if (
        not isinstance(selected, dict)
        or selected not in original["worklist"]
        or not selected["review_required"]
    ):
        raise Rejected("select an actual required resource from the saved worklist")
    plan = load(read(Path(parameters["plan"])))
    current = review.worklist(plan)
    if (
        current["plan_digest"] != original["plan_digest"]
        or current["worklist_digest"] != original["worklist_digest"]
    ):
        raise Rejected("selected worklist is stale for this plan")
    decisions = []
    for entry in state.history():
        files = state.files(entry["id"])
        if "review.json" in files:
            prior = json_value(files["review.json"])
            if (
                prior.get("kind") == "asserted_change_review_receipt"
                and prior.get("worklist_digest") == current["worklist_digest"]
            ):
                decisions = list(prior["decisions"])
                break
    decisions = [row for row in decisions if row["address"] != selected["address"]]
    decisions.append(
        {
            "address": selected["address"],
            "decision": parameters["decision"],
            "reviewer": parameters["reviewer"],
            "ticket": parameters["ticket"],
            "reason": parameters["reason"],
        }
    )
    return review.receipt(plan, {**review.template(current), "decisions": decisions})


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Call only the existing offline core and immutable exporters; no tool bootstrap, shell or cloud route exists."""
    mode, output = parameters["mode"], stage / "bundle"
    if mode == MODES[2]:
        result = estimate(read(Path(parameters["scenario"])))
        return (
            mode,
            f"USD {result['total_usd']} illustrative estimate; {len(result['exclusions'])} explicit exclusions",
            text_bundle(result, "Supplied-rate cost scenario"),
        )
    if mode not in MODES:
        raise Rejected("unsupported native operation")
    if mode == MODES[4]:
        result = selected_receipt(state, parameters)
    else:
        plan = load(read(Path(parameters["plan"])))
        if mode == MODES[0]:
            result = assess(plan)
            export(result, output)
        elif mode == MODES[1]:
            result = compare(assess(load(read(Path(parameters["before"])))), assess(plan))
            return (
                mode,
                f"{len(result['changes'])} selected-control changes; not live inventory drift",
                text_bundle(result, "Plan assessment comparison"),
            )
        elif mode == MODES[3]:
            result = review.worklist(plan)
        else:
            result = review.receipt(plan, read(Path(parameters["receipt"])))
    if mode in (MODES[3], MODES[4], MODES[5]):
        review.export(result, output)
    counts = result["counts"]
    summary = f"Selected-control gate {'allowed' if result['allowed'] else 'BLOCKED'}; {counts['PASS']} PASS / {counts['FAIL']} FAIL / {counts['UNKNOWN']} UNKNOWN / {counts['REVIEW']} REVIEW"
    if "required_addresses" in result:
        summary += f"; {len(result['required_addresses'])} resources require review"
    if "decisions" in result:
        summary += f"; {len(result['decisions'])} asserted decisions; {len(result['unreviewed_addresses'])} unreviewed; no deployment authorization"
    return (
        mode,
        summary,
        {path.name: read_bytes(path, 32 * 1024 * 1024) for path in output.iterdir()},
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Separate actual policy findings, required changes, asserted decisions and exact supplied decimal costs."""
    if "result.json" in files:
        result = json_value(files["result.json"])
        if "items" in result:
            return {
                "Supplied cost items (not a bill)": result["items"],
                "Explicit cost exclusions": [
                    {"message": row, "status": "EXCLUDED"} for row in result["exclusions"]
                ],
            }
        return {"Plan assessment changes": result["changes"]}
    if "review.json" in files:
        result = json_value(files["review.json"])
        return {
            "Resource change worklist": result["worklist"],
            "Selected-control findings": result["findings"],
            "Asserted resource decisions": result.get("decisions", []),
            "Still-unreviewed resources": [
                {"address": address, "status": "UNREVIEWED"}
                for address in result.get("unreviewed_addresses", result["required_addresses"])
            ],
        }
    return {"Selected-control findings": json_value(files["report.json"])["findings"]}


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Show literal policy/decision/change states and exact decimal strings, without replacing a blocked gate."""
    return (
        str(row.get("address", row.get("name", "cost scope"))),
        str(row.get("control", row.get("change_kind", row.get("unit", "decision")))),
        str(
            row.get(
                "message",
                row.get("reason", ", ".join(row.get("review_reasons", [])) or "inspect detail"),
            )
        ),
        str(
            row.get(
                "status",
                row.get(
                    "decision",
                    row.get(
                        "subtotal_usd",
                        f"{row.get('before')} → {row.get('after')}"
                        if "after" in row
                        else "REVIEW"
                        if row.get("review_required")
                        else "no required change",
                    ),
                ),
            )
        ),
    )
