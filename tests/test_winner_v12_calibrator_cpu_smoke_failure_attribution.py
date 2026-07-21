from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_failure_attribution.json"
)


def canonical_lf_sha256(value: bytes) -> str:
    return hashlib.sha256(value.replace(b"\r\n", b"\n")).hexdigest()


def git_bytes(commit: str, relative: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)


def test_failure_attribution_closes_exact_smoke_without_training_authority() -> None:
    evidence = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert evidence["status"] == "HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE_NO_RESULT"
    assert evidence["decision"] == (
        "STOP_EXACT_SMOKE_AND_PREREGISTER_READ_ONLY_ARTIFACT_RECOVERY_IF_PURSUED"
    )
    assert evidence["execution"]["smoke_optimizer_updates"] == {
        "stage1": 1,
        "stage2": 1,
    }
    assert evidence["execution"]["raw_result_written"] is False
    assert evidence["checkpoint_readback"] == {
        "all_40_arrays_finite": True,
        "array_count": 40,
        "stage1_adam_count": 1,
        "stage2_adam_count": 1,
    }
    assert evidence["recovery_boundary"] == {
        "allowed_next_work": (
            "a separately frozen read-only verifier may inspect the recovered "
            "checkpoint/ONNX and deterministically reconstruct evidence without "
            "creating or selecting a new checkpoint"
        ),
        "new_optimizer_updates": 0,
        "rerun_same_smoke": False,
        "training_authorized": False,
    }
    assert not any(evidence["authority"].values())


def test_failure_run_sources_reproduce_from_exact_commit() -> None:
    evidence = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    commit = evidence["github"]["commit"]
    assert commit == "0340ee946a8783434c919fea614b88f199b38a3b"
    for relative, expected in evidence["frozen_run_sources"].items():
        assert expected["hash_mode"] == "lf"
        assert canonical_lf_sha256(git_bytes(commit, relative)) == expected["sha256"]


def test_failure_is_exact_missing_dt_signature_after_artifact_creation() -> None:
    evidence = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    source = git_bytes(
        evidence["github"]["commit"],
        "tools/run_winner_v12_calibrator_cpu_smoke.py",
    ).decode()
    assert "p30_plant.step(target) - p31_plant.step(target)" in source
    main_source = source[source.index("def main() -> int:") :]
    assert main_source.index("graph = onnx_contract(") < main_source.index(
        "fixed_observer_canary = observer_plant_canary("
    )
    assert main_source.index(
        "restored_parameters, checkpoint = save_restore_checkpoint("
    ) < main_source.index("fixed_observer_canary = observer_plant_canary(")
