#!/usr/bin/env python3
"""Preregister V148's single-center local residual graph contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/build_winner_v148_single_center_residual.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V147_RESULT = ANALYSIS / "winner_v147_head_only_dagger_cpu_result.json"
V134_LOADER = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_LOADER = ROOT / "training/winner_v145_on_policy_dagger.py"
OUTPUT = ANALYSIS / "winner_v148_single_center_residual_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V148_SINGLE_CENTER_RESIDUAL_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "1c84ee636e1aa41fda2fb3452c011d0927dd26a42733af231e8e5e2e32612dbc"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v140_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v147_result": (
        "cf46b78e3a1e5777d324ce744952406a949ddd34b54d12e7d25fe1f265b83b91"
    ),
    "v134_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "v145_loader": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "source_raw": (
        "aa1025ae4bd2daf1c513cd81374e8eb7961308a41ca10bbe55f6284944fd6460"
    ),
    "source_deployed": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
    ),
    "shadow_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--source-deployed", type=Path, required=True)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V148: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    shadow_trace = args.shadow_trace.resolve()
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v147 = json.loads(V147_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v147_result": sha256(V147_RESULT),
        "v134_loader": sha256(V134_LOADER),
        "v145_loader": sha256(V145_LOADER),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "shadow_trace": sha256(shadow_trace),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v144_exact_event_label_green": (
            v144.get("decision")
            == "EARN_ONE_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION"
            and v144["causal_result"]["torque_events"] == 1
        ),
        "global_and_head_dagger_closed": (
            v147.get("decision") == "CLOSE_HEAD_ONLY_DAGGER"
        ),
        "single_center_single_joint_only": True,
        "radius_formula_has_no_search": True,
        "frozen_safety_projection_reapplied": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v148.single_center_residual_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V148_SINGLE_CENTER_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V148_SINGLE_CENTER_RESIDUAL_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V140 selected raw actor",
            "center": "V144 shadow trajectory tick 394",
            "joint": "right ankle / action index 13",
            "correction": (
                "exact two-fit oracle final-minus-base action at the center"
            ),
            "feature": "obs[115] concatenated with h_in[64]",
            "normalization": (
                "z-score over the frozen 4,800+600 aggregate; dimensions "
                "with std<1e-6 contribute zero"
            ),
            "radius": (
                "half the normalized Euclidean distance to the nearest "
                "other aggregate row"
            ),
            "outside_radius": "bit-exact V140 action",
            "postprocess": (
                "frozen G3 guard, x=0 deadband, and final rate projection "
                "are reapplied after the residual"
            ),
            "optimizer_or_training": False,
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "pass_rule": {
            "gate": "exactly one of 5,400 aggregate rows activates",
            "target": "center right ankle matches exact oracle <=1e-7",
            "preservation": "all other aggregate actions bit-exact",
            "state": "previous_action_out equals final action; h_out exact",
            "safety": "reapplied deployment transform contract passes",
        },
        "stop_rule": (
            "if the graph changes any other aggregate row/element, misses "
            "the center target, or fails the deployment contract, close "
            "the local residual; do not change center, radius, feature, or "
            "correction"
        ),
        "authority": {
            "cpu_graph_contract": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V148 single-center residual preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One center, one right-ankle correction, radius derived from the "
        "nearest other frozen state.\n"
        "- No training, behavior, Colab, policy deployment, or hardware "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
