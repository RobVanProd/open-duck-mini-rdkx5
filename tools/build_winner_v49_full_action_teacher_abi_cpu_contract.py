#!/usr/bin/env python3
"""Freeze the default-off Winner-v49 full-action teacher ABI CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))

import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


OUTPUT = ANALYSIS / "winner_v49_full_action_teacher_abi_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT_20260722.md"
V48C_RESULT = ANALYSIS / "winner_v48c_causal_population_scope_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v49_full_action_teacher_abi_cpu_contract.py"),
    "teacher": Path("patches/winner_v49_full_action_static_target_teacher.py"),
    "teacher_tests": Path("tests/test_winner_v49_full_action_static_target_teacher.py"),
    "runner": Path("tools/run_winner_v49_full_action_teacher_abi_cpu_contract.py"),
    "runner_tests": Path("tests/test_winner_v49_full_action_teacher_abi_cpu_contract.py"),
    "winner_v48c_result": Path(
        "outputs/analysis/winner_v48c_causal_population_scope_result.json"
    ),
    "winner_v42_result": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "pitch_teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "action_boundary": Path("patches/winner_v12_calibrator_training.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v49 contract: {path}")

    causal = json.loads(V48C_RESULT.read_text(encoding="utf-8"))
    table_result = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    table = v49.v43.load_teacher_table(table_result)
    if (
        causal.get("status") != "PASS_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
        or causal.get("decision")
        != "AUTHORIZE_FULL_14D_STATIC_TEACHER_MECHANISM_PREREGISTRATION_ONLY"
        or causal.get("findings", {}).get("full_teacher_support_pass_count") != 32
        or causal.get("findings", {}).get("classification_counts", {}).get(
            "pitch_nonpitch_interaction"
        )
        != 3
        or tuple(table) != v49.v43.CONFIGURATION_IDS
        or not v49.per_element_scale_is_preserved()
    ):
        raise ValueError("Winner-v49 source authority changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v49.full_action_teacher_abi_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_FULL_ACTION_TEACHER_CPU_PROOF_ONLY",
        "question": (
            "Can the exact Winner-v42 target supervise all 14 actions while preserving "
            "the old six-pitch per-element weight exactly and adding the eight "
            "causally required non-pitch zero targets?"
        ),
        "teacher_abi": {
            "configuration_ids": list(v49.v43.CONFIGURATION_IDS),
            "configuration_occurrences": "exactly two, one per actuator plant",
            "duration_ticks": 250,
            "raw_and_bounded_targets": "bit-exact to Winner-v43",
            "supervised_action_indices": list(v49.ACTION_INDICES),
            "pitch_action_indices": list(v49.PITCH_ACTION_INDICES),
            "nonpitch_action_indices": list(v49.NONPITCH_ACTION_INDICES),
            "supervised_elements": 15 * 2 * 250 * 14,
            "loss": "mean squared candidate-minus-stopped-bounded-target on all valid action elements",
            "old_pitch_teacher_scale": float(v49.OLD_PITCH_TEACHER_SCALE),
            "full_action_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "scale_rule": (
                "old_scale * 14 / 6, making float32 scale/14 bit-exact to old_scale/6"
            ),
            "actor_inputs_or_deployable_onnx_abi_change": False,
            "privileged_configuration_use": "training-label lookup only",
            "default_off": "baseline loss and gradients bit-exact",
        },
        "pass_checks": [
            "bind the exact Winner-v48c causal result and Winner-v42 table",
            "construct exactly 30 two-plant x 250-tick labels and 105000 selected elements",
            "match Winner-v43 raw and bounded targets bit-exactly",
            "prove all 14 valid elements are selected and target/previous paths are stopped",
            "prove finite nonzero teacher gradients on every action index",
            "prove full-scale divided by 14 is float32 bit-exact to old scale divided by 6",
            "prove pitch-only candidate gradients retain the old scaled pitch gradient",
            "prove the disabled combined loss and gradients are bit-exact to baseline",
            "execute no optimizer, simulator, locomotion, export, or hardware work",
        ],
        "source_evidence": {
            "winner_v48c_result_lf_sha256": lf_sha256(V48C_RESULT),
            "winner_v42_result_lf_sha256": lf_sha256(V42_RESULT),
            "full_teacher_support_pass_count": 32,
            "pitch_output_causal_pairs": 25,
            "pitch_nonpitch_interaction_pairs": 3,
        },
        "execution_now": {
            "synthetic_teacher_rows": 0,
            "optimizer_updates": 0,
            "simulator_behavior_ticks": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "training_authorized": False,
            "one_update_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered source-gradient CPU contract",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v49 full-action teacher ABI CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Supervised indices / elements: `14 / 105,000`",
                "- Pitch/non-pitch causal evidence: `25 / 3` pairs",
                "- Old/full scale: `58.436370849609375 / 136.35153198242188`",
                "- Optimizer / simulator / locomotion / export / robot: `0 / 0 / 0 / 0 / 0`",
                "",
                "A pass proves only the training-label ABI. It cannot run an update,",
                "select a checkpoint, train locomotion, or clear the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
