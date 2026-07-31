#!/usr/bin/env python3
"""Preregister the physical peak-torque continuation CPU smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V110 = ANALYSIS / "winner_v110_pitch_guard_behavior_result.json"
CURRENT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
ARCHIVE = ANALYSIS / "winner_v3_recurrent_adapter_artifacts.tar.gz"
PATCH = ROOT / "patches/ground_up_peak_torque_exceedance.patch"
COMPOSER = ROOT / "tools/compose_winner_v111_peak_torque_playground.py"
OUTPUT = ANALYSIS / "winner_v111_peak_torque_cpu_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V111_PEAK_TORQUE_CPU_PREREGISTRATION_20260724.md"
EXPECTED = {
    "v110": "0386bc3834fb451d9f6470187ed8447e971ad90021748379977b59fd19174404",
    "current": "17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb",
    "archive": "bee604f002df5082bce579734be5a7983f2b31a6026b1caaa34d64b26ce48d91",
    "patch": "4f48578c5b309336e90fc13280b9d3e4a7ef6d14259cc23c8102b0c3a27e26de",
}
SOURCE_DIRECTORY_SHA256 = (
    "70d589520d4280c9e2f276d45a3f12ccc90aa25a0691b5bd462cbde464419bbd"
)
SOURCE_ONNX_SHA256 = (
    "fb725c5e8f45866c9b96e56b2429774f2e1ce73261ffb33ff534d977195544f0"
)
OBJECTIVE_SCALE = -1000.0
PEAK_TORQUE_NM = 1.91229675
WORST_OBSERVED_UNSCALED_COST = 0.006753196897202126


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(
            str(child.relative_to(path)).replace("\\", "/").encode()
        )
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--source-onnx", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite: {path}")

    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    source_onnx = args.source_onnx.resolve()
    manifest = playground / "WINNER_V111_COMPOSED_SOURCE_MANIFEST.json"
    v110 = json.loads(V110.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    composed = json.loads(manifest.read_text(encoding="utf-8"))
    gate = current["prospective_offline_candidate_gate"]
    checks = {
        "v110_exact_rejection": sha256(V110) == EXPECTED["v110"]
        and v110.get("status") == "PASS_WINNER_V110_PITCH_GUARD_BEHAVIOR"
        and v110.get("decision", {}).get("status") == "REJECT_G3_REPAIR",
        "current_contract_exact": sha256(CURRENT) == EXPECTED["current"]
        and gate["per_joint_peak_torque_nm_max"] == PEAK_TORQUE_NM,
        "source_archive_exact": sha256(ARCHIVE) == EXPECTED["archive"],
        "objective_patch_exact": sha256(PATCH) == EXPECTED["patch"],
        "composed_manifest_exact": composed.get("schema_version")
        == "winner_v111.peak_torque_composed_source.v1"
        and composed["peak_torque_patch"]["sha256"] == EXPECTED["patch"],
        "source_checkpoint_exact": sha256_directory(source_checkpoint)
        == SOURCE_DIRECTORY_SHA256,
        "source_onnx_exact": sha256(source_onnx) == SOURCE_ONNX_SHA256,
        "single_scale_derived_before_training": OBJECTIVE_SCALE == -1000.0
        and abs(
            OBJECTIVE_SCALE * WORST_OBSERVED_UNSCALED_COST
            - (-6.753196897202126)
        )
        <= 1.0e-12,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v111.peak_torque_cpu_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "source": {
            "checkpoint_path": str(source_checkpoint),
            "checkpoint_directory_sha256": sha256_directory(
                source_checkpoint
            ),
            "raw_onnx_path": str(source_onnx),
            "raw_onnx_sha256": sha256(source_onnx),
            "selection": (
                "latest full-domain recurrent checkpoint; both source "
                "checkpoints preserve nominal behavior, and the final has "
                "lower worst tracking p95 under Winner-v109"
            ),
        },
        "objective": {
            "name": "peak_torque_exceedance",
            "formula": (
                "mean_j(max(abs(actuator_force_nm[j]) - "
                "1.91229675, 0)^2)"
            ),
            "threshold_nm": PEAK_TORQUE_NM,
            "scale": OBJECTIVE_SCALE,
            "default_off_scale": 0.0,
            "observed_worst_unscaled_cost": (
                WORST_OBSERVED_UNSCALED_COST
            ),
            "observed_worst_scaled_cost": (
                OBJECTIVE_SCALE * WORST_OBSERVED_UNSCALED_COST
            ),
            "scale_derivation": (
                "At the worst frozen G3 tick the weighted cost is -6.753, "
                "33.77% of the +20 alive term before the common 0.02 dt. "
                "It is strong at the sparse failure boundary while the worst "
                "600-tick mean weighted cost is only -0.0416."
            ),
            "all_joint": True,
            "no_current_p95_objective": True,
        },
        "cpu_smoke": {
            "timesteps": 1024,
            "seed": 100,
            "num_envs": 4,
            "episode_length": 64,
            "unroll_length": 8,
            "required_exports": [0, 1024],
            "required_checks": [
                "source restore and step-zero parameter equality",
                "default-off reward and transition equality",
                "analytic hinge equality and threshold boundary",
                "all metrics and parameters finite",
                "all actor leaves update",
                "stateful ONNX ABI and 256-tick CPU chain",
            ],
        },
        "hosted_if_cpu_passes": {
            "one_continuation_only": True,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "full_variable_configuration": True,
            "post_export_transform": (
                "apply the exact G3 guard and deadband transform before "
                "behavior evaluation"
            ),
            "selection_requires_both_postupdate_checkpoints": True,
        },
        "input_hashes": {
            **EXPECTED,
            "composer": sha256(COMPOSER),
            "composed_manifest": sha256(manifest),
        },
        "authority": {
            "cpu_smoke_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v111 peak-torque CPU preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "This freezes one default-off, all-joint squared hinge above the "
        "manufacturer 1.91229675-N.m peak-torque limit. Its sole scale is "
        "-1000, selected analytically before training. Only a 1,024-step CPU "
        "restore/update/export smoke is authorized. Hosted compute, behavior "
        "selection, Gate 5, robot use, torque, and motion remain blocked.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"output_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
