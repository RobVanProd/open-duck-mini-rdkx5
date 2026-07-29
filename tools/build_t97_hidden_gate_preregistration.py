#!/usr/bin/env python3
"""Freeze the T97 live-hidden COM gate falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t97_hidden_gate_preregistration.json"
MARKDOWN = ANALYSIS / "T97_HIDDEN_GATE_PREREGISTRATION_20260728.md"
AUDITOR = ROOT / "tools" / "audit_t97_hidden_gate.py"
TEST = ROOT / "tests" / "test_t97_hidden_gate.py"
T93_PREREG = ANALYSIS / "t93_adapter_authority_preregistration.json"
T93_RESULT = ANALYSIS / "t93_adapter_authority_result.json"
T71_RESULT = ANALYSIS / "t71_t67_com_hidden_causal_result.json"
T76_RESULT = ANALYSIS / "t76_com_hidden_geometry_result.json"


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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T97 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T97 preregistration requires a clean worktree")

    t93_prereg = json.loads(T93_PREREG.read_text(encoding="utf-8"))
    t93_result = json.loads(T93_RESULT.read_text(encoding="utf-8"))
    t71_result = json.loads(T71_RESULT.read_text(encoding="utf-8"))
    t76_result = json.loads(T76_RESULT.read_text(encoding="utf-8"))
    selected = [
        item
        for item in t93_prereg["traces"]
        if item["population"] in {"nominal", "com_x_negative"}
        and float(item["command_x_m_s"]) in {0.074, 0.077, 0.08}
    ]
    population_counts = {
        population: sum(item["population"] == population for item in selected)
        for population in ("nominal", "com_x_negative")
    }
    checks = {
        "t71_hidden_signal_present_and_causal": (
            t71_result["status"]
            == "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
            and t71_result["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        ),
        "t76_rank_one_response_closed": (
            t76_result["status"] == "HOLD_T76_COM_HIDDEN_GEOMETRY"
            and t76_result["decision"]
            == "CLOSE_COM_AXIS_OUTPUT_HEAD_REFLECTION"
        ),
        "t93_no_hard_adapter_authority_limit": (
            t93_result["status"] == "PASS_T93_ADAPTER_AUTHORITY_AUDIT"
            and t93_result["classification"]
            == "NO_HARD_ADAPTER_AUTHORITY_LIMIT_FOUND"
        ),
        "paired_population_exact": (
            len(selected) == 24
            and population_counts
            == {"nominal": 12, "com_x_negative": 12}
        ),
        "two_checkpoints_two_fits_three_commands": (
            {item["checkpoint_id"] for item in selected}
            == {"T78_JOINT_ADAPTER_HALF", "T78_JOINT_ADAPTER_FINAL"}
            and {item["fit_id"] for item in selected} == {"p30", "p31_34"}
            and {float(item["command_x_m_s"]) for item in selected}
            == {0.074, 0.077, 0.08}
        ),
        "no_training_simulator_or_hardware": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T97 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": "open_duck.t97_hidden_gate_preregistration.v1",
        "status": "PREREGISTERED_T97_HIDDEN_GATE_FALSIFIER",
        "question": (
            "Can the mature T78 recurrent hidden state identify the exact "
            "negative torso-COM-X plant early and out of group, strongly "
            "enough to justify a shared-ABI hidden-gated adapter expert?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "t71": (
                "the live recurrent state contains plant-sensitive COM "
                "information and causally changes the action"
            ),
            "t76": (
                "the hidden displacement is not stable rank one, so a fixed "
                "axis reflection is closed"
            ),
            "t78_t93": (
                "the jointly trained adapter has material full-rank action "
                "authority, but one shared head did not retain COM-X-negative"
            ),
            "selected_falsifier": (
                "test the cheapest deployable gate first: a regularized "
                "linear readout of the current h_out, with no new input"
            ),
        },
        "population": {
            "labels": {
                "nominal": -1,
                "com_x_negative": 1,
            },
            "ticks": [8, 16, 32],
            "trace_count": len(selected),
            "sample_count": len(selected) * 3,
            "checkpoints": ["T78_JOINT_ADAPTER_HALF", "T78_JOINT_ADAPTER_FINAL"],
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.074, 0.077, 0.08],
            "feature": "policy_state_output.h_out[0] float32[64]",
        },
        "classifier": {
            "type": "train-fold standardized linear ridge classifier",
            "ridge": (
                "identity penalty after train-fold standardization; "
                "intercept unpenalized; no fitted scalar or sweep"
            ),
            "threshold": 0.0,
            "cross_validation": [
                "leave-one-checkpoint-out",
                "leave-one-fit-out",
                "leave-one-command-out",
                "leave-one-checkpoint-fit-command-group-out",
            ],
        },
        "thresholds": {
            "minimum_each_family_balanced_accuracy": 0.90,
            "minimum_each_fold_balanced_accuracy": 0.75,
            "minimum_group_holdout_tick8_negative_recall": 0.75,
            "minimum_group_holdout_tick8_nominal_specificity": 0.75,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T98_HIDDEN_GATED_EXPERT_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_LINEAR_LIVE_HIDDEN_EXPERT_GATE_WITHOUT_TRAINING"
            ),
            "pass_requires": (
                "every threshold and receipt check passes; a pass authorizes "
                "only a step-zero-exact CPU software contract"
            ),
        },
        "traces": selected,
        "inputs": {
            "builder": receipt(Path(__file__).resolve()),
            "auditor": receipt(AUDITOR),
            "test": receipt(TEST),
            "t93_preregistration": receipt(T93_PREREG),
            "t93_result": receipt(T93_RESULT),
            "t71_result": receipt(T71_RESULT),
            "t76_result": receipt(T76_RESULT),
        },
        "checks": checks,
        "failed_checks": [],
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t97_read_only_audit": True,
            "t98_cpu_contract_preregistration": False,
            "training": False,
            "hosted_compute": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T97 live-hidden expert-gate preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Inputs: mature T78 hidden traces, nominal vs exact COM-X-negative",
                "- Features: `h_out[64]` at ticks `8/16/32`",
                "- Validation: checkpoint, fit, command, and exact-group holdouts",
                "- Model: fixed linear ridge readout; no scalar sweep",
                "- Optimizer / simulator / hosted / robot: `0 / 0 / 0 / 0`",
                (
                    "- Contract SHA-256: `"
                    f"{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"traces={len(selected)} samples={len(selected) * 3}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
