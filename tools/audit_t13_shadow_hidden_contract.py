#!/usr/bin/env python3
"""Independently audit the T13 shadow-hidden CPU result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t13_shadow_hidden_preregistration.json"
RESULT = ANALYSIS / "t13_shadow_hidden_result.json"
AUDIT = ANALYSIS / "t13_shadow_hidden_independent_audit_v2.json"
MARKDOWN = (
    ANALYSIS / "T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_V2_20260726.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def read_one(path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or rows[0].get("tick") != 0:
        raise RuntimeError(f"T13 audit expected exactly tick zero: {path}")
    return rows[0]


def verify_raw(raw: dict[str, Any], issues: list[str], label: str) -> None:
    for name in ("evaluation", "stdout", "trace"):
        item = raw[name]
        path = Path(item["path"])
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            issues.append(f"{label}.{name}_receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    issues: list[str] = []
    contract_failures: list[str] = []
    prereg_basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    result_basis = {
        key: item
        for key, item in result.items()
        if key != "result_sha256"
    }
    if (
        canonical_sha256(prereg_basis)
        != prereg["preregistered_contract_sha256"]
    ):
        issues.append("preregistration_sha")
    if canonical_sha256(result_basis) != result["result_sha256"]:
        issues.append("result_sha")

    policies = {
        item["checkpoint_id"]: Path(item["policy"]["path"])
        for item in prereg["candidate"]["checkpoints"]
    }
    recomputed: dict[tuple[str, str], dict[str, Any]] = {}
    for cell in result["cells"]:
        key = (cell["checkpoint_id"], cell["fit_id"])
        verify_raw(cell["raw"], issues, ".".join(key))
        evaluation_path = Path(cell["raw"]["evaluation"]["path"])
        trace_path = Path(cell["raw"]["trace"]["path"])
        evaluation = json.loads(
            evaluation_path.read_text(encoding="utf-8")
        )
        row = read_one(trace_path)
        mode = (
            ((evaluation["run"].get("modes") or {}).get("fitted") or {})
        )
        response = mode.get("response_calibration") or {}
        hidden = np.asarray(
            response.get("shadow_policy_hidden"), dtype=np.float32
        )[None, :]
        context = np.asarray(
            response.get("calibration_context"), dtype=np.float32
        )[None, :]
        obs = np.asarray(row["obs_state"], dtype=np.float32)[None, :]
        previous = np.asarray(
            row["policy_state_input"]["previous_action"],
            dtype=np.float32,
        )
        traced_hidden = np.asarray(
            row["policy_state_input"]["h_in"], dtype=np.float32
        )
        traced_action = np.asarray(
            row["action"], dtype=np.float32
        )[None, :]
        ort_session = session(policies[cell["checkpoint_id"]])

        def infer(
            h_in: np.ndarray, observation: np.ndarray
        ) -> tuple[np.ndarray, np.ndarray]:
            action, previous_out = ort_session.run(
                ["continuous_actions", "previous_action_out"],
                {
                    "obs": observation,
                    "previous_action": previous,
                    "h_in": h_in,
                    "calibration_context": context,
                },
            )
            return action, previous_out

        action, previous_out = infer(hidden, obs)
        zero_action, _ = infer(np.zeros_like(hidden), obs)
        x0_obs = obs.copy()
        x0_obs[:, 6:9] = 0.0
        x0_obs[:, 101:115] = 0.0
        x0_action, x0_previous = infer(hidden, x0_obs)
        delta = float(np.max(np.abs(action - zero_action)))
        cell_issues = []
        if hidden.shape != (1, 64) or not np.all(np.isfinite(hidden)):
            cell_issues.append("hidden")
        if context.shape != (1, 64) or not np.all(np.isfinite(context)):
            cell_issues.append("context")
        if response.get("shadow_policy_steps") != 250:
            cell_issues.append("shadow_steps")
        if response.get("shadow_policy_actions_ignored") is not True:
            cell_issues.append("shadow_actions")
        if response.get("shadow_policy_hidden_sha256") != array_sha256(
            hidden
        ):
            cell_issues.append("hidden_sha")
        if response.get("context_sha256") != array_sha256(context):
            cell_issues.append("context_sha")
        if not np.array_equal(hidden, traced_hidden):
            cell_issues.append("handoff_hidden")
        if not np.array_equal(action, traced_action):
            cell_issues.append("trace_replay")
        if not np.array_equal(action, previous_out):
            cell_issues.append("previous_out")
        if not np.array_equal(x0_action, np.zeros_like(x0_action)):
            cell_issues.append("x0_action")
        if not np.array_equal(
            x0_previous, np.zeros_like(x0_previous)
        ):
            cell_issues.append("x0_previous")
        if delta <= 1.0e-6:
            cell_issues.append("shadow_action_visibility")
        if cell_issues:
            issues.extend(f"{'.'.join(key)}.{item}" for item in cell_issues)
        recomputed[key] = {
            "hidden": hidden,
            "context": context,
            "obs": obs,
            "previous": previous,
            "delta": delta,
        }
        if abs(
            delta - float(cell["shadow_vs_zero_final_action_linf"])
        ) > 1.0e-12:
            issues.append(f"{'.'.join(key)}.reported_delta")

    pair_metrics = []
    for checkpoint_id, policy in policies.items():
        left = recomputed[(checkpoint_id, "p30")]
        right = recomputed[(checkpoint_id, "p31_34")]
        ort_session = session(policy)
        feed = {
            "obs": left["obs"],
            "previous_action": left["previous"],
            "calibration_context": left["context"],
        }
        left_action = ort_session.run(
            ["continuous_actions"],
            {**feed, "h_in": left["hidden"]},
        )[0]
        right_action = ort_session.run(
            ["continuous_actions"],
            {**feed, "h_in": right["hidden"]},
        )[0]
        hidden_delta = float(
            np.max(np.abs(left["hidden"] - right["hidden"]))
        )
        action_delta = float(np.max(np.abs(left_action - right_action)))
        if hidden_delta <= 1.0e-7:
            contract_failures.append(
                f"{checkpoint_id}.plant_hidden_visibility"
            )
        if action_delta <= 1.0e-6:
            contract_failures.append(
                f"{checkpoint_id}.plant_action_visibility"
            )
        pair_metrics.append(
            {
                "checkpoint_id": checkpoint_id,
                "hidden_linf_separation": hidden_delta,
                "same_observation_final_action_linf_separation": (
                    action_delta
                ),
            }
        )

    expected_pass = not contract_failures
    expected_status = (
        "PASS_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
        if expected_pass
        else "HOLD_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
    )
    expected_decision = (
        "AUTHORIZE_T14_SHADOW_HIDDEN_COM_BEHAVIOR_PREREGISTRATION_ONLY"
        if expected_pass
        else "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
    )
    if result["status"] != expected_status:
        issues.append("status")
    if result["decision"] != expected_decision:
        issues.append("decision")
    expected_checks = {
        "all_cell_checks": not any(
            item.endswith(
                (
                    ".hidden",
                    ".context",
                    ".shadow_steps",
                    ".shadow_actions",
                    ".hidden_sha",
                    ".context_sha",
                    ".handoff_hidden",
                    ".trace_replay",
                    ".previous_out",
                    ".x0_action",
                    ".x0_previous",
                    ".shadow_action_visibility",
                )
            )
            for item in issues
        ),
        "both_plant_hidden_states_separate": not any(
            item.endswith(".plant_hidden_visibility")
            for item in contract_failures
        ),
        "both_plant_hidden_states_actionable": not any(
            item.endswith(".plant_action_visibility")
            for item in contract_failures
        ),
    }
    for name, expected in expected_checks.items():
        if result["checks"].get(name) is not expected:
            issues.append(f"reported_check.{name}")
    status = (
        "PASS_T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_V2"
        if not issues
        else "HOLD_T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_V2"
    )
    basis = {
        "schema_version": "open_duck.t13_shadow_hidden_audit.v2",
        "status": status,
        "result_sha256": result["result_sha256"],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "issues": issues,
        "recomputed_contract_failures": contract_failures,
        "recomputed_cells": len(recomputed),
        "recomputed_pairs": pair_metrics,
        "decision": result["decision"],
        "execution": {
            "simulator_prefix_cells": 0,
            "scored_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    audit = {**basis, "audit_sha256": canonical_sha256(basis)}
    AUDIT.write_text(
        json.dumps(audit, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T13 shadow-hidden independent audit",
                "",
                f"- Status: `{status}`",
                f"- Decision: `{result['decision']}`",
                f"- Issues: `{len(issues)}`",
                f"- Audit SHA-256: `{audit['audit_sha256']}`",
                "",
                "The audit replays the frozen ONNX graph and raw tick-zero "
                "receipts without importing the T13 runner.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
