#!/usr/bin/env python3
"""Freeze the default-off Winner-v43 static-target teacher ABI CPU contract."""

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

import winner_v43_static_target_teacher as v43  # noqa: E402


OUTPUT = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_20260722.md"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v43_static_target_teacher_abi_cpu_contract.py"),
    "teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "teacher_tests": Path("tests/test_winner_v43_static_target_teacher.py"),
    "runner": Path("tools/run_winner_v43_static_target_teacher_abi_cpu_contract.py"),
    "runner_tests": Path("tests/test_winner_v43_static_target_teacher_abi_cpu_contract.py"),
    "preregistration_tests": Path(
        "tests/test_winner_v43_static_target_teacher_abi_cpu_preregistration.py"
    ),
    "result_importer": Path(
        "tools/import_winner_v43_static_target_teacher_abi_cpu_result.py"
    ),
    "result_importer_tests": Path(
        "tests/test_winner_v43_static_target_teacher_abi_cpu_import.py"
    ),
    "workflow": Path(".github/workflows/winner-v43-static-target-teacher-abi-cpu.yml"),
    "winner_v42_preregistration": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_preregistration.json"
    ),
    "winner_v42_result": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "winner_v42_importer": Path(
        "tools/import_winner_v42_static_target_teacher_table.py"
    ),
    "action_boundary": Path("patches/winner_v12_calibrator_training.py"),
    "inward_graph_constants": Path("patches/winner_v11_dynamic_calibration_networks.py"),
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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v43 contract")
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    table = v43.load_teacher_table(v42)
    if tuple(table) != v43.CONFIGURATION_IDS:
        raise ValueError("Winner-v42 table did not authorize Winner-v43")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v43.static_target_teacher_abi_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_STATIC_TARGET_TEACHER_ABI_CPU_PROOF_ONLY",
        "question": (
            "Can the exact Winner-v42 selected table be represented as a stopped, "
            "training-only, pitch-only, graph-bounded teacher whose disabled objective "
            "is bit-exact and whose privileged configuration key cannot enter deployment?"
        ),
        "teacher_abi": {
            "configuration_ids": list(v43.CONFIGURATION_IDS),
            "configuration_occurrences": "exactly two, one per actuator plant",
            "duration_ticks": 250,
            "raw_target": "selected Winner-v42 three-coordinate target expanded to 14 actions",
            "bounded_target": (
                "exact Winner-v11 inward graph boundary applied relative to realized "
                "previous_action at the same tick"
            ),
            "supervised_action_indices": list(v43.PITCH_ACTION_INDICES),
            "supervised_elements": 15 * 2 * 250 * 6,
            "loss": "mean squared candidate-minus-stopped-bounded-target on valid pitch elements",
            "actor_inputs": "unchanged deployable observation, previous_action, and recurrent hidden state",
            "privileged_configuration_use": "training-label lookup only",
            "deployable_graph_inputs_or_outputs_added": [],
            "nonpitch_teacher_gradient": "exact zero",
            "default_off": "baseline loss and gradients bit-exact",
        },
        "pass_checks": [
            "bind the exact imported Winner-v42 result and all 15 selected targets",
            "rederive every 14-action target and match both selected replay raw-target hashes",
            "construct exactly 30 two-plant x 250-tick labels and 45,000 selected elements",
            "match the inherited inward graph boundary bit-exactly",
            "prove target and previous-action paths are stop-gradient",
            "prove teacher gradients are finite/nonzero on all six pitch indices and exact zero elsewhere",
            "prove the disabled combined loss and gradients are bit-exact to baseline",
            "prove the enabled unit-scale diagnostic changes only pitch gradients",
            "execute no optimizer update, behavior rollout, deployment export, or hardware access",
        ],
        "execution_now": {
            "synthetic_teacher_rows": 0,
            "optimizer_updates": 0,
            "simulator_behavior_ticks": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v42_result_lf_sha256": lf_sha256(V42_RESULT),
            "winner_v42_repository_attribution": v42["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered zero-update source-gradient CPU contract"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v43 static-target teacher ABI CPU contract", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Configurations / plants / ticks: `15 / 2 / 250`",
            "- Supervised indices / elements: `6 / 45,000`",
            "- Optimizer / simulator / training / export / robot: `0 / 0 / 0 / 0 / 0`", "",
            value["question"], "",
            "The table is a privileged training label only. A pass cannot train, alter",
            "an ONNX ABI, select a checkpoint, implement a runtime wrapper, or clear the robot.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
