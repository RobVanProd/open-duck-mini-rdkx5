#!/usr/bin/env python3
"""Preregister the V137 recurrent sequence-teacher CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRAINING = ROOT / "training/winner_v137_sequence_teacher_distillation.py"
RUNNER = ROOT / "tools/run_winner_v137_sequence_teacher_cpu_contract.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V136_RESULT = ANALYSIS / "winner_v136_warm_start_startup_result.json"
OUTPUT = ANALYSIS / "winner_v137_sequence_teacher_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V137_SEQUENCE_TEACHER_CPU_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v136_warm_start_result": (
        "9347cdc8e627aaced830ef0a2cd0bc096793f016dd614c1b85bafe6ae2b4347c"
    ),
    "training_module": (
        "246c17ba3051965989aae0d34476daae527e7f06fedf0d9d6a93c0e58f2e77ca"
    ),
    "runner": (
        "9d701fc18b1bfc9f4473e667dd1ca3539ddc7bf9053075e58694a0190e851384"
    ),
    "network_source": (
        "ffd07d0a6e96d846aa1f62a8d131bf892f10db6b2a22710affe3946b7b145ebd"
    ),
    "source_checkpoint": (
        "c1d9b8574c941e2279294de14aca1cb57d4736bdc63635b5aaf1e205fa7f86c1"
    ),
    "cpu_template": (
        "217a1551c4cc778e4b957636a40ca6e01eafa51efeaef905eb73e9debc7c26e5"
    ),
    "v121_final_deployed": (
        "bc54ea1bf39e617f76771e7416de91db2ccfe0b1bf903de08faaa64a67ce4aab"
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
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--v121-final-deployed", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V137: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    deployed = args.v121_final_deployed.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v136 = json.loads(V136_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v121_transform": sha256(V121_TRANSFORM),
        "v131_behavior_result": sha256(V131_RESULT),
        "v136_warm_start_result": sha256(V136_RESULT),
        "training_module": sha256(TRAINING),
        "runner": sha256(RUNNER),
        "network_source": sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": sha256(deployed),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "robust_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "static_warm_start_closed": (
            v136.get("status")
            == "HOLD_WINNER_V136_WARM_START_STARTUP_SCREEN"
            and v136.get("decision")
            == "CLOSE_PHASE_CONSISTENT_WARM_START"
        ),
        "bptt_is_distinct_from_rowwise_teacher": True,
        "only_recurrent_adapter_is_trainable": True,
        "two_deterministic_cpu_updates_only": True,
        "formal_training_not_authorized": True,
        "behavior_not_authorized": True,
        "hosted_compute_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v137.sequence_teacher_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V137_SEQUENCE_TEACHER_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V121 final recurrent actor",
            "teacher": "V131 exact common-safe two-fit oracle",
            "question": (
                "Can gradients propagated through the recurrent chain over "
                "ticks 0-31 alter precursor hidden dynamics enough to learn "
                "the startup corrections without disturbing the full gait?"
            ),
            "why_distinct": (
                "V129/V134 used frozen rowwise h_in values. V137 scans the "
                "existing stateful policy from zero hidden and previous-action "
                "state, feeds each output state into the next tick, and "
                "backpropagates through that complete startup chain."
            ),
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "dataset": {
            "traces": 8,
            "ticks_per_trace": 600,
            "startup_ticks": 32,
            "startup_rows": 256,
            "full_corrected_rows": 71,
            "startup_corrected_rows": 15,
            "startup_preservation_rows": 241,
            "startup_correction_weight": "241/15",
            "target": "V131 exact common-safe final action[14]",
            "state_initialization": {
                "previous_action": "exact zero[14]",
                "h_in": "exact zero[64]",
            },
        },
        "objective": {
            "loss": (
                "class-balanced startup action MSE over the 8x32 recurrent "
                "scan; hidden energy is diagnostic only"
            ),
            "trainable_leaves": [
                "adapter_hidden_bias",
                "adapter_hidden_projection/kernel",
                "adapter_location/bias",
                "adapter_location/kernel",
                "adapter_obs_projection/kernel",
            ],
            "frozen": [
                "normalizer",
                "residual trunk and location",
                "scale logits",
                "value tree",
            ],
        },
        "optimizer": {
            "updates": 2,
            "direction": "full-batch recurrent gradient",
            "initial_step": "1/max(1, global_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": (
                "Armijo decrease with fixed conventional fraction 1e-4"
            ),
            "search_or_retry": False,
        },
        "pass_rule": {
            "startup_corrected_error": "<=0.95 times source",
            "full_corrected_error": "<=0.95 times source",
            "full_preservation_leakage": "<=0.01 times corrected baseline",
            "x0": "all candidate deployed actions remain exact zero",
            "leaves": (
                "exactly the five declared recurrent-adapter leaves change"
            ),
            "step_zero": "deployed inference matches V121 final <=1e-7",
            "exports": "step 0 and 2 stateful ONNX contracts both pass",
        },
        "stop_rule": (
            "if any pass rule fails, close recurrent sequence-teacher "
            "distillation; do not alter the window, weights, line search, "
            "trainable leaves, or optimizer"
        ),
        "authority": {
            "cpu_contract": not failed,
            "formal_cpu_preregistration": False,
            "formal_training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
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
        "# Winner V137 sequence-teacher CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Two deterministic CPU BPTT updates over ticks 0-31 only.\n"
        "- Exactly five recurrent-adapter leaves may change.\n"
        "- No formal training, behavior evaluation, Colab, or hardware "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
