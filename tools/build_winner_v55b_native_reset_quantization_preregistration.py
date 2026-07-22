#!/usr/bin/env python3
"""Preregister one native-quantized reset-label attribution after Winner-v55."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v55b_native_reset_quantization_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V55B_NATIVE_RESET_QUANTIZATION_PREREGISTRATION_20260722.md"
V55_RESULT = ANALYSIS / "winner_v55_reset_label_handoff_result.json"
V55_RESULT_SHA256 = "4ded36d436484af1b801d078a436b654d3aabc2507a26565117af3703008ed0e"

SOURCES = {
    "builder": Path("tools/build_winner_v55b_native_reset_quantization_preregistration.py"),
    "runner": Path("tools/run_winner_v55b_native_reset_quantization.py"),
    "tests": Path("tests/test_winner_v55b_native_reset_quantization.py"),
    "v55_result": Path("outputs/analysis/winner_v55_reset_label_handoff_result.json"),
    "v55_preregistration": Path("outputs/analysis/winner_v55_reset_label_handoff_preregistration.json"),
    "v55_runner": Path("tools/run_winner_v55_reset_label_handoff.py"),
    "v54_runner": Path("tools/run_winner_v54_residual_teacher_causal.py"),
    "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_smoke_runner": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            raise FileExistsError(f"refusing to overwrite Winner-v55b contract: {path}")
    v55 = json.loads(V55_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V55_RESULT) != V55_RESULT_SHA256
        or v55.get("status") != "PASS_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC"
        or v55.get("classification") != "NO_RESET_LABEL_CONFLICT"
        or v55.get("reset_audit", {}).get("unique_reset_input_count") != 15
        or v55.get("execution", {}).get("reset_rows") != 30
        or v55.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v55 source changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v55b.native_reset_quantization_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_READ_ONLY_30_ROW_CPU_ATTRIBUTION_ONLY",
        "causal_question": (
            "Do the 15 exact raw reset inputs distinguished by Winner-v55 remain "
            "label-separable after the already frozen native BNO055 and servo quantization?"
        ),
        "frozen_source": {
            "v55_result_sha256": V55_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 453,
            "teacher_configuration_ids": [
                row["configuration_id"]
                for row in v55["reset_audit"]["rows"][::2]
            ],
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "raw_unique_reset_inputs": 15,
            "raw_unique_graph_actions": 15,
            "bounded_teacher_labels": 4,
        },
        "frozen_attribution": {
            "rows": 30,
            "transport": (
                "run_winner_v12_calibrator_support_gate.native_quantize_observation "
                "with no random noise, delay, rounding change, or fitted threshold"
            ),
            "input": "quantized obs[115] + zero previous_action[14] + zero h_in[64]",
            "collision": (
                "one exact quantized reset-input hash maps to more than one exact bounded-teacher-action hash"
            ),
            "raw_observation_hash_must_reproduce_v55": True,
        },
        "classification": {
            "NATIVE_QUANTIZATION_CREATES_RESET_LABEL_CONFLICT": (
                "at least one exact quantized input maps to multiple teacher labels"
            ),
            "NATIVE_RESET_LABELS_REMAIN_SEPARABLE": (
                "every exact quantized input maps to one teacher label"
            ),
            "decision_if_conflict": (
                "AUTHORIZE_UNIVERSAL_FIRST_ACTION_FEASIBILITY_PREREGISTRATION_ONLY"
            ),
            "decision_if_separable": (
                "AUTHORIZE_FIRST_TICK_TEACHER_MAPPING_CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
        },
        "pass_rule": {
            "exact_30_rows": True,
            "all_raw_observation_hashes_match_v55": True,
            "all_initial_contacts_double": True,
            "all_graph_actions_within_boundary": True,
            "all_values_finite": True,
        },
        "execution_now": {
            "reset_rows": 0,
            "simulator_steps": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": "one separate CPU mechanism preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v55b native reset-quantization preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Population: `15 configurations x 2 plants = 30 reset rows`",
                "- Simulator steps / optimizer / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
