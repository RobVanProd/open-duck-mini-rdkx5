#!/usr/bin/env python3
"""Preregister the V119 default-off transition-match CPU smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = (
    ANALYSIS / "winner_v118_nominal_failure_attribution.json"
)
V114_VALIDATION = (
    ANALYSIS / "winner_v114_recovered_training_validation.json"
)
V117_CONTRACT = (
    ANALYSIS / "winner_v117_postguard_rate_projection_contract.json"
)
PATCH = ROOT / "patches/winner_v119_train_transition_match.patch"
COMPOSER = (
    ROOT / "tools/compose_winner_v119_train_transition_playground.py"
)
OUTPUT = ANALYSIS / "winner_v119_transition_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V119_TRANSITION_CPU_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "attribution": (
        "e22bf043da93921cbda62d7b96adf6a85db7830e091a6ac47f0e37a3ca83369f"
    ),
    "v114_validation": (
        "d822de06ce69e349403e9ef9cacdb961dbaf15157b5e5d28907b8c95cde9ddae"
    ),
    "v117_contract": (
        "9aab1d09ffcff7608fa758ea891f4b2a6c54d90b00a056a4478c503514d05beb"
    ),
    "patch": (
        "2cafd2280f5233c50bcad94d1c2d4d5f76065ca1e4f8bb657de4fdb7e597f94f"
    ),
    "composer": (
        "c3deb4f14a7835ff14d746e77c148c634084ef8f64952d3c663956e7ee3844ca"
    ),
    "composed_manifest": (
        "88cdb1287461a82c6d2b79c467afd6c78fb232c0355e28e9bfc7291b8053917b"
    ),
    "source_checkpoint": (
        "3a31304fc673a4ec24cf7a2f099a51a9e120031787179afc973553f6dff92c26"
    ),
    "source_onnx": (
        "2915d664b3f66d03df30b2ad0c674b0f1b1ddeffb0f829bab669ec47442c4e8c"
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
            raise FileExistsError(f"refusing to overwrite V119: {path}")

    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    source_onnx = args.source_onnx.resolve()
    manifest = playground / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    validation = json.loads(
        V114_VALIDATION.read_text(encoding="utf-8")
    )
    v117_contract = json.loads(
        V117_CONTRACT.read_text(encoding="utf-8")
    )
    hashes = {
        "attribution": sha256(ATTRIBUTION),
        "v114_validation": sha256(V114_VALIDATION),
        "v117_contract": sha256(V117_CONTRACT),
        "patch": sha256(PATCH),
        "composer": sha256(COMPOSER),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source_checkpoint),
        "source_onnx": sha256(source_onnx),
    }
    source_checkpoint_row = next(
        row
        for row in validation["checkpoints"]
        if row["step"] == 2_007_040
    )
    projection = v117_contract["projection"]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "attribution_selects_v119_cpu_contract": (
            attribution.get("status")
            == "PASS_WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION"
            and attribution.get("decision")
            == "PREREGISTER_V119_DEFAULT_OFF_AND_CPU_TRANSITION_CONTRACT"
            and attribution.get("authority", {}).get(
                "v119_cpu_contract_preregistration_authorized"
            )
            is True
            and attribution.get("authority", {}).get(
                "training_authorized"
            )
            is False
        ),
        "v114_validation_exact": (
            validation.get("status")
            == "PASS_WINNER_V114_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "source_is_exact_v114_final": (
            source_checkpoint_row["directory_sha256"]
            == hashes["source_checkpoint"]
            and hashes["source_onnx"] == EXPECTED["source_onnx"]
        ),
        "v117_projection_exact": (
            v117_contract.get("status")
            == "PASS_WINNER_V117_POSTGUARD_RATE_PROJECTION_CONTRACT"
            and projection["g3_margin_rad"] == 0.165
            and projection["candidate_vectors"] == 1
        ),
        "default_off_patch_only": True,
        "single_cpu_smoke_only": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v119.transition_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V119_TRANSITION_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V119_TRANSITION_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "source": {
            "checkpoint_path": str(source_checkpoint),
            "checkpoint_directory_sha256": hashes["source_checkpoint"],
            "raw_onnx_path": str(source_onnx),
            "raw_onnx_sha256": hashes["source_onnx"],
            "step": 2_007_040,
            "selection": (
                "V114 final is a continuation source because its V117 "
                "postexport form passes all eight nominal cells; it is not "
                "a deployment checkpoint until persistence and robustness"
            ),
        },
        "transition": {
            "default_enabled": False,
            "rate_limits_rad_s": projection[
                "selected_rate_limit_rad_s"
            ],
            "selected_normalized_action_delta": projection[
                "selected_normalized_action_delta"
            ],
            "actual_centered_guard_margin_rad": 0.165,
            "pitch_chain_action_indices": projection[
                "pitch_chain_action_indices"
            ],
            "order": [
                "existing sent-target rate projection",
                "G3 actual-position-centered pitch guard",
                "final V117 rate projection",
                "measured delay/tau actuator bridge",
            ],
            "applied_target_observation": True,
            "x0_deadband_training_support": False,
            "x0_deadband_postexport": True,
        },
        "objectives": {
            "linear_peak_torque_scale": -307.48131091308585,
            "linear_peak_torque_threshold_nm": 1.91229675,
            "tracking_tail_scale": -6572.254964031055,
            "tracking_tail_threshold_rad": 0.20,
            "new_reward_term": False,
            "reward_selection": False,
        },
        "cpu_smoke": {
            "seed": 100,
            "timesteps": 1024,
            "num_envs": 4,
            "episode_length": 64,
            "unroll_length": 8,
            "required_exports": [0, 1024],
            "required_checks": [
                "default-off transition is bit exact",
                "enabled hierarchy matches its analytic definition",
                "V117 rate vector and 0.165 guard are exact",
                "exact V114-final restore at step zero",
                "all policy leaves update and all values remain finite",
                "postexport stateful ONNX chain feeds back final bounded action",
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
            "reward_curve_selection": False,
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
        "# Winner-v119 transition CPU preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "The patch is default-off. Enabled, it places the frozen G3 guard "
        "and V117 final rate vector in the training transition before the "
        "already measured actuator bridge. The CPU smoke must restore V114 "
        "final exactly, update all actor leaves, and export the exact "
        "stateful deployment hierarchy. No hosted training is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
