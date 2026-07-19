#!/usr/bin/env python3
"""Freeze the exact single-process winner-v3 CPU curriculum launch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUT_JSON = ANALYSIS / "winner_v3_cpu_curriculum_launch_contract.json"
OUT_MD = ANALYSIS / "WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT_20260719.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    paths = {
        "driver": ROOT / "tools/run_winner_v3_variable_configuration_cpu_curriculum.py",
        "preregistration": ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json",
        "recurrent_cpu_contract": ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json",
        "curriculum_cpu_contract": ANALYSIS / "winner_v3_variable_configuration_curriculum_contract.json",
        "source_archive": ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz",
        "reference_features": ANALYSIS / "ground_up_projected_reference_feature_table.npz",
        "composed_manifest": playground / "WINNER_V3_COMPOSED_SOURCE_MANIFEST.json",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    prereg = json.loads(paths["preregistration"].read_text())
    recurrent = json.loads(paths["recurrent_cpu_contract"].read_text())
    curriculum = json.loads(paths["curriculum_cpu_contract"].read_text())
    driver_source = paths["driver"].read_text()
    checks = {
        "preregistration_authorizes_cpu_training": prereg.get("authority", {}).get(
            "cpu_training_after_contract_pass"
        )
        is True,
        "recurrent_contract_passed": recurrent.get("status")
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT",
        "curriculum_contract_passed": curriculum.get("status")
        == "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT",
        "composed_manifest_matches_formal_contract": input_hashes["composed_manifest"]
        == curriculum.get("winner_v3_composed_manifest_sha256"),
        "single_process_driver_has_no_subprocess_surface": (
            "import subprocess" not in driver_source
            and "subprocess." not in driver_source
        ),
        "no_retry_work_root_guard_present": "single-run no-retry work root exists"
        in driver_source,
        "cpu_device_guards_present": all(
            token in driver_source
            for token in (
                'os.environ["CUDA_VISIBLE_DEVICES"] = ""',
                'os.environ["JAX_PLATFORMS"] = "cpu"',
                'all(device.platform == "cpu"',
            )
        ),
        "stage_schedule_literal_exact": all(
            token in driver_source
            for token in (
                '"steps": 245_760',
                '"steps": 2_007_040',
                '"deviation_scale": 0.25',
                '"deviation_scale": 0.5',
                '"deviation_scale": 1.0',
                '"expected_steps": [0, 1_003_520, 2_007_040]',
            )
        ),
        "formal_outcomes_zero": not (
            ANALYSIS / "winner_v3_recurrent_adapter_training_result.json"
        ).exists(),
        "behavior_cells_zero": not (
            ANALYSIS / "winner_v3_variable_configuration_result.json"
        ).exists(),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT"
        if not failed
        else "HOLD_WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v3.cpu_curriculum_launch_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": input_hashes,
        "execution": {
            "processes": 1,
            "seed": 100,
            "retry": False,
            "stages": [
                {"id": "DOMAIN_25_PERCENT", "steps": 245_760, "deviation_scale": 0.25},
                {"id": "DOMAIN_50_PERCENT", "steps": 245_760, "deviation_scale": 0.5},
                {
                    "id": "DOMAIN_100_PERCENT",
                    "steps": 2_007_040,
                    "deviation_scale": 1.0,
                    "persistent_exports_relative_steps": [1_003_520, 2_007_040],
                },
            ],
            "wall_ceiling_seconds": 43_200,
        },
        "formal_training_steps_executed": 0,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "single_cpu_curriculum_after_pass": not failed,
            "frozen_cpu_evaluation_after_valid_artifact": False,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
            "robot_clearance": False,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        f"""# Winner-v3 CPU Curriculum Launch Contract — 2026-07-19

Status: `{status}`

The exact single-process driver, formal composed simulator manifest, protected
restore archive, reference features, preregistration and both prerequisite CPU
contracts are hash-bound before training. The driver permits one seed-100 CPU
process, no retry, the frozen 25%/50%/100% schedule and only the two full-domain
persistent exports. The conservative 12-hour wall ceiling is fixed before the
run. Formal curriculum steps and behavior cells remain `0 / 0`.

- failed checks: `{failed}`

A pass authorizes only this one CPU curriculum. It is not behavior evidence or
a passing supported-configuration envelope and grants no hosted/Colab,
GPU/iGPU, RDK-X5, robot, runtime, Gate 5, deployment or clearance authority.
"""
    )
    print(status)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
