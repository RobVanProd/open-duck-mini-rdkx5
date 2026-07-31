#!/usr/bin/env python3
"""Preregister one import-closure-corrected Winner-v102 hosted curriculum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V102_PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "winner_v104_hosted_package_failure_attribution.json"
V6_NETWORK = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
OUTPUT = (
    ANALYSIS / "winner_v105_hosted_packaging_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V105_HOSTED_PACKAGING_CORRECTION_PREREGISTRATION_20260723.md"
)
V102_PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
ATTRIBUTION_SHA256 = (
    "6d728c78d65f913426d5e3093045c93d79d46608ea2f19a3098d50a715ace985"
)
V6_NETWORK_SHA256 = (
    "cfff280a1c592043d7e1849c68a3c99b05574814180506e6608f17877a5dbb90"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v105 preregistration: {path}"
            )

    playground = args.playground_root.resolve()
    calibrator = args.calibrator.resolve()
    v102 = json.loads(V102_PREREGISTRATION.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    failed = attribution.get("failed_run") or {}
    if (
        sha256(V102_PREREGISTRATION) != V102_PREREGISTRATION_SHA256
        or v102.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or sha256(ATTRIBUTION) != ATTRIBUTION_SHA256
        or attribution.get("status")
        != "HOLD_WINNER_V104_V102_PACKAGE_IMPORT_CLOSURE"
        or failed.get("stages_started") != 0
        or failed.get("optimizer_steps") != 0
        or failed.get("simulator_locomotion_steps") != 0
        or failed.get("formal_behavior_cells") != 0
        or failed.get("robot_or_rdk_access") != 0
        or sha256(V6_NETWORK) != V6_NETWORK_SHA256
    ):
        raise ValueError("Winner-v105 correction prerequisite changed")

    original_paths = {
        "driver": ROOT / "tools/colab_winner_v102_response_conditioned_curriculum.py",
        "v96_network": ROOT / "patches/winner_v96_response_conditioned_networks.py",
        "cpu_contract": (
            ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
        ),
        "composed_manifest": (
            playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "source_archive": ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz",
        "reference_features": (
            ANALYSIS / "ground_up_projected_reference_feature_table.npz"
        ),
        "protected_policy": (
            ROOT
            / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
            "T2_EQUAL_512000.onnx"
        ),
        "calibrator": calibrator,
    }
    original_hashes = {name: sha256(path) for name, path in original_paths.items()}
    if original_hashes != v102.get("input_hashes"):
        raise ValueError("Winner-v105 inherited training inputs changed")
    for relative, expected in v102["composed_playground_files"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"Winner-v105 composed source changed: {relative}")

    input_hashes = dict(original_hashes)
    input_hashes["v6_network"] = V6_NETWORK_SHA256
    value = {
        "schema_version": (
            "winner_v105.hosted_packaging_correction_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V105_HOSTED_PACKAGING_CORRECTION"
        ),
        "decision": (
            "AUTHORIZE_ONE_IMPORT_CLOSURE_CORRECTED_GPU_CURRICULUM_WITHOUT_RETRY"
        ),
        "user_authority": {
            "compute_units_available_reported": 679.02,
            "colab_cli_requested": True,
            "hosted_training_authorized": True,
        },
        "superseded_attempt": {
            "v102_preregistration_sha256": V102_PREREGISTRATION_SHA256,
            "v104_failure_attribution_sha256": ATTRIBUTION_SHA256,
            "stages_started": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "training_outcome_observed": False,
        },
        "correction": {
            "add_exact_archive_member": (
                "winner_v102_hosted_bundle/"
                "winner_v6_dynamic_calibration_networks.py"
            ),
            "v6_network_sha256": V6_NETWORK_SHA256,
            "add_static_local_import_closure_check": True,
            "add_hosted_import_preflight_before_driver": True,
            "reuse_exact_v102_training_driver": True,
            "reuse_exact_v102_training_preregistration": True,
            "policy_equations_changed": False,
            "calibrator_equations_changed": False,
            "training_hyperparameters_changed": False,
            "stage_schedule_changed": False,
            "export_steps_changed": False,
            "seeds_or_thresholds_changed": False,
            "reward_or_selection_changed": False,
        },
        "training": v102["training"],
        "contract": v102["contract"],
        "pass_rule": v102["pass_rule"],
        "source_checkpoint_directory_sha256": (
            v102["source_checkpoint_directory_sha256"]
        ),
        "input_hashes": input_hashes,
        "input_manifest_sha256": canonical_sha256(input_hashes),
        "composed_playground_files": v102["composed_playground_files"],
        "composed_playground_files_sha256": canonical_sha256(
            v102["composed_playground_files"]
        ),
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_l4_gpu_curriculum_authorized": True,
            "retry_or_resume": False,
            "additional_hosted_attempt_authorized": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v105 hosted packaging-correction preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "The prior L4 submission produced no training outcome. Winner-v105 changes "
        "only archive import closure: it adds the exact V6 module required by the "
        "already frozen V96 adapter and checks that import before invoking the exact "
        "Winner-v102 driver. The curriculum, equations, stages, exports, thresholds, "
        "and selection rules remain unchanged. Exactly one L4 run is authorized, "
        "without retry or resume. No behavior, deployment, Gate 5, RDK-X5, robot, "
        "torque, or motion authority is granted.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
