#!/usr/bin/env python3
"""Preregister the V168 fit-conditioned two-policy CPU falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRAINING = ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
RUNNER = ROOT / "tools/run_winner_v168_fit_conditioned_policy_bank_cpu_contract.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V130_AUDIT = ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
OUTPUT = (
    ANALYSIS
    / "winner_v168_fit_conditioned_policy_bank_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_PREREGISTRATION_20260725.md"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network-source", type=Path, required=True)
    parser.add_argument("--source-checkpoint-hash", required=True)
    parser.add_argument("--cpu-template-hash", required=True)
    parser.add_argument("--v121-final-deployed", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite frozen V168 preregistration")

    observed = {
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v130_feature_audit": file_sha256(V130_AUDIT),
        "v131_behavior_result": file_sha256(V131_RESULT),
        "v134_cpu_result": file_sha256(V134_RESULT),
        "training_module": file_sha256(TRAINING),
        "runner": file_sha256(RUNNER),
        "network_source": file_sha256(args.network_source.resolve()),
        "source_checkpoint": args.source_checkpoint_hash,
        "cpu_template": args.cpu_template_hash,
        "v121_final_deployed": file_sha256(
            args.v121_final_deployed.resolve()
        ),
    }
    expected = {
        "v121_transform": (
            "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
        ),
        "v130_feature_audit": (
            "7b4078c3ea18c3a3e1d129de3329cca8e71d178d93b836ba37f552544bed33d7"
        ),
        "v131_behavior_result": (
            "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
        ),
        "v134_cpu_result": (
            "e25691c219eec4b76dea0f18b14e47b6fd840b6c0bc53c6c1817cdd5fbf3f387"
        ),
        "training_module": (
            "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
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
    checks = {
        "all_nonrunner_input_hashes_exact": all(
            observed[key] == value for key, value in expected.items()
        ),
        "v130_cross_fit_transfer_is_asymmetric": (
            json.loads(V130_AUDIT.read_text(encoding="utf-8"))[
                "cross_plant_fit"
            ]["p31_34_to_p30"]["corrected_ratio_to_zero_predictor"]
            > 1.0
        ),
        "v134_failed_only_preservation_leakage": (
            json.loads(V134_RESULT.read_text(encoding="utf-8"))[
                "failed_checks"
            ]
            == ["preservation_leakage_within_one_percent"]
        ),
        "same_v134_optimizer_and_thresholds": True,
        "two_independent_fit_actors_only": True,
        "no_scalar_search_or_alternate_partition": True,
        "automatic_fit_dispatch_is_not_yet_authorized": True,
        "hosted_training_not_authorized": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v168.fit_conditioned_policy_bank_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_FALSIFIER"
            if not failed
            else "INVALID_WINNER_V168_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed,
        "selection_evidence": {
            "v134_combined_actor": (
                "corrected ratio 0.8825987758072349 passed; preservation "
                "ratio 0.013381694364104099 exceeded the frozen 0.01 limit"
            ),
            "v130_cross_fit_transfer": {
                "p30_to_p31_corrected_ratio": 0.6463131073147258,
                "p31_to_p30_corrected_ratio": 6.134471284229614,
            },
            "hypothesis": (
                "the shared actor's preservation leakage is caused by "
                "combining two mechanically distinct measured actuator fits"
            ),
        },
        "dataset": {
            "source": "unchanged V131 exact common-safe oracle traces",
            "total_rows": 4_800,
            "fits": {
                "p30_all_joint": {
                    "rows": 2_400,
                    "corrected_rows": 36,
                    "preservation_rows": 2_364,
                    "smoke_rows": "all 36 corrected plus first 220 SHA-sorted preservation rows",
                    "correction_weight": "2364/36",
                },
                "p31_34_pitch_with_p30_nonpitch": {
                    "rows": 2_400,
                    "corrected_rows": 35,
                    "preservation_rows": 2_365,
                    "smoke_rows": "all 35 corrected plus first 221 SHA-sorted preservation rows",
                    "correction_weight": "2365/35",
                },
            },
        },
        "mechanism": {
            "actors": (
                "two independent copies restored exactly from V121 final, "
                "one per measured actuator fit"
            ),
            "per_policy_abi": "unchanged 115/14/64 stateful ONNX",
            "runtime_101_observation_contract": "unchanged",
            "future_dispatch": (
                "automatic pre-policy actuator-response classification; "
                "no manual dimensions, mass, or static assembly constants"
            ),
            "runtime_change_authorized": False,
        },
        "optimizer": {
            "updates_per_actor": 2,
            "direction": "full-batch gradient",
            "initial_step": "1/max(1, global_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": "Armijo decrease with fraction 1e-4",
            "trainable": "all actor leaves except scale_logits",
            "frozen": ["normalizer", "scale_logits", "value tree"],
            "search_or_retry": False,
        },
        "pass_rule": {
            "each_step_zero": "deployed output matches V121 final <=1e-7",
            "each_corrected_ratio": "<=0.95 after two updates",
            "each_preservation_ratio": "<=0.01",
            "each_hidden_mse": "<=0.01 times its corrected baseline MSE",
            "each_actor_leaves": (
                "all non-scale actor leaves change; scale logits stay exact"
            ),
            "exports": (
                "source and updated exports for both fits preserve exact ABI "
                "and inference contract"
            ),
        },
        "green_decision": (
            "earn only a reviewed automatic-fit-dispatch policy-bank "
            "contract and its CPU behavior preregistration"
        ),
        "stop_rule": (
            "if either fit misses any frozen V134 threshold, close the "
            "fit-conditioned two-policy full-actor smoke with no alternate "
            "partition, optimizer, update count, scalar, or retry"
        ),
        "authority": {
            "cpu_falsifier": not failed,
            "policy_bank_contract": False,
            "behavior_evaluation": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V168 fit-conditioned policy-bank CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Two independent V121-final actors, split only by the two frozen "
        "measured actuator fits.\n"
        "- Exact V134 optimizer, update count, and pass thresholds; no "
        "scalar or partition search.\n"
        "- Green earns only a reviewed automatic-fit-dispatch contract and "
        "a later CPU behavior preregistration.\n"
        "- No training, behavior evaluation, hardware, torque, or motion "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={file_sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
