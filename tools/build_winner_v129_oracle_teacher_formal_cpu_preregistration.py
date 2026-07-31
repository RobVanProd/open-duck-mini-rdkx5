#!/usr/bin/env python3
"""Preregister the single V129 formal CPU distillation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v129_oracle_teacher_cpu_result.json"
TRAINING = ROOT / "training/winner_v129_oracle_teacher_distillation.py"
RUNNER = (
    ROOT / "tools/run_winner_v129_oracle_teacher_formal_cpu_distillation.py"
)
OUTPUT = (
    ANALYSIS / "winner_v129_oracle_teacher_formal_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "cpu_result": (
        "865aacdcb5d990ec84b1c5bae44776d6889cf141282e0d3189aea1cef32eb79a"
    ),
    "training_module": (
        "2ecdae3fbe9c50cf10833651fa2dae9af7326d8af728cf1c7cc0630323a57a98"
    ),
    "formal_runner": (
        "6f7b5b0e0c45af68f502152541aa343719428771e348565ecff329d34a951e58"
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
            raise FileExistsError(f"refusing to overwrite formal V129: {path}")
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    deployed = args.v121_final_deployed.resolve()
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "cpu_result": sha256(CPU_RESULT),
        "training_module": sha256(TRAINING),
        "formal_runner": sha256(RUNNER),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": sha256(deployed),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "cpu_contract_green": (
            cpu_result.get("status")
            == "PASS_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
            and cpu_result.get("failed_checks") == []
            and cpu_result.get("decision")
            == "EARN_ONE_V129_FORMAL_CPU_DISTILLATION_PREREGISTRATION"
        ),
        "dataset_exact_4800_rows": (
            cpu_result["dataset"]["rows"] == 4_800
            and cpu_result["dataset"]["corrected_rows"] == 14
            and cpu_result["dataset"]["preservation_rows"] == 4_786
        ),
        "head_only_smoke_green": (
            cpu_result["checks"]["only_adapter_location_head_changed"]
            and cpu_result["checks"]["two_updates_reduce_action_loss"]
        ),
        "two_epochs_derived_without_search": True,
        "two_checkpoint_persistence_required": True,
        "formal_run_cpu_only": True,
        "behavior_not_authorized": True,
        "hosted_compute_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v129.oracle_teacher_formal_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V129_FORMAL_CPU_DISTILLATION"
            if not failed
            else "HOLD_WINNER_V129_FORMAL_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "student_restore": "V121 final raw checkpoint",
            "teacher": "V121 final closed loop plus exact V126 oracle",
            "teacher_selection": (
                "mechanism-derived: V121 half has zero oracle corrections; "
                "V121 final has 14"
            ),
            "trainable_leaves": [
                "policy/adapter_location/kernel",
                "policy/adapter_location/bias",
            ],
            "frozen": "all other normalizer/policy/value leaves",
            "deployment_transition_in_loss": (
                "inherited rate -> actual-centered guard -> x=0 deadband -> "
                "final trained rate projection"
            ),
        },
        "dataset": {
            "rows": 4_800,
            "order": "ascending sha256(trace_name:tick)",
            "batch_size": 256,
            "updates_per_epoch": 19,
            "padding": "tail repeat with zero weight",
            "corrected_rows": 14,
            "preservation_rows": 4_786,
            "correction_weight": "4786/14",
        },
        "training": {
            "optimizer": "Adam",
            "learning_rate": 0.0003,
            "learning_rate_source": "frozen V121 value",
            "epochs": 2,
            "updates": 38,
            "exports": [0, 19, 38],
            "half_checkpoint": 19,
            "final_checkpoint": 38,
            "retry_or_resume": False,
        },
        "pass_rule": {
            "half_and_final": (
                "objective and corrected-row action MSE below step zero"
            ),
            "changed_leaves": "exactly two adapter_location leaves",
            "step_zero": "deployed inference matches V121 final <=1e-7",
            "exports": "all 115/14/64 stateful ABI contracts pass",
            "next": (
                "one separately preregistered frozen 16-cell nominal gate; "
                "both update-19 and update-38 checkpoints must pass"
            ),
        },
        "stop_rule": (
            "if this contract fails, or if either subsequent nominal "
            "checkpoint fails any cell, V129 head-only oracle distillation "
            "closes with no learning-rate, epoch, weighting, or retry change"
        ),
        "authority": {
            "formal_cpu_distillation": not failed,
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
        "# Winner V129 formal CPU distillation preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Train only the final adapter head for 38 deterministic CPU "
        "updates.\n"
        "- Export at updates 19 and 38; both must pass the later 16-cell "
        "nominal gate.\n"
        "- No Colab, behavior evaluation, hardware, retry, or parameter "
        "search is authorized here.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
