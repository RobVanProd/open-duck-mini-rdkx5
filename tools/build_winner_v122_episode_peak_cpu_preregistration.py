#!/usr/bin/env python3
"""Preregister the V122 default-off episode-peak CPU mechanics smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
DIAGNOSIS = ANALYSIS / "winner_v121_peak_objective_diagnosis.json"
V119_VALIDATION = (
    ANALYSIS / "winner_v119_recovered_training_validation.json"
)
PATCH = ROOT / "patches/winner_v122_episode_peak_torque_increment.patch"
COMPOSER = ROOT / "tools/compose_winner_v122_episode_peak_playground.py"
OUTPUT = ANALYSIS / "winner_v122_episode_peak_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V122_EPISODE_PEAK_CPU_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "diagnosis": (
        "1c84a48c3f4eff354108240b4084d6546d1232cccd6bf67d715d9c1518b0e26a"
    ),
    "v119_validation": (
        "456121dc7680df6e66915fa67e59f088f718e08db1468d3523795f8dd56abb14"
    ),
    "patch": (
        "afa07528fa832b0e64e220587936b3c699ee893f026d1caa822674b3850f6c8e"
    ),
    "composer": (
        "80129cf24cb4288341f84a3e1d87666c26b0d81fd88c69f01e6759c3bf0b8859"
    ),
    "composed_manifest": (
        "5a53d713e22035151f2f5aaa1a3ee57735a90296a15fe5f3336f13178fca8918"
    ),
    "source_checkpoint": (
        "6f2d9856b5ab674f9f20f04c46be6dc00adc5eabc31826f16b4743c5172dfad8"
    ),
    "source_onnx": (
        "2d3cfb686a9c9643d9414a99a10e4db3aee7fc8f63cbc2fd81f107b487cf1311"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
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
            raise FileExistsError(f"refusing to overwrite V122: {path}")

    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    source_onnx = args.source_onnx.resolve()
    manifest = playground / "WINNER_V122_COMPOSED_SOURCE_MANIFEST.json"
    diagnosis = json.loads(DIAGNOSIS.read_text(encoding="utf-8"))
    validation = json.loads(
        V119_VALIDATION.read_text(encoding="utf-8")
    )
    hashes = {
        "diagnosis": sha256(DIAGNOSIS),
        "v119_validation": sha256(V119_VALIDATION),
        "patch": sha256(PATCH),
        "composer": sha256(COMPOSER),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source_checkpoint),
        "source_onnx": sha256(source_onnx),
    }
    source_row = next(
        row
        for row in validation["checkpoints"]
        if row["step"] == 1_003_520
    )
    source_onnx_row = next(
        row
        for row in validation["onnx"]
        if row["step"] == 1_003_520
    )
    nominal_result = json.loads(
        (
            ANALYSIS / "winner_v121_nominal_behavior_result.json"
        ).read_text(encoding="utf-8")
    )
    source_nominal = next(
        row
        for row in nominal_result["per_checkpoint"]
        if row["step"] == 1_003_520
    )
    selected = diagnosis["selected_mechanism"]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "diagnosis_selects_exact_episode_peak": (
            diagnosis.get("status")
            == "PASS_WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS"
            and diagnosis.get("decision")
            == "PREREGISTER_V122_DEFAULT_OFF_EPISODE_PEAK_CPU_CONTRACT"
            and selected.get("name")
            == "episode_global_peak_torque_increment_integral"
            and selected.get("scale_search") is False
        ),
        "v119_training_validation_exact": (
            validation.get("status")
            == "PASS_WINNER_V119_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "source_is_exact_v119_half": (
            source_row["directory_sha256"] == hashes["source_checkpoint"]
            and source_onnx_row["sha256"] == hashes["source_onnx"]
            and source_row["step"] == 1_003_520
        ),
        "source_passed_all_eight_nominal_cells": (
            source_nominal["passing_cells"] == 8
            and source_nominal["all_eight_cells_pass"] is True
        ),
        "source_is_continuation_only_not_deployment_selection": True,
        "default_off_patch_only": True,
        "one_cpu_smoke_only": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v122.episode_peak_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V122_EPISODE_PEAK_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "source": {
            "checkpoint_path": str(source_checkpoint),
            "checkpoint_directory_sha256": hashes["source_checkpoint"],
            "raw_onnx_path": str(source_onnx),
            "raw_onnx_sha256": hashes["source_onnx"],
            "step": 1_003_520,
            "selection": (
                "V119 half passed all eight V121 nominal cells and is used "
                "only as a continuation source. Both new post-update "
                "checkpoints remain mandatory; this is not checkpoint "
                "selection for deployment."
            ),
        },
        "objective": {
            "name": selected["name"],
            "threshold_nm": 1.91229675,
            "instantaneous_excess": selected["instantaneous_excess"],
            "state": selected["state"],
            "per_step_cost": selected["per_step_cost"],
            "episode_integral_identity": selected[
                "episode_integral_identity"
            ],
            "scale": selected["reuse_scale"],
            "existing_linear_peak_scale": 0.0,
            "tracking_tail_scale": -6572.254964031055,
            "default_enabled": False,
            "scale_search": False,
            "reward_curve_selection": False,
        },
        "cpu_smoke": {
            "seed": 100,
            "timesteps": 1024,
            "num_envs": 4,
            "episode_length": 64,
            "unroll_length": 8,
            "required_exports": [0, 1024],
            "required_checks": [
                "default-off protected transition outputs are exact",
                "enabled running state is monotonic and reset is zero",
                "cost integral equals analytic episode-global peak excess",
                "exact V119-half restore at step zero",
                "all 15 policy leaves update and every value is finite",
                "both deployed ONNX graphs pass the V121 stateful ABI",
            ],
        },
        "hosted_if_cpu_passes": {
            "separate_preregistration_required": True,
            "one_continuation_only": True,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "both_postupdate_checkpoints_required": True,
            "retry": False,
            "resume": False,
            "scalar_search": False,
            "reward_curve_selection": False,
        },
        "execution": {
            "training_steps": 0,
            "behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_smoke_authorized": not failed,
            "hosted_training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v122 episode-peak CPU preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "V121 failed only sparse physical peaks. V122 replaces the diluted "
        "linear mean hinge with a running-peak increment whose episode "
        "integral is exactly the frozen peak-torque gate. The patch is "
        "default-off and receives one 1,024-step CPU mechanics smoke. No "
        "Colab run or behavior evaluation is authorized here.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
