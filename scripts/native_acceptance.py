"""Exercise the same real frozen Tk controls/core on an explicit synthetic profile; no arbitrary scripts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 90
# parameter: target — line 90
# parameter: window — line 90
# variable: load — line 96
# variable: gdi — line 97
# variable: user — line 97
# variable: pointer — line 98
# variable: arguments — line 99
# variable: library — line 99
# variable: name — line 99
# variable: result — line 99
# variable: function — line 117
# variable: handle — line 120
# variable: rectangle — line 121
# variable: height — line 124
# variable: width — line 124
# variable: source — line 127
# variable: destination — line 128
# variable: bitmap — line 129
# variable: previous — line 130
# variable: pixels — line 135
# variable: header — line 136
# variable: raw — line 143
# variable: scanlines — line 144
# variable: row — line 145
# variable: column — line 147
# variable: offset — line 148
# definition: chunk — line 151
# parameter: data — line 151
# parameter: name — line 151
# definition: exercise — line 173
# parameter: output — line 173
# parameter: reopen — line 173
# parameter: window — line 173
# variable: deadline — line 176
# variable: receipt — line 177
# definition: finish — line 195
# parameter: error — line 195
# variable: data — line 202
# variable: name — line 202
# variable: row — line 204
# definition: checked — line 211
# parameter: callback — line 211
# definition: wait — line 220
# parameter: callback — line 220
# definition: worklisted — line 230
# variable: report — line 232
# variable: key — line 243
# variable: value — line 243
# definition: reviewed — line 254
# variable: report — line 256
# variable: parent — line 268
# variable: exported — line 272
# variable: path — line 273
# definition: compared — line 283
# definition: costed — line 293
# variable: report — line 295
# variable: bad — line 297
# definition: rejected — line 305
# definition: layout — line 311
# variable: original — line 313
# variable: button — line 336
# variable: name — line 336
# variable: button — line 341
# definition: begin — line 357
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from assurance import desktop_project as project
from assurance.desktop_io import json_value

if TYPE_CHECKING:
    from assurance.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [pointer, pointer, ctypes.c_uint, ctypes.c_uint, pointer, pointer, ctypes.c_uint],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    window.root.update_idletasks()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII", 40, width, -height, 1, 32, 0, width * height * 4, 0, 0, 0, 0
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the actual project widgets, real core and private state with independent domain oracles."""
    output.mkdir(mode=0o700)
    deadline = time.monotonic() + 55
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        **window.identity,
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
    }

    (output / "acceptance.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    receipt["tcl_version"] = window.root.tk.call("info", "patchlevel")
    receipt["tk_version"] = window.root.tk.call("package", "require", "Tk")

    def finish(error: bool = False) -> None:
        """Record only synthetic aggregate/hash evidence and request the ordinary graceful exit."""
        receipt["passed"] = not error
        window.acceptance_result = not error
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(data).hexdigest()
                for name, data in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        window.exit()

    def checked(callback: Any) -> None:
        """A failed oracle remains a failed receipt; original data is not replaced by a sample or reset."""
        try:
            callback()
        except Exception:
            receipt["failure"] = "native acceptance assertion or operation failed"
            receipt["failure_stage"] = callback.__name__
            finish(True)

    def wait(callback: Any) -> None:
        """Wait for this owned real operation without retries, collector access or forced shutdown."""
        if time.monotonic() > deadline:
            receipt["failure"] = "owned operation deadline exceeded"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def worklisted() -> None:
        """A destructive resource remains blocked before any asserted human review."""
        report = json_value(window.state.files(1)["review.json"])
        assert report["allowed"] is False and len(report["required_addresses"]) == 10
        window.search.set("aws_vpc.sample")
        assert len(window.table.get_children()) == 1
        window.table.selection_set("0")
        window.inspect()
        assert window.visible[0]["change_kind"] == "replace-delete-first"
        capture(window, output / "destructive-change-review.png")
        assert window.review_button is not None
        window.review_button.invoke()
        assert window.mode.get() == project.REVIEW_MODE and not window.authorized.get()
        for key, value in {
            "reviewer": "fictional-training-reviewer",
            "ticket": "LAB-101",
            "decision": "acknowledged",
            "reason": "Reviewed fictional deletion dependency and recovery requirements; no deployment authorized.",
        }.items():
            window.values[key].set(value)
        window.authorized.set(True)
        window.run_button.invoke()
        wait(reviewed)

    def reviewed() -> None:
        """A reasoned assertion is retained against the exact worklist but cannot approve its blocked policy."""
        report = json_value(window.state.files(2)["review.json"])
        assert report["allowed"] is False and len(report["decisions"]) == 1
        assert len(report["unreviewed_addresses"]) == 9 and not report["all_required_acknowledged"]
        window.view.set("Asserted resource decisions")
        window.search.set("")
        window.render()
        window.table.selection_set("0")
        window.inspect()
        layout()
        capture(window, output / "reasoned-resource-receipt.png")
        from unittest.mock import patch

        parent = output / "private-export"
        parent.mkdir()
        with patch("tkinter.filedialog.askdirectory", return_value=str(parent)):
            window.export_button.invoke()
        exported = next(parent.iterdir())
        assert {path.name: path.read_bytes() for path in exported.iterdir()} == window.state.files(
            2
        )
        receipt["steps"].append("real-digest-bound-resource-review-cannot-override-blocked-policy")
        window.prepared.set(project.SCENARIOS[2])
        window.load_prepared()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(compared)

    def compared() -> None:
        """Original independently labeled healthy/insecure plans differ at exactly two selected controls."""
        assert len(json_value(window.state.files(3)["result.json"])["changes"]) == 2
        receipt["steps"].append("real-plan-assessment-comparison")
        window.prepared.set(project.SCENARIOS[4])
        window.load_prepared()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(costed)

    def costed() -> None:
        """Supplied decimal rates produce the documented illustrative total, never a cloud bill."""
        report = json_value(window.state.files(4)["result.json"])
        assert report["total_usd"] == "1.55" and len(report["exclusions"]) >= 1
        bad = output / "invalid-receipt.json"
        bad.write_text('{"schema":1}', encoding="utf-8")
        window.mode.set(project.MODES[5])
        window.values["receipt"].set(str(bad))
        window.authorized.set(True)
        window.run_button.invoke()
        wait(rejected)

    def rejected() -> None:
        """Incomplete external receipts are refused without guessing bindings or replacing saved evidence."""
        assert len(window.state.history()) == 4 and "rejected" in window.status.get().lower()
        receipt["steps"].append("real-decimal-cost-and-malformed-receipt-retention")
        finish()

    def layout() -> None:
        """Real minimum-width layout keeps every lifecycle control fully visible even with long status text."""
        original = window.status.get()
        window.root.geometry("980x700")
        window.status.set(
            original
            + " Synthetic long-message layout check: existing evidence remains available and Exit waits for the owned operation."
        )
        window.root.update()
        receipt["layout"] = {
            "root": [window.root.winfo_width(), window.root.winfo_height()],
            "status": [
                window.status_label.winfo_width(),
                window.status_label.winfo_height(),
                window.status_label.winfo_reqheight(),
                int(window.status_label.cget("wraplength")),
            ],
            "buttons": {
                name: [
                    button.winfo_width(),
                    button.winfo_reqwidth(),
                    button.winfo_rootx() - window.root.winfo_rootx(),
                    button.winfo_rooty() - window.root.winfo_rooty(),
                    button.winfo_height(),
                ]
                for name, button in window.footer_buttons.items()
            },
        }
        assert int(window.status_label.cget("wraplength")) <= window.status_label.winfo_width()
        assert window.status_label.winfo_height() >= window.status_label.winfo_reqheight()
        for button in window.footer_buttons.values():
            assert button.winfo_width() >= button.winfo_reqwidth()
            assert button.winfo_rootx() >= window.root.winfo_rootx()
            assert (
                button.winfo_rootx() + button.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                button.winfo_rooty() + button.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        window.status.set(original)
        window.root.geometry("1260x860")
        window.root.update()
        receipt["steps"].append("real-minimum-width-long-status-all-lifecycle-controls-visible")

    def begin() -> None:
        """Use actual widgets/mainloop and persisted results, with no Terraform, OPA or cloud invocation."""
        if reopen:
            assert len(window.state.history()) == 4
            window.history_table.selection_set("2")
            window.open_button.invoke()
            assert len(window.current["Asserted resource decisions"]) == 1
            window.history_table.selection_set("4")
            window.open_button.invoke()
            assert len(window.current["Supplied cost items (not a bill)"]) > 0
            receipt["steps"].append("actual-process-reopen-four-exact-bundles")
            finish()
            return
        assert window.state.history() == []
        window.prepared.set(project.SCENARIOS[3])
        window.load_prepared()
        window.run_button.invoke()
        assert not window.busy and window.state.history() == []
        window.authorized.set(True)
        window.run_button.invoke()
        wait(worklisted)

    checked(begin)
