#!/usr/bin/env python3
"""Preregister the V114 linear-torque CPU mechanics smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = ANALYSIS / "winner_v113_nominal_failure_attribution.json"
V112_VALIDATION = ANALYSIS / "winner_v112_recovered_training_validation.json"
PATCH = ROOT / "patches/ground_up_linear_peak_torque_exceedance.patch"
COMPOSER = ROOT / "tools/compose_winner_v114_linear_torque_playground.py"
OUTPUT = ANALYSIS / "winner_v114_linear_torque_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V114_LINEAR_TORQUE_CPU_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "attribution": (
        "90a62c58f41178ce43a64af8a5bc8d7f51b613937395d7fe1418d6d7be8af198"
    ),
    "v112_validation": (
        "895c010a015da4dc43bec2bf3752767c7633859adef2f1b277ef7315e941d4a7"
    ),
    "patch": (
        "c0ecdefd7cc2379e9afa4e636e4d80d7e1510ef09edc07a9c55e695316508103"
    ),
    "composer": (
        "2fbf48c239e95736d499f6e050a2710e2e9323aee38f9a41501fd69dc73b262c"
    ),
    "composed_manifest": (
        "d0bcf899e9be15b1ddd678ccb35036f6d750eae6aa65e9686fba2a1cf81a5a41"
    ),
    "source_checkpoint": (
        "d63309e0e0524d684813d1bf068e8642b21d2e829653d7716949614350f0423c"
    ),
    "source_onnx": (
        "6a400a7c465e56520e853d3607265e544888f86560d065f553a765b3d259563b"
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
            raise FileExistsError(f"refusing to overwrite V114: {path}")
    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    source_onnx = args.source_onnx.resolve()
    manifest = playground / "WINNER_V114_COMPOSED_SOURCE_MANIFEST.json"
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    validation = json.loads(V112_VALIDATION.read_text(encoding="utf-8"))
    hashes = {
        "attribution": sha256(ATTRIBUTION),
        "v112_validation": sha256(V112_VALIDATION),
        "patch": sha256(PATCH),
        "composer": sha256(COMPOSER),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source_checkpoint),
        "source_onnx": sha256(source_onnx),
    }
    objective = attribution["objective_diagnosis"]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "attribution_selects_linear_cpu_contract": (
            attribution.get("status")
            == "PASS_WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION"
            and attribution.get("decision")
            == "PREREGISTER_LINEAR_TORQUE_EXCEEDANCE_CPU_CONTRACT"
            and attribution.get("authority", {}).get(
                "linear_objective_cpu_preregistration_authorized"
            )
            is True
        ),
        "v112_recovered_training_validation_exact": (
            validation.get("status")
            == "PASS_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "source_is_v112_final_checkpoint": (
            hashes["source_checkpoint"] == EXPECTED["source_checkpoint"]
            and hashes["source_onnx"] == EXPECTED["source_onnx"]
        ),
        "linear_scale_derived_before_training": (
            objective["training_scale"] == -307.48131091308585
            and objective["default_off_scale"] == 0.0
        ),
        "squared_objective_disabled_for_isolation": True,
        "single_cpu_smoke_only": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v114.linear_torque_cpu_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V114_LINEAR_TORQUE_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "source": {
            "checkpoint_path": str(source_checkpoint),
            "checkpoint_directory_sha256": hashes["source_checkpoint"],
            "raw_onnx_path": str(source_onnx),
            "raw_onnx_sha256": hashes["source_onnx"],
            "selection": (
                "V112 final is the only post-update checkpoint to pass any "
                "moving nominal cell and has the lowest hosted linear-boundary "
                "training metric; it is a continuation source, not a selected "
                "deployment checkpoint"
            ),
        },
        "objective": {
            "name": "linear_peak_torque_exceedance",
            "formula": objective["formula"],
            "threshold_nm": 1.91229675,
            "default_off_scale": 0.0,
            "training_scale": objective["training_scale"],
            "squared_peak_torque_scale": 0.0,
            "scale_derivation": objective["scale_derivation"],
            "closed_alternative": objective["closed_option"],
            "all_joint": True,
        },
        "cpu_smoke": {
            "seed": 100,
            "timesteps": 1024,
            "num_envs": 4,
            "episode_length": 64,
            "unroll_length": 8,
            "required_exports": [0, 1024],
            "required_checks": [
                "explicit CPU topology restore of the V112 GPU checkpoint",
                "step-zero parameter equality",
                "default-off reward equality",
                "analytic linear hinge equality and finite nonzero metric",
                "all actor leaves update",
                "stateful ONNX ABI and 256-tick CPU chain",
            ],
        },
        "hosted_if_cpu_passes": {
            "one_continuation_only": True,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "full_variable_configuration": True,
            "selection_requires_both_postupdate_checkpoints": True,
            "post_export_transform": (
                "apply the exact G3 guard and x=0 deadband before behavior"
            ),
            "retry": False,
            "resume": False,
        },
        "authority": {
            "cpu_smoke_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v114 linear-torque CPU preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "V113 proves the failures are sparse single-joint boundary events and "
        "that a max-squared objective would be only a scalar rewrite. V114 "
        "therefore freezes one linear-hinge mechanics smoke from the exact "
        "V112 final checkpoint. A pass authorizes only separate hosted-run "
        "preregistration; it grants no training, Gate 5, or robot authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
