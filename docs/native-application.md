# Infrastructure Policy Workbench native application

Created by Jason Stys · [GitHub](https://github.com/JasonStys) · [Contact](https://www.linkedin.com/in/jason-stys-31b30b351/)

The Windows x64 portable `InfrastructurePolicyLab.exe` bundles the actual project core, SQLite history, Python 3.14.10/Tk 9 runtime, authored examples and runtime notices. End users launch one file, with no separately installed Python, Node, Docker, account or setup commands. This is a portable application, not an MSI/NSIS installer. Publishing and creating its individual desktop shortcut are separate reviewed steps; this source change does not install anything or reset user data.

## Actual project workflows

**Assess proposed plan** and **Compare plan assessments** use the original selected-control engine against explicitly chosen Terraform JSON exports. Unknown, sensitive/unresolved, destructive and unsupported evidence retain their original policy states. This application does not invoke Terraform/OPA, a shell, AWS or any apply/destroy operation. The separate provider-mocked Terraform/OPA source and CI workflows remain unchanged.

**Build resource change worklist** creates actual create/update/delete/replace/read/no-op work and an empty external decision template. Select a required resource row and choose **Review selected resource**. Enter an asserted reviewer reference, ticket, decision and a specific reason, then acknowledge permission and run. Each new receipt retains prior decisions for that exact semantic plan/worklist while preserving earlier saved bundles. Re-reviewing one resource replaces only its latest assertion in the new receipt. A stale plan, wrong row, missing justification or invalid decision is refused. Acknowledgement never changes the original allowed/blocked policy gate or authorizes deployment. **Validate external review receipt** applies the same original digest/schema checks to a chosen decisions JSON file. Deleting the most recent retained receipt can remove the basis for a later cumulative review; export needed evidence first.

**Calculate supplied cost scenario** multiplies the user's decimal quantities/rates exactly and shows explicit exclusions. This is not current AWS pricing, a full bill or budget enforcement. Fictional secure/insecure/replacement/unknown plans and the documented $1.55 scenario are optional ordinary inputs within this same application. No raw Terraform values are copied into the metadata-only findings or receipts; resource addresses and reviewer assertions can still be sensitive.

## Inspect, retain, export and exit

Results are actual core outputs, not simulated UI rows. Select an evidence view, use a literal search across the full record and select a row to inspect its complete JSON. The visible table caps 5,000 rows; exact complete bundles remain exportable. No input is interpreted as a command, plugin or Python expression. Unsupported or malformed input is rejected without substituting a prepared sample or clearing prior results.

The **Saved analyses** tab reopens verified original bytes without recalculating old evidence against today's inputs. **Export selected analysis bundle** creates a new private directory and refuses overwrite. **Remove selected local copy** requires confirmation and the selected exact hash manifest; it removes only that retained database copy, leaving input/export files unchanged. Run identities are not reused. **Help**, **Licenses** and **Exit application** remain available. Native close/Exit waits for the captured background operation and SQLite transaction; closing during work does not abandon the writer.

The default Windows workspace is `%LOCALAPPDATA%\JasonStys\InfrastructurePolicyLab`. It is version-independent and outside the executable/source; `--profile PATH` is an advanced explicit alternative, not required for desktop launch. Unknown nonempty profiles, linked/junction paths, install/source-contained profiles and concurrent owners are refused. The profile marker, single-owner lock and bounded `history.sqlite` contain plaintext OS-owner evidence. They do not establish multiuser identity or resist administrators/local malware.

History retains at most 20 runs, 128 MiB of payloads, 64 MiB per bundle, 32 MiB per file and eight files per bundle. Parameters/SQLite/filesystem overhead add space. Capacity failures preserve earlier evidence and require deliberate retention/export choices. Logical removal is not forensic erasure and may not shrink the database file. Back up the entire profile after a clean exit before replacing an executable. Removing the executable leaves saved data intact. Only synthetic profile restart was exercised; a populated real-user migration has not been tested.

## Build and actual package acceptance

Use a separate reviewed Windows CPython **3.14.10** SDK; no global Python/PATH/registry upgrade is needed:

```text
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
python scripts/build_native.py
python scripts/test_native_app.py
```

The official reference SDK supplies Tcl/Tk 9.0.4 using DLL zipfs. The builder reads its actual runtime notices, retains the authored/runtime/bootloader licenses, refuses older Python and binds actual bundled `python314.dll` bytes. Startup checks exact source/dirty/resource identities before opening a profile. Checksums are byte-integrity evidence, not Authenticode or publisher authentication. The source GUI remains usable on macOS/Linux with an appropriate Tk runtime; frozen acceptance here targets Windows x64, not mobile or every OS.

Acceptance drives the same real widgets/handlers/mainloop against explicit marked synthetic profiles, checks independent domain oracles, literal filters/detail, exact export, rejection and a second real process reopening identical saved bundle hashes. It captures only its owned window through PrintWindow, with no desktop fallback. Test flags cannot open normal profiles or convert a partial run into success. The child receives no Python/Node/provider environment and uses only the Windows system directory on PATH. No default user workspace or installed application is used.

See [dated native observations](reports/native-application-2026-11-10.md), the existing [testing strategy](testing.md), and [PyInstaller one-file behavior](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works). Tk work stays on the [Tk main thread](https://docs.python.org/3.14/library/tkinter.html#threading-model); analysis runs in one owned worker. Existing source CLI, cross-platform, security, coverage and project-specific external-tool gates remain mandatory.
