#!/usr/bin/env python3
"""Freeze T55's materialization and two-stage CPU smoke contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t55_dynamic_single_support_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T55_DYNAMIC_SINGLE_SUPPORT_CPU_PREREGISTRATION_20260728.md"
)
T54 = ANALYSIS / "t54_t53_condition7_failure_attribution.json"
T52_PREREG = (
    ANALYSIS / "t52_uniform_half_head_qualification_preregistration.json"
)
T52_RESULT = ANALYSIS / "t52_uniform_half_head_qualification_result.json"
T32_VALIDATION = ANALYSIS / "t32_recovered_training_validation.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t55-v2")
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-t31-v1")
MANIFEST = COMPOSED / "T55_COMPOSED_SOURCE_MANIFEST.json"
CPU_TEMPLATE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v119-transition-cpu-smoke-20260724/"
    "smoke/2026_07_24_150649_0"
)
T32_TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t32b_extracted_20260727/"
    "t32_action_margin_trainthrough_continuation/training"
)
T32_HALF = T32_TRAINING / "2026_07_27_133205_1003520"
T32_FINAL = T32_TRAINING / "2026_07_27_133723_2007040"
MODULE = ROOT / "patches" / "t55_dynamic_single_support_curriculum.py"
PATCH = (
    ROOT
    / "patches"
    / "winner_t55_dynamic_single_support_curriculum.patch"
)
COMPOSER = ROOT / "tools" / "compose_t55_dynamic_single_support_playground.py"
RUNNER = ROOT / "tools" / "run_t55_dynamic_single_support_cpu_contract.py"
TEST = ROOT / "tests" / "test_t55_dynamic_single_support_curriculum.py"
RESULT_TEST = (
    ROOT / "tests" / "test_t55_dynamic_single_support_cpu_contract.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "directory",
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T55: {path}")
    t54 = json.loads(T54.read_text(encoding="utf-8"))
    t52_prereg = json.loads(T52_PREREG.read_text(encoding="utf-8"))
    t52_result = json.loads(T52_RESULT.read_text(encoding="utf-8"))
    t32 = json.loads(T32_VALIDATION.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    half_policy = t52_prereg["policies"][0]
    validation_checkpoints = {
        int(row["step"]): row["directory_sha256"]
        for row in t32["checkpoints"]
    }
    sources = {
        "t54_attribution": file_receipt(T54),
        "t52_preregistration": file_receipt(T52_PREREG),
        "t52_result": file_receipt(T52_RESULT),
        "t32_validation": file_receipt(T32_VALIDATION),
        "module": file_receipt(MODULE),
        "patch": file_receipt(PATCH),
        "composer": file_receipt(COMPOSER),
        "runner": file_receipt(RUNNER),
        "mechanics_test": file_receipt(TEST),
        "result_test": file_receipt(RESULT_TEST),
        "composed_manifest": file_receipt(MANIFEST),
    }
    assets = {
        "cpu_topology_template": directory_receipt(CPU_TEMPLATE),
        "t32_half_checkpoint": directory_receipt(T32_HALF),
        "t32_final_checkpoint": directory_receipt(T32_FINAL),
        "t52_half_policy": {
            "kind": "file",
            "path": half_policy["path"],
            "bytes": half_policy["bytes"],
            "sha256": half_policy["sha256"],
        },
        "reference_features": file_receipt(REFERENCE),
    }
    python_inventory = {
        path.relative_to(COMPOSED).as_posix(): sha256(path)
        for path in sorted(COMPOSED.rglob("*.py"))
    }
    checks = {
        "t54_earned_only_cpu_contract_preregistration": (
            t54["status"]
            == "PASS_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
            and t54["decision"]
            == "EARN_T55_DYNAMIC_SINGLE_SUPPORT_CURRICULUM_"
            "CPU_CONTRACT_PREREGISTRATION_ONLY"
            and t54["failed_checks"] == []
            and not t54["authority"]["hosted_training"]
        ),
        "t52_source_qualified_conditions1_through4": (
            t52_result["status"]
            == "PASS_T52_UNIFORM_HALF_HEAD_QUALIFICATION"
            and t52_result["summary"]["green_cells"] == 64
            and t52_result["summary"]["completed_cells"] == 64
        ),
        "t32_recovered_checkpoints_green": (
            t32["status"] == "PASS_T32_RECOVERED_TRAINING_VALIDATION"
            and t32["failed_checks"] == []
            and assets["t32_half_checkpoint"]["sha256"]
            == validation_checkpoints[1_003_520]
            and assets["t32_final_checkpoint"]["sha256"]
            == validation_checkpoints[2_007_040]
        ),
        "cpu_template_exact": (
            assets["cpu_topology_template"]["sha256"]
            == t32["input_hashes"]["cpu_template"]
        ),
        "t52_half_policy_exact": (
            Path(half_policy["path"]).is_file()
            and sha256(Path(half_policy["path"])) == half_policy["sha256"]
        ),
        "composed_manifest_exact": (
            manifest["schema_version"]
            == "open_duck.t55_composed_source.v1"
            and manifest["sources"]["module"]["sha256"] == sha256(MODULE)
            and manifest["sources"]["patch"]["sha256"] == sha256(PATCH)
        ),
        "all_sources_and_assets_present": all(
            Path(item["path"]).exists()
            for item in (*sources.values(), *assets.values())
        ),
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t55_dynamic_single_support_cpu_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            if not failed
            else "HOLD_T55_DYNAMIC_SINGLE_SUPPORT_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can T52-half be materialized as a trainable checkpoint and "
            "complete a bilateral balance-first then gait-transfer CPU smoke "
            "with exact default-off and deployment contracts?"
        ),
        "causal_basis": {
            "t53_condition7": "8/16 green; x=0 4/4, moving 4/12",
            "failure": (
                "eight delayed backward-pitch collapses at ticks 139-382"
            ),
            "support_onset": (
                "six left-only, two double, zero right-only at -0.25 rad"
            ),
            "negative_results": (
                "capture-point support margin and reconstructed pressure "
                "overlap passing and failing cells"
            ),
            "selected_mechanism": (
                "phase-selected bilateral single-support reward using "
                "projected gravity and gyro over the measured four-tick "
                "control horizon"
            ),
        },
        "mechanism": {
            "balance_stage": (
                "replace the clipped locomotion reward with the bilateral "
                "single-support balance reward"
            ),
            "transfer_stage": (
                "restore the complete locomotion reward and add the same "
                "single-support reward"
            ),
            "support_side": (
                "phase sine <=0 targets left; phase sine >0 targets right"
            ),
            "perfect_support_reward": (
                "20 alive-scale * 0.02 s = 0.4 per tick"
            ),
            "tilt_quality": (
                "exp(-||predicted_roll_pitch / 0.25||^2)"
            ),
            "prediction_horizon": (
                "4 ticks * 0.02 s = 0.08 s, derived from the maximum "
                "three-tick actuator delay plus the first controllable tick"
            ),
            "manual_mass_com_or_foot_measurement": False,
            "capture_point_or_pressure_objective": False,
            "policy_abi_change": False,
            "runtime_change": False,
        },
        "materialization": {
            "source": "T32 half trainable checkpoint",
            "replace_from_t32_final": [
                "1/params/residual_trunk",
                "1/params/residual_location",
            ],
            "preserve_from_t32_half": [
                "normalizer",
                "adapter core",
                "adapter output head",
                "critic",
            ],
            "required_proof": (
                "step-zero complete deployment graph byte-exact T52-half"
            ),
        },
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(COMPOSED.resolve()),
            "base_path": str(BASE.resolve()),
            "manifest_sha256": sha256(MANIFEST),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(
                python_inventory
            ),
        },
        "cpu_contract": {
            "balance_simulator_steps": 1024,
            "transfer_simulator_steps": 1024,
            "exports_per_stage": [0, 1024],
            "ppo_envs": 4,
            "required_checks": [
                "materialized deployment byte-exact T52-half",
                "T31 and T55 default-off trajectories bit-exact",
                "both left and right support metrics positive and finite",
                "both stage reward metrics positive and finite",
                "all actor and critic leaves update in each stage",
                "all trees and three final deployment graphs finite",
                "no observation/action ABI change",
            ],
        },
        "decision_rule": {
            "pass": (
                "Earn only a separately committed T56 hosted-training "
                "preregistration; do not launch compute."
            ),
            "fail": (
                "Close this exact curriculum without changing phase split, "
                "tilt gate, horizon, reward scale, or stage ordering."
            ),
            "hosted_training_earned_now": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "cpu_simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_2048_step_cpu_contract": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_matrix": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    basis["preregistered_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T55 dynamic single-support CPU preregistration",
                "",
                f"- Status: `{basis['status']}`",
                "- Materialize T52-half into a trainable checkpoint",
                "- Stage 1: 1,024 CPU balance-only steps",
                "- Stage 2: 1,024 CPU gait-transfer steps",
                "- Both left and right support required",
                "- Manual mass/COM/foot measurements: `NO`",
                "- Policy ABI/runtime changes: `0/0`",
                "- Hosted/behavior/Gate5/robot authority: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(basis["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    print(
        "preregistered_contract_sha256="
        f"{basis['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
