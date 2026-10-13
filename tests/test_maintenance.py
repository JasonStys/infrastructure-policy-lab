"""Documentation map and offline tool archive integrity regression tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_python_map — line 43
# variable: source — line 45
# variable: generated — line 46
# variable: name — line 48
# definition: test_other_maps — line 61
# parameter: source — line 61
# parameter: suffix — line 61
# variable: generated — line 63
# definition: test_raw_tool_digest — line 68
# variable: source — line 70
# definition: test_zip_extract_only_fixed_member — line 76
# variable: stream — line 78
# variable: archive — line 79
# variable: source — line 82
# definition: test_zip_symlink — line 88
# variable: stream — line 90
# variable: archive — line 91
# variable: member — line 92
# variable: source — line 95
# definition: test_mock_only_operations — line 100
# variable: source — line 102
# variable: workflow — line 105
# definition: test_preservation_guards — line 110
# variable: source — line 112
# definition: test_provider_lock_multiple_platforms — line 117
# variable: source — line 119
# END CODE MAP

import hashlib
import io
import re
import zipfile

import pytest

from scripts.bootstrap import verified_bytes
from scripts.code_map import mapped, shell_mapped
from scripts.fixtures import ROOT


def test_python_map() -> None:
    """Self-consistent headers include every definition/parameter/assignment and remain idempotent."""
    source = '"""purpose"""\n\ndef work(value):\n    """contract"""\n    result = value\n    return result\n'
    generated = mapped(source)
    assert generated == mapped(generated)
    for name in ("work", "value", "result"):
        assert name in generated


@pytest.mark.parametrize(
    "suffix,source",
    [
        (".tf", '# purpose\nvariable "name" {\n  type = string\n}\n'),
        (".rego", "# purpose\npackage lab\nallow if { input.schema == 1 }\n"),
        (".sh", "#!/bin/bash\n# purpose\nexport PYTHONPATH=.\n"),
        (".yml", "# purpose\nname: CI\njobs:\n  check:\n    runs-on: ubuntu-latest\n"),
    ],
)
def test_other_maps(suffix: str, source: str) -> None:
    """Terraform/Rego/shell/workflow map generation is stable and preserves original executable syntax."""
    generated = shell_mapped(source, suffix)
    assert generated == shell_mapped(generated, suffix)
    assert "line" in generated


def test_raw_tool_digest() -> None:
    """No downloaded executable is used before its exact reviewed digest matches."""
    source = b"synthetic-test-only"
    assert verified_bytes(source, hashlib.sha256(source).hexdigest(), None) == source
    with pytest.raises(ValueError, match="checksum"):
        verified_bytes(source, "0" * 64, None)


def test_zip_extract_only_fixed_member() -> None:
    """Archive traversal members are never extracted; only exact approved binary bytes are returned."""
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("terraform.exe", b"safe-test")
        archive.writestr("../../escape", b"do-not-extract")
    source = stream.getvalue()
    assert (
        verified_bytes(source, hashlib.sha256(source).hexdigest(), "terraform.exe") == b"safe-test"
    )


def test_zip_symlink() -> None:
    """Even a digest-matching synthetic archive cannot provide a linked executable."""
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        member = zipfile.ZipInfo("terraform")
        member.external_attr = 0o120777 << 16
        archive.writestr(member, "elsewhere")
    source = stream.getvalue()
    with pytest.raises(ValueError, match="unsafe"):
        verified_bytes(source, hashlib.sha256(source).hexdigest(), "terraform")


def test_mock_only_operations() -> None:
    """Authored test runs remain mocked plan operations, not a live apply/destroy command."""
    source = (ROOT / "infra/tests/baseline.tftest.hcl").read_text()
    assert 'mock_provider "aws"' in source
    assert re.findall(r"command\s*=\s*(\w+)", source) == ["plan"] * 5
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    assert "upload-artifact" not in workflow and "actions/cache" not in workflow
    assert "AWS_ACCESS_KEY_ID" not in workflow and "id-token: write" not in workflow


def test_preservation_guards() -> None:
    """Source preservation guards are explicit; plan inspection alone cannot recover Terraform lifecycle policy."""
    source = (ROOT / "infra/main.tf").read_text()
    assert len(re.findall(r"prevent_destroy\s*=\s*true", source)) == 2
    assert re.search(r"force_destroy\s*=\s*false", source)


def test_provider_lock_multiple_platforms() -> None:
    """Windows/Linux need multiple unpacked hashes plus vendor archive checksums; CI stays read-only."""
    source = (ROOT / "infra/.terraform.lock.hcl").read_text()
    assert len(re.findall(r'"h1:[^"\n]+"', source)) >= 2
    assert len(re.findall(r'"zh:[a-f0-9]{64}"', source)) >= 2
    assert 'version     = "6.68.0"' in source
    assert '"-lockfile=readonly"' in (ROOT / "scripts/infra_checks.py").read_text()
