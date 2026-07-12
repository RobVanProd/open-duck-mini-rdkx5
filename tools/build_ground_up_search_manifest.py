#!/usr/bin/env python3
"""Build the frozen ground-up policy-search manifest without training."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "policy/BEST_WALK_ONNX_2.onnx"
REFERENCE = ROOT.parent / "Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"
BASELINE_SHA = "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067"
REFERENCE_SHA = "5850c0610ed89e2860e7047f9ee27d8412462e1199752952c3c2a0efd2cb7a25"
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_git_object(repo: Path, revision: str) -> None:
    subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="outputs/analysis/ground_up_reference_policy_search_manifest.json",
    )
    args = parser.parse_args()

    if sha256(BASELINE) != BASELINE_SHA:
        raise SystemExit("BEST_WALK_ONNX_2 hash mismatch")
    if sha256(REFERENCE) != REFERENCE_SHA:
        raise SystemExit("reference-motion hash mismatch")
    require_git_object(REFERENCE.parents[3], CONTROL_COMMIT)

    families = [
        "upstream_control",
        "residual_reference",
        "phase_residual",
        "recurrent_residual",
        "imitation_decay",
        "asymmetric_critic",
    ]
    manifest = {
        "schema_version": "ground_up_reference_policy_search.v1",
        "status": "FROZEN_AWAITING_CPU_CONTRACTS_AND_COLAB_CALIBRATION",
        "objective": "more robust than BEST_WALK_ONNX_2 under measured RDK-X5 constraints",
        "sources": {
            "baseline": {"path": str(BASELINE.relative_to(ROOT)), "sha256": BASELINE_SHA},
            "playground_control_commit": CONTROL_COMMIT,
            "reference": {"path": str(REFERENCE), "sha256": REFERENCE_SHA},
            "actuator_fit": "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
        },
        "contract": {
            "observation_shape": [1, 101],
            "action_shape": [1, 14],
            "control_hz": 50,
            "action_scale_rad": 0.25,
            "pitch_chain_indices": [2, 3, 4, 11, 12, 13],
            "pitch_chain_velocity_limits_rad_s": [1.5, 1.5, 1.75, 1.25, 1.0, 1.25],
        },
        "families": families,
        "seed_splits": {
            "development": list(range(100, 116)),
            "search_validation": list(range(200, 216)),
            "final_held_out": list(range(1000, 1032)),
        },
        "commands_x": [0.0, 0.08],
        "compute_units": {
            "hard_total": 94,
            "calibration_max": 3,
            "search_max": 35,
            "finalist_training_max": 38,
            "heldout_eval_max": 12,
            "interruption_reserve": 6,
            "consumed": 0,
        },
        "rungs": {
            "calibration": {"timesteps": None, "derived_after_steps_per_unit_measurement": True},
            "broad": {"timesteps": None, "derived_after_calibration": True},
            "medium": {"timesteps": None, "derived_after_calibration": True},
            "final": {"timesteps": None, "derived_after_calibration": True},
        },
        "hardware_authorized": False,
        "local_gpu_authorized": False,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
