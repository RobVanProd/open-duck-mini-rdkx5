#!/usr/bin/env python3
"""Freeze T105's ABI-preserving two-frame hidden-gate falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T104_PREREG = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
T104_RESULT = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t105_two_frame_gate_falsifier.py"
TEST = ROOT / "tests" / "test_t105_two_frame_gate.py"
OUTPUT = ANALYSIS / "t105_two_frame_gate_preregistration.json"
MARKDOWN = ANALYSIS / "T105_TWO_FRAME_GATE_PREREGISTRATION_20260728.md"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T105 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T105 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T105 preregistration requires a clean worktree")

    t104_prereg = json.loads(T104_PREREG.read_text(encoding="utf-8"))
    t104_result = json.loads(T104_RESULT.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    traces = [
        item
        for item in t104_prereg["traces"]
        if float(item["command_x_m_s"]) > 0.0
    ]
    pair_keys = {
        (
            item["checkpoint_id"],
            item["fit_id"],
            float(item["command_x_m_s"]),
        )
        for item in traces
    }
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t104_preregistration": T104_PREREG,
        "t104_result": T104_RESULT,
        "hidden_gate_asset": GATE,
    }
    checks = {
        "t104_exactly_selects_gate_stabilization": (
            t104_result["status"]
            == "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
            and t104_result["classification"]
            == "HARD_GATE_DYNAMICS_INCONSISTENT"
            and t104_result["decision"]
            == "EARN_T105_GATE_STABILIZATION_CPU_PREREGISTRATION_ONLY"
        ),
        "gate_asset_exact": (
            gate["status"] == "FROZEN_T98_HIDDEN_GATE_ASSET"
            and gate["derivation"]["feature"]
            == "policy_state_output.h_out[0]"
        ),
        "exactly_twenty_four_moving_traces": len(traces) == 24,
        "exactly_twelve_paired_groups": len(pair_keys) == 12,
        "each_pair_has_nominal_and_negative_com": all(
            {
                item["population"]
                for item in traces
                if (
                    item["checkpoint_id"],
                    item["fit_id"],
                    float(item["command_x_m_s"]),
                )
                == key
            }
            == {"nominal", "com_x_negative"}
            for key in pair_keys
        ),
        "all_trace_receipts_exact": all(
            Path(item["trace"]["path"]).stat().st_size
            == item["trace"]["bytes"]
            and sha256(Path(item["trace"]["path"]))
            == item["trace"]["sha256"]
            for item in traces
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_graph_transform_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t105_two_frame_gate_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T105_TWO_FRAME_GATE_FALSIFIER"
            if not failed
            else "HOLD_T105_TWO_FRAME_GATE_PREREGISTRATION"
        ),
        "question": (
            "Can an ABI-preserving equal two-frame hidden score, using "
            "h_in and h_out, make the negative-configuration gate stable "
            "without a tuned smoothing coefficient?"
        ),
        "gate_asset": receipt(GATE),
        "traces": traces,
        "population": {
            "moving_traces": 24,
            "paired_groups": 12,
            "warmup_ticks": 32,
            "labels": {"nominal": -1, "com_x_negative": 1},
            "group_key": [
                "checkpoint_id",
                "fit_id",
                "command_x_m_s",
            ],
        },
        "candidate": {
            "current_score": (
                "dot((h_out - mean) / scale, coefficient) + intercept"
            ),
            "previous_score": (
                "dot((h_in - mean) / scale, coefficient) + intercept"
            ),
            "two_frame_score": (
                "0.5 * (current_score + previous_score)"
            ),
            "threshold_derivation": (
                "For each training population, derive the finite interval "
                "of thresholds satisfying <=5% nominal false-active and "
                "<=5% negative-COM false-inactive under score>=threshold; "
                "choose the interval midpoint."
            ),
            "validation": (
                "leave one matched nominal/negative-COM trajectory pair "
                "out; derive threshold on the other eleven pairs; evaluate "
                "only the held-out pair; aggregate all twelve folds"
            ),
            "new_state": False,
            "new_input_or_output": False,
            "scalar_search": False,
        },
        "thresholds": {
            "maximum_expected_class_error_fraction": 0.05,
            "maximum_post_warmup_transitions_per_failing_trace": 4,
            "maximum_h_in_previous_h_out_error": 1.0e-6,
            "all_twelve_folds_must_have_feasible_threshold": True,
        },
        "decision_rule": {
            "pass": (
                "The full-population threshold interval is nonempty; all "
                "twelve held-out folds have a nonempty training interval; "
                "aggregate held-out nominal false-active and negative-COM "
                "false-inactive fractions are each <=0.05; no failing "
                "negative-COM trace exceeds four post-warmup transitions; "
                "and h_in is the exact prior h_out."
            ),
            "pass_decision": (
                "EARN_T106_TWO_FRAME_GATE_GRAPH_TRANSFORM_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_TWO_FRAME_STATELESS_GATE_STABILIZATION"
            ),
            "training_selection_weight": 0,
            "no_behavior_or_training": True,
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
            "one_cpu_trace_falsifier": not failed,
            "graph_transform": False,
            "behavior": False,
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
                "# T105 two-frame gate preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Candidate: exact equal mean of current/prior hidden score",
                "- Validation: `12` matched leave-one-pair-out folds",
                "- ABI / graph / behavior / training changes: `0 / 0 / 0 / 0`",
                "- Colab / robot: `0 / 0`",
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
