#!/usr/bin/env python3
"""Preregister the V145 one-step on-policy DAgger CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRAINING = ROOT / "training/winner_v145_on_policy_dagger.py"
V134_TRAINING = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
RUNNER = ROOT / "tools/run_winner_v145_on_policy_dagger_cpu_contract.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
OUTPUT = ANALYSIS / "winner_v145_on_policy_dagger_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "v131_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v140_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v134_training_module": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "training_module": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "runner": (
        "c6e18bc2679372eca83872aedb84d1e6f6430106a52bcc6aa21e211cfebdd104"
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
    "teacher_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "shadow_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
    "v140_selected_deployed": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
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
    parser.add_argument("--shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V145: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    shadow_trace = args.shadow_trace.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    selected_deployed = Path(
        v140["artifacts"]["selected_deployed"]["path"]
    )
    input_hashes = {
        "v131_result": sha256(V131_RESULT),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v121_transform": sha256(V121_TRANSFORM),
        "v134_training_module": sha256(V134_TRAINING),
        "training_module": sha256(TRAINING),
        "runner": sha256(RUNNER),
        "network_source": sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "teacher_result": sha256(V131_RESULT),
        "shadow_trace": sha256(shadow_trace),
        "v140_selected_deployed": sha256(selected_deployed),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "two_fit_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
        ),
        "v140_actor_contract_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "v144_causal_screen_green": (
            v144.get("status")
            == "PASS_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION"
            and v144.get("decision")
            == "EARN_ONE_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION"
        ),
        "one_dataset_aggregation_iteration_only": True,
        "joint_element_targets_only": True,
        "optimizer_identical_to_v134": True,
        "training_not_yet_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v145.on_policy_dagger_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V145_ON_POLICY_DAGGER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V145_ON_POLICY_DAGGER_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "exactly reconstructed V140 actor",
            "dataset": (
                "4,800 V131 teacher states plus the 600-state V144 "
                "unmodified V140 trajectory"
            ),
            "target": (
                "replace only joint elements explicitly projected by the "
                "two-fit torque oracle; preserve the V140 output on every "
                "other joint element and preserve V140 h_out"
            ),
            "why_distinct": (
                "V142 proved the prior miss arose after closed-loop "
                "trajectory shift; V144 now supplies labels on that visited "
                "state distribution instead of another offline-only fit"
            ),
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "dataset": {
            "rows": 5_400,
            "teacher_rows": 4_800,
            "shadow_on_policy_rows": 600,
            "teacher_corrected_rows": 17,
            "shadow_corrected_rows": 4,
            "joint_element_labels": 60,
            "preservation_rows": 5_379,
            "correction_weight": "5379/21",
        },
        "optimizer": {
            "updates": 2,
            "batch": "all 5,400 rows",
            "direction": "full-batch gradient",
            "initial_step": "1/max(1, global_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": (
                "Armijo decrease with fixed conventional fraction 1e-4"
            ),
            "scale_logits_frozen": True,
            "search_or_retry": False,
        },
        "pass_rule": {
            "reconstruction": (
                "V140 JAX reconstruction matches selected deployment "
                "<=1e-7 and reproduces V144 action/h_out <=1e-6"
            ),
            "corrected_ratio": (
                "<=0.95 overall, on V131 rows, and on V144 rows"
            ),
            "preservation_ratio": (
                "<=0.01 overall, on V131 rows, and on V144 rows"
            ),
            "hidden_mse": "<=0.01 times corrected baseline MSE",
            "leaves": (
                "every non-scale actor leaf changes; scale logits stay exact"
            ),
            "exports": "step 0 and 2 stateful ONNX contracts both pass",
        },
        "stop_rule": (
            "if any check fails, close one-step on-policy DAgger from V140; "
            "do not alter row populations, targets, class balance, update "
            "count, optimizer, or thresholds"
        ),
        "authority": {
            "cpu_contract": not failed,
            "behavior": False,
            "hosted_training": False,
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
        "# Winner V145 on-policy DAgger CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One 5,400-row aggregate; only 60 torque-projected joint "
        "elements receive teacher targets.\n"
        "- Two deterministic full-batch updates; no sweep or retry.\n"
        "- No behavior, Colab, policy deployment, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
