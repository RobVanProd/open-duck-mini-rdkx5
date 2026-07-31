#!/usr/bin/env python3
"""Freeze T104's read-only T100C gate-dynamics and expert-effect audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T101_RESULT = ANALYSIS / "t101_t100c_postexport_result.json"
T102_RESULT = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T103_RESULT = ANALYSIS / "t103_t100c_negative_endpoint_result.json"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
RUNNER = ROOT / "tools" / "run_t104_t100c_gate_dynamics_audit.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t104_t100c_gate_dynamics.py"
OUTPUT = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
MARKDOWN = ANALYSIS / "T104_T100C_GATE_DYNAMICS_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def trace_population(
    result: dict[str, Any], population: str
) -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    for block in result["blocks"]:
        for cell in block["result"]["cells"]:
            path = Path(cell["protection"]["path"])
            traces.append(
                {
                    "population": population,
                    "condition_id": block["condition_id"],
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(
                        block.get(
                            "step",
                            1_003_520
                            if block["checkpoint_id"].endswith("HALF")
                            else 2_007_040,
                        )
                    ),
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(cell["command_x_m_s"]),
                    "cell_green": bool(cell["cell_green"]),
                    "behavior_samples": int(cell["behavior"]["samples"]),
                    "termination_reason": cell["behavior"][
                        "termination_reason"
                    ],
                    "trace": receipt(path),
                }
            )
    return traces


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T104 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T104 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T104 preregistration requires a clean worktree")

    t101 = json.loads(T101_RESULT.read_text(encoding="utf-8"))
    t102 = json.loads(T102_RESULT.read_text(encoding="utf-8"))
    t103 = json.loads(T103_RESULT.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    traces = [
        *trace_population(t102, "nominal"),
        *trace_population(t103, "com_x_negative"),
    ]
    policies = {
        str(step): t101["deployments"][str(step)]["wrapped"]
        for step in (0, 1_003_520, 2_007_040)
    }
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t101_result": T101_RESULT,
        "t102_result": T102_RESULT,
        "t103_result": T103_RESULT,
        "hidden_gate_asset": GATE,
    }
    checks = {
        "t102_exactly_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
        ),
        "t103_exactly_closed_at_nine_of_sixteen": (
            t103["status"] == "HOLD_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
            and t103["decision"]
            == "CLOSE_T100C_HIDDEN_EXPERT_CONTINUATION"
            and t103["condition"]["green_cells"] == 9
        ),
        "gate_asset_frozen": (
            gate["status"] == "FROZEN_T98_HIDDEN_GATE_ASSET"
            and gate["derivation"]["feature"]
            == "policy_state_output.h_out[0]"
            and gate["derivation"]["decision"]
            == "negative_com_if_score_greater_than_or_equal_to_zero"
        ),
        "exactly_thirty_two_traces": len(traces) == 32,
        "sixteen_traces_per_population": (
            sum(item["population"] == "nominal" for item in traces) == 16
            and sum(
                item["population"] == "com_x_negative" for item in traces
            )
            == 16
        ),
        "all_trace_receipts_exact": all(
            sha256(Path(item["trace"]["path"])) == item["trace"]["sha256"]
            and Path(item["trace"]["path"]).stat().st_size
            == item["trace"]["bytes"]
            for item in traces
        ),
        "all_policy_receipts_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            and Path(item["path"]).stat().st_size == item["bytes"]
            for item in policies.values()
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t104_t100c_gate_dynamics_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T104_T100C_GATE_DYNAMICS_AUDIT"
            if not failed
            else "HOLD_T104_T100C_GATE_DYNAMICS_PREREGISTRATION"
        ),
        "question": (
            "Did T100C fail because the frozen hidden gate switches or "
            "misclassifies on-policy trajectories, or because the active "
            "negative expert's correction destabilizes the closed loop?"
        ),
        "policies": policies,
        "gate_asset": receipt(GATE),
        "traces": traces,
        "measurements": {
            "warmup_ticks": 32,
            "trace_replay_max_abs_tolerance": 1.0e-6,
            "gate_score_reconstruction_tolerance": 1.0e-5,
            "material_final_action_delta": 1.0e-6,
            "maximum_expected_class_error_fraction": 0.05,
            "maximum_post_warmup_transitions_per_trace": 4,
            "intermediates": [
                "hidden_gate_score",
                "negative_com_gate",
                "negative_adapter_location",
                "raw_continuous_actions",
                "velocity_bounded_actions",
            ],
            "same_state_counterfactual": (
                "current checkpoint versus step-0 zero-head graph at each "
                "stored obs, previous_action, and h_in; calibration_context "
                "is the proven unused all-zero compatibility input"
            ),
        },
        "decision_rule": {
            "gate_dynamics_inconsistent_if": (
                "on moving post-warmup rows, nominal false-active fraction "
                "or negative-COM false-inactive fraction exceeds 0.05, or "
                "any failing negative-COM trace has more than four gate "
                "transitions after warmup"
            ),
            "gate_dynamics_decision": (
                "EARN_T105_GATE_STABILIZATION_CPU_PREREGISTRATION_ONLY"
            ),
            "expert_drift_if": (
                "gate dynamics are consistent, the trained final action "
                "differs materially from step 0, and negative-COM moving "
                "failures increase from half to final"
            ),
            "expert_drift_decision": (
                "EARN_T105_EXPERT_DRIFT_ATTRIBUTION_PREREGISTRATION_ONLY"
            ),
            "otherwise": "CLOSE_T100C_WITHOUT_HIDDEN_EXPERT_SUCCESSOR",
            "training_selection_weight": 0,
            "no_scalar_screen_or_training": True,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_trace_audit": not failed,
            "successor_preregistration": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T104 T100C gate-dynamics preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Population: `32 frozen traces / no simulator rerun`",
                "- Comparison: trained half/final against zero-head step 0",
                "- Gate warmup boundary: `32 ticks`",
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
