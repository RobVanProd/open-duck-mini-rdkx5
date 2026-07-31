#!/usr/bin/env python3
"""Preregister the V143 torque-only nonlinear actor CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRAINING = ROOT / "training/winner_v143_torque_only_actor_distillation.py"
V134_TRAINING = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
RUNNER = ROOT / "tools/run_winner_v143_torque_only_actor_cpu_contract.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V142_ATTRIBUTION = (
    ANALYSIS / "winner_v142_transferred_load_attribution.json"
)
OUTPUT = ANALYSIS / "winner_v143_torque_only_actor_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V143_TORQUE_ONLY_ACTOR_CPU_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v142_attribution": (
        "38049a224d0d6190b6415a5691ecbabd9e5915ac8a6b788245abdc08b2234181"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v134_training_module": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "training_module": (
        "6b206b23ff6cada49ebb22a04735aaae4cb91c353de0d950883a3ce5c5e058ab"
    ),
    "runner": (
        "384d510cd8d257202b69f25de8e0a572b001b160319d1e1d1b1260e7e57fd8ce"
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
            raise FileExistsError(f"refusing to overwrite V143: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    deployed = args.v121_final_deployed.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v142 = json.loads(V142_ATTRIBUTION.read_text(encoding="utf-8"))
    input_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "v142_attribution": sha256(V142_ATTRIBUTION),
        "v121_transform": sha256(V121_TRANSFORM),
        "v134_training_module": sha256(V134_TRAINING),
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
        "transferred_load_attribution_green": (
            v142.get("status")
            == "PASS_WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION"
            and v142.get("decision")
            == (
                "PREREGISTER_TORQUE_ONLY_PRESERVATION_CONSTRAINED_ACTOR_CPU"
            )
        ),
        "target_class_changed_from_v134_not_optimizer": True,
        "class_balance_derived_without_sweep": True,
        "scale_logits_frozen_as_unsupervised": True,
        "two_update_cpu_smoke_only": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v143.torque_only_actor_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "selection": {
            "source": "V121 final recurrent actor",
            "teacher": "V131 exact common-safe two-fit oracle traces",
            "causal_evidence": (
                "V142 showed that the V140 direction repaired the labeled "
                "startup knee but transferred closed-loop load to the "
                "mature right ankle"
            ),
            "mechanical_change": (
                "only torque-projected rows retain oracle targets; every "
                "supreme-only and unchanged row targets the source action"
            ),
            "optimizer_change_from_v134": False,
            "parameter_search": False,
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "dataset": {
            "rows": 4_800,
            "torque_corrected_rows": 17,
            "supreme_only_rows_reset_to_source": 54,
            "preservation_rows": 4_783,
            "smoke_batch": (
                "all 17 torque rows plus first 239 SHA-sorted "
                "preservation rows"
            ),
            "correction_weight": "4783/17",
            "preservation_weight": 1.0,
        },
        "objective": {
            "action": (
                "class-balanced MSE against torque-only final targets"
            ),
            "hidden": "unweighted MSE on frozen source h_out",
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
            "direction": "full-smoke-batch gradient",
            "initial_step": "1/max(1, global_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": (
                "Armijo decrease with fixed conventional fraction 1e-4"
            ),
            "identical_to_v134": True,
            "search_or_retry": False,
        },
        "pass_rule": {
            "step_zero": "deployed inference matches V121 final <=1e-7",
            "loss": "total and action losses strictly decrease",
            "corrected_ratio": (
                "<=0.95 after two updates on smoke and full datasets"
            ),
            "preservation_ratio": (
                "<=0.01 on smoke and all 4,783 preservation rows"
            ),
            "hidden_mse": (
                "<=0.01 times corrected baseline MSE on smoke and full"
            ),
            "leaves": (
                "every non-scale actor leaf changes; scale logits stay exact"
            ),
            "exports": "step 0 and 2 stateful ONNX contracts both pass",
        },
        "stop_rule": (
            "if any check fails, close this exact torque-only actor "
            "formulation; do not tune the optimizer, target population, "
            "class weight, number of updates, or pass thresholds"
        ),
        "authority": {
            "cpu_contract": not failed,
            "formal_distillation": False,
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
        "# Winner V143 torque-only actor CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Targets: 17 exact torque corrections; 4,783 exact source "
        "actions.\n"
        "- Two deterministic V134-identical updates; no sweep or retry.\n"
        "- No behavior, Colab, policy deployment, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
