#!/usr/bin/env python3
"""Run the preregistered T13 shadow-recurrent handoff CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t13_shadow_hidden_preregistration.json"
RESULT = ANALYSIS / "t13_shadow_hidden_result.json"
MARKDOWN = ANALYSIS / "T13_SHADOW_HIDDEN_RESULT_20260726.md"


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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_receipt(item: dict[str, Any], label: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != item["bytes"]
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T13 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["schema_version"]
        != "open_duck.t13_shadow_hidden_preregistration.v1"
        or value["status"]
        != "PREREGISTERED_T13_SHADOW_HIDDEN_CPU_CONTRACT"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T13 preregistration identity changed")
    for name, item in value["sources"].items():
        verify_receipt(item, name)
    for checkpoint in value["candidate"]["checkpoints"]:
        verify_receipt(checkpoint["policy"], checkpoint["checkpoint_id"])
    for fit_id, item in value["candidate"]["fits"].items():
        verify_receipt(item, fit_id)
    verify_receipt(value["candidate"]["calibrator"], "calibrator")
    verify_receipt(value["candidate"]["reference"], "reference")
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"][
        "required_file_sha256"
    ].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T13 playground changed: {relative}")
    return value


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


def exact_com_readback(report: dict[str, Any] | None) -> bool:
    report = report or {}
    readback = report.get("readback") or {}
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [-0.05, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and isinstance(readback.get("before"), list)
        and isinstance(readback.get("after"), list)
        and len(readback["before"]) == 3
        and len(readback["after"]) == 3
        and abs(
            float(readback["after"][0])
            - float(readback["before"][0])
            + 0.05
        )
        <= 1.0e-12
        and float(readback["after"][1])
        == float(readback["before"][1])
        and float(readback["after"][2])
        == float(readback["before"][2])
    )


def read_one_trace(path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or rows[0].get("tick") != 0:
        raise RuntimeError(f"T13 expected exactly tick zero: {path}")
    return rows[0]


def run_block(
    prereg: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
    root: Path,
) -> dict[str, Any]:
    directory = root / checkpoint["checkpoint_id"] / fit_id
    if directory.exists():
        raise FileExistsError(f"refusing to reuse T13 block: {directory}")
    directory.mkdir(parents=True)
    trace = directory / "tick0.jsonl"
    evaluation = directory / "evaluation.json"
    stdout = directory / "stdout.log"
    command = [
        sys.executable,
        str(ROOT / "tools" / "evaluate_t13_shadow_hidden_contract.py"),
        "--policy",
        checkpoint["policy"]["path"],
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["candidate"]["fits"][fit_id]["path"],
        "--reference-feature-table",
        prereg["candidate"]["reference"]["path"],
        "--calibrator",
        prereg["candidate"]["calibrator"]["path"],
        "--trace-jsonl",
        str(trace),
        "--output-json",
        str(evaluation),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1200,
    )
    stdout.write_text(
        completed.stdout, encoding="utf-8", newline="\n"
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T13 worker failed rc={completed.returncode}; "
            f"tail={completed.stdout[-8000:]}"
        )
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "fit_id": fit_id,
        "command": command,
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "trace": receipt(trace),
        "payload": json.loads(evaluation.read_text(encoding="utf-8")),
        "row": read_one_trace(trace),
    }


def replay_cell(
    policy_path: Path,
    block: dict[str, Any],
) -> dict[str, Any]:
    payload = block["payload"]
    row = block["row"]
    mode = ((payload["run"].get("modes") or {}).get("fitted") or {})
    audit = mode.get("response_calibration") or {}
    shadow_hidden = np.asarray(
        audit.get("shadow_policy_hidden"), dtype=np.float32
    )[None, :]
    context = np.asarray(
        audit.get("calibration_context"), dtype=np.float32
    )[None, :]
    obs = np.asarray(row["obs_state"], dtype=np.float32)[None, :]
    previous = np.asarray(
        row["policy_state_input"]["previous_action"], dtype=np.float32
    )
    traced_hidden = np.asarray(
        row["policy_state_input"]["h_in"], dtype=np.float32
    )
    traced_action = np.asarray(row["action"], dtype=np.float32)[None, :]
    ort_session = session(policy_path)

    def infer(hidden: np.ndarray, observation: np.ndarray) -> list[np.ndarray]:
        return ort_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )

    shadow_action, shadow_previous, _ = infer(shadow_hidden, obs)
    zero_action, _, _ = infer(np.zeros_like(shadow_hidden), obs)
    x0_obs = obs.copy()
    x0_obs[:, 6:9] = 0.0
    x0_obs[:, 101:115] = 0.0
    x0_action, x0_previous, _ = infer(shadow_hidden, x0_obs)
    shadow_delta = float(
        np.max(np.abs(shadow_action - zero_action))
    )
    context_hash = array_sha256(context)
    hidden_hash = array_sha256(shadow_hidden)
    checks = {
        "block_complete": (
            payload.get("status")
            == "COMPLETE_T13_SHADOW_HIDDEN_BLOCK"
            and payload["run"].get("status") == "PASS"
        ),
        "com_readback_exact": exact_com_readback(
            payload["run"].get("dynamics_override")
        ),
        "response_prefix_exact": bool(
            audit.get("enabled") is True
            and audit.get("calibration_ticks") == 250
            and audit.get("home_return_ticks") == 0
            and audit.get("handoff_state_preserved") is True
            and audit.get("shadow_policy_enabled") is True
            and audit.get("shadow_policy_steps") == 250
            and audit.get("shadow_policy_actions_ignored") is True
            and audit.get("calibration_final_action")
            == [
                0.0,
                0.0,
                -0.5,
                0.25,
                0.25,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.5,
                0.25,
                0.25,
            ]
        ),
        "shadow_hidden_valid": bool(
            shadow_hidden.shape == (1, 64)
            and np.all(np.isfinite(shadow_hidden))
            and np.count_nonzero(shadow_hidden)
            and audit.get("shadow_policy_hidden_finite") is True
            and audit.get("shadow_policy_hidden_nonzero") is True
            and audit.get("locomotion_hidden_matches_shadow") is True
            and audit.get("shadow_policy_hidden_sha256") == hidden_hash
            and np.array_equal(shadow_hidden, traced_hidden)
        ),
        "context_valid": bool(
            context.shape == (1, 64)
            and np.all(np.isfinite(context))
            and audit.get("context_finite") is True
            and audit.get("context_sha256") == context_hash
        ),
        "graph_trace_replay_exact": bool(
            np.array_equal(shadow_action, traced_action)
            and np.array_equal(shadow_previous, shadow_action)
            and row.get("policy_graph_authoritative_output") is True
            and float(row.get("policy_host_action_delta_max_abs", 1.0))
            == 0.0
        ),
        "bounds_and_rate_green": bool(
            np.all(np.isfinite(shadow_action))
            and np.all(shadow_action >= -1.0)
            and np.all(shadow_action <= 1.0)
            and float(row.get("sent_target_rate_excess_rad_s", 1.0))
            <= 1.0e-6
            and float(
                row.get("conservative_rate_excess_rad_s", 1.0)
            )
            <= 1.0e-6
        ),
        "x0_exact": bool(
            np.array_equal(x0_action, np.zeros_like(x0_action))
            and np.array_equal(
                x0_previous, np.zeros_like(x0_previous)
            )
        ),
        "shadow_changes_final_action": shadow_delta > 1.0e-6,
    }
    return {
        "checkpoint_id": block["checkpoint_id"],
        "fit_id": block["fit_id"],
        "checks": checks,
        "shadow_hidden_sha256": hidden_hash,
        "context_sha256": context_hash,
        "shadow_vs_zero_final_action_linf": shadow_delta,
        "raw": {
            "command": block["command"],
            "evaluation": block["evaluation"],
            "stdout": block["stdout"],
            "trace": block["trace"],
        },
        "_shadow_hidden": shadow_hidden,
        "_context": context,
        "_obs": obs,
        "_previous": previous,
        "_policy": policy_path,
    }


def cross_plant_visibility(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    ort_session = session(left["_policy"])
    feed = {
        "obs": left["_obs"],
        "previous_action": left["_previous"],
        "calibration_context": left["_context"],
    }
    left_action = ort_session.run(
        ["continuous_actions"],
        {**feed, "h_in": left["_shadow_hidden"]},
    )[0]
    right_hidden_action = ort_session.run(
        ["continuous_actions"],
        {**feed, "h_in": right["_shadow_hidden"]},
    )[0]
    hidden_separation = float(
        np.max(np.abs(left["_shadow_hidden"] - right["_shadow_hidden"]))
    )
    action_separation = float(
        np.max(np.abs(left_action - right_hidden_action))
    )
    return {
        "checkpoint_id": left["checkpoint_id"],
        "same_observation_source_fit": left["fit_id"],
        "counterfactual_hidden_fit": right["fit_id"],
        "hidden_linf_separation": hidden_separation,
        "same_observation_final_action_linf_separation": action_separation,
        "hidden_response_separated": hidden_separation > 1.0e-7,
        "hidden_response_actionable": action_separation > 1.0e-6,
    }


def public_cell(cell: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in cell.items() if not key.startswith("_")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.work_root.resolve()
    if root.exists():
        raise FileExistsError(f"refusing to reuse T13 work root: {root}")
    root.mkdir(parents=True)
    prereg = load_preregistration()

    cells = []
    for checkpoint in prereg["candidate"]["checkpoints"]:
        for fit_id in prereg["candidate"]["fits"]:
            block = run_block(prereg, checkpoint, fit_id, root)
            cells.append(
                replay_cell(Path(checkpoint["policy"]["path"]), block)
            )
    pairs = []
    for checkpoint in prereg["candidate"]["checkpoints"]:
        matches = [
            cell
            for cell in cells
            if cell["checkpoint_id"] == checkpoint["checkpoint_id"]
        ]
        by_fit = {cell["fit_id"]: cell for cell in matches}
        pairs.append(
            cross_plant_visibility(by_fit["p30"], by_fit["p31_34"])
        )

    checks = {
        "exact_four_cells": len(cells) == 4,
        "all_cell_checks": all(
            all(cell["checks"].values()) for cell in cells
        ),
        "both_plant_hidden_states_separate": all(
            pair["hidden_response_separated"] for pair in pairs
        ),
        "both_plant_hidden_states_actionable": all(
            pair["hidden_response_actionable"] for pair in pairs
        ),
        "cpu_only": True,
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    passed = all(checks.values())
    basis = {
        "schema_version": "open_duck.t13_shadow_hidden_result.v1",
        "status": (
            "PASS_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
            if passed
            else "HOLD_T13_SHADOW_HIDDEN_RESPONSE_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_T14_SHADOW_HIDDEN_COM_BEHAVIOR_PREREGISTRATION_ONLY"
            if passed
            else "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": [
            name for name, passed_check in checks.items() if not passed_check
        ],
        "cells": [public_cell(cell) for cell in cells],
        "cross_plant_visibility": pairs,
        "summary": {
            "minimum_shadow_vs_zero_final_action_linf": min(
                cell["shadow_vs_zero_final_action_linf"] for cell in cells
            ),
            "minimum_hidden_linf_separation": min(
                pair["hidden_linf_separation"] for pair in pairs
            ),
            "minimum_cross_plant_action_linf_separation": min(
                pair["same_observation_final_action_linf_separation"]
                for pair in pairs
            ),
        },
        "execution": {
            "simulator_prefix_cells": 4,
            "scored_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    result = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T13 shadow-hidden CPU contract result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- Scored behavior cells: `0`",
                "- Optimizer / hosted / robot: `0 / 0 / 0`",
                (
                    "- Minimum shadow-vs-zero final-action effect: "
                    f"`{basis['summary']['minimum_shadow_vs_zero_final_action_linf']:.9g}`"
                ),
                (
                    "- Minimum cross-plant hidden separation: "
                    f"`{basis['summary']['minimum_hidden_linf_separation']:.9g}`"
                ),
                (
                    "- Minimum same-observation cross-plant action effect: "
                    f"`{basis['summary']['minimum_cross_plant_action_linf_separation']:.9g}`"
                ),
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
                "This contract does not authorize training, deployment, "
                "Gate 5, hardware, or motion.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(result["decision"])
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
