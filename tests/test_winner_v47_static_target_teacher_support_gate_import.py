from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v47_static_target_teacher_support_gate_result.py"
RESULT = ROOT / "outputs/analysis/winner_v47_static_target_teacher_support_gate_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v47_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v47-static-target-teacher-support-gate-result.json"
    assert module.RAW_RECEIPT_NAME.endswith(".sha256")


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))


def test_importer_completes_attribution_and_reporting_after_validation(
    monkeypatch, tmp_path: Path
) -> None:
    module = load()
    raw = {
        "status": "PASS_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE",
        "decision": "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY",
        "checkpoint_results": [{"label": "half"}, {"label": "final"}],
    }
    raw_bytes = (json.dumps(raw, sort_keys=True) + "\n").encode()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    receipt = f"{raw_sha}  /tmp/{module.RAW_RESULT_NAME}\n".encode()
    archive_path = tmp_path / "gate.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(module.RAW_RESULT_NAME, raw_bytes)
        archive.writestr(module.RAW_RECEIPT_NAME, receipt)
    archive_sha = hashlib.sha256(archive_path.read_bytes()).hexdigest()

    output_json = tmp_path / "result.json"
    output_md = tmp_path / "result.md"
    monkeypatch.setattr(module, "OUTPUT_JSON", output_json)
    monkeypatch.setattr(module, "OUTPUT_MD", output_md)
    monkeypatch.setattr(
        module,
        "lf_sha256",
        lambda path: hashlib.sha256(str(path).encode()).hexdigest(),
    )
    validated: list[dict[str, object]] = []
    monkeypatch.setattr(
        module,
        "validate_result",
        lambda value: validated.append(dict(value)),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(IMPORTER),
            "--artifact-zip",
            str(archive_path),
            "--run-id",
            "47",
            "--run-attempt",
            "1",
            "--run-head-sha",
            "1" * 40,
            "--artifact-id",
            "470",
            "--artifact-name",
            "winner-v47-static-target-teacher-support-gate-47",
            "--artifact-digest",
            f"sha256:{archive_sha}",
        ],
    )

    assert module.main() == 0

    imported = json.loads(output_json.read_text(encoding="utf-8"))
    attribution = imported["repository_attribution"]
    assert attribution["github_run_id"] == 47
    assert attribution["github_artifact_id"] == 470
    assert attribution["artifact_zip_sha256"] == archive_sha
    assert attribution["raw_result_sha256"] == raw_sha
    assert len(validated) == 2
    assert "repository_attribution" not in validated[0]
    assert validated[1]["repository_attribution"] == attribution
    assert "Main cells / heldout repeats: `248 / 64`" in output_md.read_text(
        encoding="utf-8"
    )
