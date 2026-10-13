"""Install hash-verified official Terraform/OPA into this repo only, never globally. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 39
# definition: verified_bytes — line 42
# parameter: digest — line 42
# parameter: member — line 42
# parameter: source — line 42
# variable: archive — line 48
# variable: info — line 49
# definition: main — line 59
# variable: parser — line 61
# variable: args — line 63
# variable: operating — line 64
# variable: lock — line 69
# variable: suffix — line 70
# variable: artifact — line 71
# variable: expected_url — line 76
# variable: directory — line 83
# variable: destination — line 85
# variable: response — line 88
# variable: source — line 89
# variable: binary — line 92
# variable: descriptor — line 95
# variable: output — line 96
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verified_bytes(source: bytes, digest: str, member: str | None) -> bytes:
    """Check digest before opening an archive; extract only the exact regular fixed executable, never paths."""
    if hashlib.sha256(source).hexdigest() != digest:
        raise ValueError("official tool checksum mismatch")
    if member is None:
        return source
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        info = archive.getinfo(member)
        if (
            info.is_dir()
            or info.file_size > 300 * 1024 * 1024
            or ((info.external_attr >> 16) & 0o170000) == 0o120000
        ):
            raise ValueError("unsafe executable member")
        return archive.read(info)


def main() -> int:
    """Download pinned official binaries with size/time bounds; refuse overwrites and unsupported architectures."""
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=("terraform", "opa"))
    args = parser.parse_args()
    operating = {"Windows": "windows", "Linux": "linux"}.get(platform.system())
    if operating is None or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise ValueError(
            "bootstrap supports x64 Windows/Linux; use official vendor instructions elsewhere"
        )
    lock = json.loads((ROOT / "tools.lock.json").read_text())["tools"][f"{args.tool}-{operating}"]
    suffix = ".exe" if operating == "windows" else ""
    artifact = (
        f"terraform_{lock['version']}_{operating}_amd64.zip"
        if args.tool == "terraform"
        else f"opa_{operating}_amd64{'.exe' if operating == 'windows' else '_static'}"
    )
    expected_url = (
        f"https://releases.hashicorp.com/terraform/{lock['version']}/{artifact}"
        if args.tool == "terraform"
        else f"https://github.com/open-policy-agent/opa/releases/download/v{lock['version']}/{artifact}"
    )
    if lock["url"] != expected_url:
        raise ValueError("tool must use pinned official source")
    directory = ROOT / ".tools"
    directory.mkdir(mode=0o700, exist_ok=True)
    destination = directory / (args.tool + suffix)
    if destination.exists() or directory.is_symlink() or directory.is_junction():
        raise ValueError("tool destination must be a new owned non-linked path")
    with urllib.request.urlopen(expected_url, timeout=60) as response:
        source = response.read(256 * 1024 * 1024 + 1)
    if len(source) > 256 * 1024 * 1024:
        raise ValueError("tool download exceeds size bound")
    binary = verified_bytes(
        source, lock["sha256"], "terraform" + suffix if args.tool == "terraform" else None
    )
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700)
    with os.fdopen(descriptor, "wb") as output:
        output.write(binary)
    print(f"Verified official {args.tool} installed inside ignored .tools only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
