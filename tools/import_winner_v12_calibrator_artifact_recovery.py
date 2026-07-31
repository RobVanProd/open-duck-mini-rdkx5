#!/usr/bin/env python3
"""Import the single frozen Winner-v12 read-only recovery result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v12_calibrator_artifact_recovery_contract.json"
OUTPUT_JSON = ANALYSIS / "winner_v12_calibrator_artifact_recovery_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY_RESULT_20260721.md"
EXPECTED_RAW_SHA256 = "940f8a94cf5710b120892f1d7207f96ce6835e79cf970647e3bb65f646ac19e8"
EXPECTED_CONTRACT_LF_SHA256 = (
    "c06c1d5e4d94d0396d25caa2dfefa718a22823cca660404c45cc60f59a9a3826"
)
EXPECTED_RUN_ID = 29803319695
EXPECTED_RUN_COMMIT = "0d7b0309431e5401259f0528d8cc0ee009bc9d4a"
EXPECTED_ARTIFACT_ID = 8484550478
EXPECTED_ARTIFACT_DIGEST = (
    "sha256:4d6be6c54f0c44cc2279aa37b7bf462b8a6912a40b8e71ed46ebb195bbbfd070"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate(raw: dict[str, Any]) -> None:
    expected_top_level = {
        "authority",
        "checks",
        "contract",
        "corrected_observer_plant_canary",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "failed_smoke",
        "force_range_contract",
        "onnx",
        "population",
        "schema_version",
        "stage1",
        "stage2",
        "status",
        "support_boundary_canary",
    }
    if set(raw) != expected_top_level:
        raise ValueError("raw recovery result schema changed")
    if raw["schema_version"] != "winner_v12.calibrator_artifact_recovery_result.v1":
        raise ValueError("raw recovery schema version changed")
    if raw["status"] != "PASS_WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY":
        raise ValueError("raw recovery did not pass")
    if raw["decision"] != "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY":
        raise ValueError("raw recovery decision exceeded or changed authority")
    checks = raw["checks"]
    if not isinstance(checks, dict) or not checks:
        raise ValueError("raw recovery checks are absent")
    if not all(
        isinstance(name, str) and isinstance(value, bool)
        for name, value in checks.items()
    ):
        raise ValueError("raw recovery checks must be named booleans")
    observed_failed = sorted(name for name, value in checks.items() if not value)
    if raw["failed_checks"] != observed_failed or observed_failed:
        raise ValueError("raw recovery PASS requires every check to pass")
    if raw["contract"] != {
        "canonical_lf_sha256": EXPECTED_CONTRACT_LF_SHA256,
        "hash_mode": "lf",
        "path": "/home/runner/work/open-duck-mini-rdkx5/open-duck-mini-rdkx5/outputs/analysis/winner_v12_calibrator_artifact_recovery_contract.json",
    }:
        raise ValueError("raw recovery is not bound to the frozen contract")
    if lf_sha256(CONTRACT) != EXPECTED_CONTRACT_LF_SHA256:
        raise ValueError("repository recovery contract changed")
    if raw["failed_smoke"] != {
        "checkpoint_sha256": "5748978f050c222f156d733f709b1ddc76e2b27bebaa00ed726ad53d9fca2288",
        "graph_sha256": "9c0d018cd4d496abf9081584f969a917293ef72ecdcd6047483d6c553389aa4c",
        "run_id": 29802206612,
    }:
        raise ValueError("recovered artifact identity changed")
    expected_execution = {
        "formal_support_cells": 0,
        "locomotion_behavior_cells": 0,
        "locomotion_training_steps": 0,
        "new_checkpoints_written": 0,
        "new_onnx_graphs_written": 0,
        "optimizer_updates": {"stage1": 0, "stage2": 0},
        "protected_policy_inference_calls": 0,
        "retry_of_failed_smoke": False,
        "robot_or_rdk_access": 0,
    }
    if raw["execution"] != expected_execution:
        raise ValueError("raw recovery exceeded zero-update authority")
    if raw["authority"] != {
        "formal_behavior_evaluation_executed": False,
        "full_training_executed": False,
        "pass_authorizes_only": "a separate prospective full-calibrator training preregistration",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("raw recovery authority changed")
    population = raw["population"]
    if population["configuration_ids"] != [
        "MASS_LOW",
        "MASS_HIGH",
        "COM_X_NEG",
        "COM_X_POS",
        "COM_Y_NEG",
        "COM_Y_POS",
        "COM_Z_NEG",
        "COM_Z_POS",
        "INERTIA_X_LOW",
        "INERTIA_X_HIGH",
        "INERTIA_Y_LOW",
        "INERTIA_Y_HIGH",
        "INERTIA_Z_LOW",
        "INERTIA_Z_HIGH",
        "COM_CORNER_00",
        "COM_CORNER_01",
    ]:
        raise ValueError("raw recovery population changed")
    if population["plant_counts"] != {
        "P30_ALL_JOINT": 8,
        "P31_34_PITCH_WITH_P30_NONPITCH": 8,
    }:
        raise ValueError("raw recovery hidden-plant balance changed")
    if not (
        population["stage1_valid_transitions"] > 0
        and population["stage2_attempted_samples"]
        >= population["stage2_valid_transitions"]
        > 0
    ):
        raise ValueError("raw recovery has no valid transition population")
    versions = raw["environment"]["software_versions"]
    if not versions["exact"] or versions["observed"] != versions["expected"]:
        raise ValueError("raw recovery software versions changed")
    if (
        raw["environment"]["playground_commit"]
        != "b9be205ac64488c23504ca42e5ec790337adeec3"
    ):
        raise ValueError("raw recovery Playground commit changed")
    required_nested = {
        "stage1_m": raw["stage1"]["m_comparison"]["bit_exact"],
        "stage1_v": raw["stage1"]["v_comparison"]["bit_exact"],
        "stage1_parameters": raw["stage1"]["parameter_comparison"]["bit_exact"],
        "stage2_m": raw["stage2"]["m_comparison"]["bit_exact"],
        "stage2_v": raw["stage2"]["v_comparison"]["bit_exact"],
        "stage2_parameters": raw["stage2"]["parameter_comparison"]["bit_exact"],
        "onnx_abi": raw["onnx"]["abi_exact"],
        "onnx_jax": raw["onnx"]["jax_onnx_at_most_1e_7"],
        "observer_exact": raw["corrected_observer_plant_canary"][
            "fixed_p30_observer_bit_exact_across_hidden_plant_choice"
        ],
        "plants_distinct": raw["corrected_observer_plant_canary"][
            "hidden_physical_plants_are_distinct"
        ],
    }
    if not all(required_nested.values()):
        raise ValueError("raw recovery nested proof failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v12 recovery result is already imported")
    raw_path = args.raw_result.resolve()
    if sha256(raw_path) != EXPECTED_RAW_SHA256:
        raise ValueError("raw recovery result hash changed")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    validate(raw)
    payload = dict(raw)
    payload["repository_attribution"] = {
        "github_run_id": EXPECTED_RUN_ID,
        "github_run_commit": EXPECTED_RUN_COMMIT,
        "github_artifact_id": EXPECTED_ARTIFACT_ID,
        "github_artifact_digest": EXPECTED_ARTIFACT_DIGEST,
        "raw_result_sha256": EXPECTED_RAW_SHA256,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator artifact-recovery result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run: `{EXPECTED_RUN_ID}`",
                f"- Raw result SHA-256: `{EXPECTED_RAW_SHA256}`",
                "- Optimizer updates: `0`",
                "- New checkpoint/ONNX: `0` / `0`",
                "- Formal behavior cells: `0`",
                "- Robot access/clearance: `0` / `false`",
                "",
                "All frozen checks passed. This authorizes only a separate prospective",
                "full-calibrator training preregistration; it does not select the smoke",
                "checkpoint or authorize training, behavior evaluation, or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
