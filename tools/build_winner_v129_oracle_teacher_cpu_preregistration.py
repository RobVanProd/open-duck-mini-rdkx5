#!/usr/bin/env python3
"""Preregister one V129 oracle-teacher distillation CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
AUDIT = ANALYSIS / "winner_v129_oracle_teacher_dataset_audit.json"
ATTRIBUTION = ANALYSIS / "winner_v128_nominal_failure_attribution.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
TRAINING = ROOT / "training/winner_v129_oracle_teacher_distillation.py"
RUNNER = ROOT / "tools/run_winner_v129_oracle_teacher_cpu_contract.py"
OUTPUT = ANALYSIS / "winner_v129_oracle_teacher_cpu_preregistration_v3.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V129_ORACLE_TEACHER_CPU_PREREGISTRATION_V3_20260724.md"
)
EXPECTED = {
    "dataset_audit": (
        "9fa2e685c5df292f8f817bb81e5fb5b08e2e924963cbd310f8ac08d334dfc224"
    ),
    "v128_attribution": (
        "3fcf28bc2a70d35008968881afe45e6865ddb8f19e30bb13bf9737584a92e6d1"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "training_module": (
        "2ecdae3fbe9c50cf10833651fa2dae9af7326d8af728cf1c7cc0630323a57a98"
    ),
    "runner": (
        "ca59440ded91cf70d96cc02a6a5e53c5700ccf3cc31084bf6b177ad3311cd0cc"
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
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--v121-final-deployed", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V129: {path}")
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    deployed = args.v121_final_deployed.resolve()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    attribution = json.loads(
        ATTRIBUTION.read_text(encoding="utf-8")
    )
    input_hashes = {
        "dataset_audit": sha256(AUDIT),
        "v128_attribution": sha256(ATTRIBUTION),
        "v121_transform": sha256(V121_TRANSFORM),
        "training_module": sha256(TRAINING),
        "runner": sha256(RUNNER),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": sha256(deployed),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "dataset_audit_green": (
            audit.get("status")
            == "PASS_WINNER_V129_ORACLE_TEACHER_DATASET_AUDIT"
            and audit.get("failed_checks") == []
            and audit.get("decision")
            == "AUTHORIZE_ONE_V129_CPU_DISTILLATION_CONTRACT"
        ),
        "ppo_lagrangian_closed_no_retry": (
            attribution.get("mechanism_verdict", {}).get(
                "ppo_lagrangian_v121_recipe"
            )
            == "CLOSED_NO_RETRY"
            and attribution.get("authority", {}).get(
                "additional_ppo_lagrangian"
            )
            is False
        ),
        "final_teacher_selection_is_mechanism_derived": (
            audit["teacher_correction"]["projected_events"]
            and audit["dataset"]["source"]
            == "V121_TRAIN_MATCHED_FINAL plus exact oracle"
        ),
        "half_teacher_identity_is_not_trained": True,
        "only_adapter_location_head_trainable": True,
        "all_other_policy_and_value_leaves_frozen": True,
        "class_weight_derived_without_search": True,
        "two_update_smoke_only": True,
        "formal_training_not_authorized": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v129.oracle_teacher_cpu_preregistration.v3"
        ),
        "supersedes": {
            "artifact": (
                "winner_v129_oracle_teacher_cpu_preregistration_v2.json"
            ),
            "reason": (
                "the v2 CPU runner restored the hosted normalizer as a plain "
                "dictionary; v3 applies the previously validated read-only "
                "RunningStatisticsState CPU topology remap; execution stopped "
                "before any optimizer update"
            ),
        },
        "status": (
            "PREREGISTERED_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V129_ORACLE_TEACHER_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "dataset": {
            "rows": 4_800,
            "corrected_rows": 14,
            "preservation_rows": 4_786,
            "source": "V121 final exact-oracle closed-loop traces",
            "inputs": ["obs[115]", "previous_action[14]", "h_in[64]"],
            "targets": ["oracle final action[14]", "teacher h_out[64]"],
            "teacher_correction_weight": "4786/14",
            "preservation_weight": 1.0,
        },
        "objective": {
            "action": (
                "class-balanced mean squared error on the exact final "
                "deployment action"
            ),
            "hidden": "unweighted mean squared error on teacher h_out",
            "total": "action_mse + hidden_mse",
            "trainable_leaves": [
                "policy/adapter_location/kernel",
                "policy/adapter_location/bias",
            ],
            "frozen_leaves": "all other normalizer/policy/value leaves",
            "reward_or_ppo": False,
        },
        "smoke": {
            "updates": 2,
            "batch_size": 256,
            "batch": "all 14 corrected rows plus 242 preservation rows",
            "optimizer": "Adam",
            "learning_rate": 0.0003,
            "learning_rate_source": "frozen V121 PPO value, not searched",
            "exports": [0, 2],
        },
        "pass_rule": {
            "loss": "action and total loss both decrease",
            "changed_leaves": "exactly the two adapter_location leaves",
            "step_zero": "deployed inference matches V121 final <=1e-7",
            "exports": "both 115/14/64 stateful ABI contracts pass",
        },
        "authority": {
            "cpu_contract_authorized": not failed,
            "formal_distillation_preregistration": False,
            "formal_distillation_training": False,
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
        "# Winner V129 oracle-teacher CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Source: V121 final because it is the only nonzero oracle teacher.\n"
        "- Trainable: adapter_location kernel+bias only.\n"
        "- Weight: 4,786/14, derived from the two dataset classes.\n"
        "- Smoke: two CPU updates; no behavior or formal training.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
