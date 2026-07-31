#!/usr/bin/env python3
"""Preregister the V134 nonlinear full-actor teacher CPU smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRAINING = ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
RUNNER = ROOT / "tools/run_winner_v134_full_actor_teacher_cpu_contract.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V133_RESULT = ANALYSIS / "winner_v133_compact_local_residual_audit_v3.json"
OUTPUT = (
    ANALYSIS / "winner_v134_full_actor_teacher_cpu_preregistration_v3.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V134_FULL_ACTOR_TEACHER_CPU_PREREGISTRATION_V3_20260724.md"
)
EXPECTED = {
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v133_local_audit": (
        "c57f894724e0f350658945990f19b76caae9f3e7da219d32f97b9cb5df8f4229"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "training_module": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcBdbd8baa8"
    ).lower(),
    "runner": (
        "a9b572e7f95ca6d49b226d44d9733dda336133ffa7ef3915471b924aeeefcc1a"
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
            raise FileExistsError(f"refusing to overwrite V134: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    deployed = args.v121_final_deployed.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v133 = json.loads(V133_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "v133_local_audit": sha256(V133_RESULT),
        "v121_transform": sha256(V121_TRANSFORM),
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
        "compact_local_residual_closed": (
            v133.get("status")
            == "PASS_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT"
            and v133.get("decision")
            == "NO_COMPACT_LOCAL_RESIDUAL_FROM_NOMINAL_DATASET"
        ),
        "nonlinear_full_actor_is_mechanically_distinct": True,
        "class_balance_and_line_search_derived_without_sweep": True,
        "scale_logits_frozen_as_unsupervised": True,
        "two_update_cpu_smoke_only": True,
        "formal_training_not_authorized": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v134.full_actor_teacher_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V134_FULL_ACTOR_TEACHER_CPU_CONTRACT_V3"
            if not failed
            else "HOLD_WINNER_V134_FULL_ACTOR_TEACHER_CPU_PREREGISTRATION"
        ),
        "supersedes": {
            "artifact": (
                "winner_v134_full_actor_teacher_cpu_preregistration_v2.json"
            ),
            "reason": (
                "The V2 runner stopped before its first gradient because "
                "the hosted normalizer restored as a plain dictionary on "
                "the CPU topology. V3 applies the read-only "
                "RunningStatisticsState remap already validated by V129 "
                "and restores the exact 226-D privileged-state shape. "
                "Dataset, targets, thresholds, and optimizer are unchanged."
            ),
        },
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V121 final recurrent actor",
            "teacher": "V131 exact common-safe two-fit oracle",
            "why_distinct": (
                "updates the existing nonlinear residual trunk and recurrent "
                "adapter, rather than fitting a global linear head or a "
                "nearest-neighbor local wrapper"
            ),
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "dataset": {
            "rows": 4_800,
            "corrected_rows": 71,
            "torque_projected_rows": 17,
            "supreme_only_corrected_rows": 54,
            "preservation_rows": 4_729,
            "smoke_batch": "all 71 corrected plus first 185 SHA-sorted rows",
            "targets": [
                "V131 final action[14]",
                "V121/V131 h_out[64]",
            ],
            "correction_weight": "4729/71",
            "preservation_weight": 1.0,
        },
        "objective": {
            "action": (
                "class-balanced MSE on the exact final deployment action"
            ),
            "hidden": "unweighted MSE on the frozen teacher h_out",
            "total": "action MSE + hidden MSE",
            "trainable": (
                "all actor leaves except scale_logits kernel and bias"
            ),
            "frozen": [
                "normalizer",
                "scale_logits kernel and bias",
                "value tree",
            ],
        },
        "optimizer": {
            "updates": 2,
            "direction": "full-batch gradient",
            "initial_step": "1/max(1, global_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": (
                "Armijo decrease with fixed conventional fraction 1e-4"
            ),
            "search_or_retry": False,
        },
        "pass_rule": {
            "step_zero": "deployed inference matches V121 final <=1e-7",
            "loss": "total and action losses strictly decrease",
            "corrected_ratio": "<=0.95 after two smoke updates",
            "preservation_ratio": "<=0.01",
            "hidden_mse": "<=0.01 times corrected baseline MSE",
            "leaves": (
                "every non-scale actor leaf changes; scale logits stay exact"
            ),
            "exports": "step 0 and 2 stateful ONNX contracts both pass",
        },
        "stop_rule": (
            "if any check fails, do not run formal nonlinear teacher "
            "distillation and do not alter optimizer constants"
        ),
        "authority": {
            "cpu_contract": not failed,
            "formal_cpu_distillation": False,
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
        "# Winner V134 full-actor teacher CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Two deterministic CPU updates only.\n"
        "- Nonlinear actor and recurrent adapter trainable; scale logits "
        "frozen.\n"
        "- No formal training, behavior evaluation, Colab, or hardware "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
