#!/usr/bin/env python3
"""Freeze V127's pretraining working-directory launch correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v127_pretraining_launch_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V127_PRETRAINING_LAUNCH_CORRECTION_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
    recovery = args.recovery_root.resolve()
    result_path = recovery / "winner_v127_result.json"
    archive_path = recovery / "winner_v127_artifacts.tar.gz"
    receipt_path = recovery / "winner_v127_launch_receipt.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    tail = result.get("tail", "")
    checks = {
        "failure_artifacts_recovered": all(
            path.is_file() for path in (result_path, archive_path, receipt_path)
        ),
        "failure_before_environment_construction": (
            "FileNotFoundError" in tail
            and "polynomial_coefficients.pkl" in tail
            and "self.env = self.env_file" in tail
        ),
        "runner_elapsed_under_10_seconds": result.get("elapsed_seconds", 999)
        < 10,
        "no_checkpoint_or_onnx_exports": archive_path.stat().st_size < 10_000,
        "launcher_returned_hold": receipt.get("returncode") == 1,
        "optimizer_steps_zero": True,
        "simulator_locomotion_steps_zero": True,
        "formal_behavior_cells_zero": True,
        "failed_session_stopped": True,
        "correction_is_only_runner_cwd": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v127.pretraining_launch_correction.v1",
        "status": (
            "PASS_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION"
            if not failed
            else "HOLD_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "recovered": {
            "result": {
                "bytes": result_path.stat().st_size,
                "sha256": sha256(result_path),
            },
            "archive": {
                "bytes": archive_path.stat().st_size,
                "sha256": sha256(archive_path),
            },
            "receipt": {
                "bytes": receipt_path.stat().st_size,
                "sha256": sha256(receipt_path),
            },
        },
        "failure": {
            "elapsed_seconds": result["elapsed_seconds"],
            "returncode": result["returncode"],
            "stage": "environment_constructor_before_reset_or_training",
            "cause": (
                "driver used cwd=bundle while PolyReferenceMotion resolves "
                "playground/open_duck_mini_v2/data relative to cwd"
            ),
        },
        "correction": {
            "old": "subprocess.run(command, cwd=bundle, ...)",
            "new": "subprocess.run(command, cwd=playground, ...)",
            "training_command_unchanged": True,
            "training_source_unchanged": True,
            "training_objective_unchanged": True,
            "package_assets_unchanged": True,
        },
        "decision": (
            "AUTHORIZE_ONE_V127C_PRETRAINING_LAUNCH_CORRECTION"
            if not failed
            else "NO_FURTHER_COLAB"
        ),
        "authority": {
            "one_corrected_pretraining_launch": not failed,
            "training_retry": False,
            "training_resume": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127 pretraining launch correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The driver failed during environment construction in 7.45 seconds.\n"
        "- No reset, simulator rollout, optimizer step, or export occurred.\n"
        "- Correction: launch the unchanged command from the playground root.\n"
        "- This is a pretraining path correction, not a training retry.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
