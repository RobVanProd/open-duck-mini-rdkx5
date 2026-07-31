#!/usr/bin/env python3
"""Attribute T129's sole nominal failure from frozen trace state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402


PREREG = ANALYSIS / "t134_t129_nominal_gate_attribution_preregistration.json"
RESULT = ANALYSIS / "t134_t129_nominal_gate_attribution_result.json"
MARKDOWN = ANALYSIS / "T134_T129_NOMINAL_GATE_ATTRIBUTION_RESULT_20260729.md"
OUTPUTS = (
    ("negative_com_gate", TensorProto.BOOL, [1, 1]),
    ("hidden_gate_score", TensorProto.FLOAT, [1, 1]),
    ("negative_adapter_location", TensorProto.FLOAT, [1, 14]),
    ("conditional_adapter_location", TensorProto.FLOAT, [1, 14]),
    ("raw_continuous_actions", TensorProto.FLOAT, [1, 14]),
)


def verify(item: dict[str, Any], name: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or t20.sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T134 frozen input changed: {name}={path}")


def inspection_session(path: Path) -> ort.InferenceSession:
    model = onnx.load(path)
    existing = {item.name for item in model.graph.output}
    for name, data_type, shape in OUTPUTS:
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(name, data_type, shape)
            )
    return ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"]
    )


def row_feed(row: dict[str, Any]) -> dict[str, np.ndarray]:
    return {
        "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
        "previous_action": np.asarray(
            row["policy_state_input"]["previous_action"], dtype=np.float32
        ),
        "h_in": np.asarray(
            row["policy_state_input"]["h_in"], dtype=np.float32
        ),
    }


def trace_rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def longest_true(values: list[bool]) -> int:
    longest = 0
    current = 0
    for value in values:
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest


def trace_summary(
    path: Path,
    session: ort.InferenceSession,
    *,
    reference: ort.InferenceSession | None,
) -> dict[str, Any]:
    gates: list[bool] = []
    scores: list[float] = []
    active_deltas: list[float] = []
    inactive_deltas: list[float] = []
    expert_magnitudes: list[float] = []
    for row in trace_rows(path):
        feed = row_feed(row)
        gate, score, expert, _conditional, raw = session.run(
            [item[0] for item in OUTPUTS], feed
        )
        active = bool(gate.reshape(-1)[0])
        gates.append(active)
        scores.append(float(score.reshape(-1)[0]))
        expert_magnitudes.append(float(np.max(np.abs(expert))))
        if reference is not None:
            source = reference.run(["raw_continuous_actions"], feed)[0]
            delta = float(np.max(np.abs(raw - source)))
            (active_deltas if active else inactive_deltas).append(delta)
    values = np.asarray(scores, dtype=float)
    return {
        "rows": len(gates),
        "gate_ticks": sum(gates),
        "gate_fraction": sum(gates) / len(gates),
        "first_gate_tick": next(
            (index for index, value in enumerate(gates) if value), None
        ),
        "longest_gate_run_ticks": longest_true(gates),
        "score": {
            "minimum": float(values.min()),
            "p95": float(np.quantile(values, 0.95)),
            "maximum": float(values.max()),
        },
        "maximum_expert_abs": max(expert_magnitudes),
        "maximum_source_delta_gate_active": max(
            active_deltas, default=0.0
        ),
        "maximum_source_delta_gate_inactive": max(
            inactive_deltas, default=0.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T134 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T134: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T134 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T134_T129_NOMINAL_GATE_ATTRIBUTION"
        or prereg["failed_checks"]
        or t20.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T134 preregistration changed")
    for name, item in prereg["sources"].items():
        verify(item, name)
    for name, item in prereg["graphs"].items():
        verify(item, name)

    t132 = json.loads(
        Path(prereg["sources"]["t132_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t97 = json.loads(
        Path(prereg["sources"]["t97_population"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    half = inspection_session(
        Path(prereg["graphs"]["t129_half_hard"]["path"])
    )
    final = inspection_session(
        Path(prereg["graphs"]["t129_final_hard"]["path"])
    )
    source = inspection_session(
        Path(prereg["graphs"]["t100c_half_hard"]["path"])
    )

    traces = []
    for block in t132["blocks"]:
        verify(block["manifest"], f"manifest:{block['checkpoint_id']}:{block['fit_id']}")
        manifest = json.loads(
            Path(block["manifest"]["path"]).read_text(encoding="utf-8")
        )
        for item in manifest["traces"]:
            verify(item, f"trace:{item['path']}")
            path = Path(item["path"])
            command = float(path.name.split("_seed", 1)[0][1:])
            checkpoint = (
                "half" if "HALF" in block["checkpoint_id"] else "final"
            )
            traces.append(
                {
                    "checkpoint": checkpoint,
                    "fit_id": block["fit_id"],
                    "command_x_m_s": command,
                    "trace": item,
                    "summary": trace_summary(
                        path,
                        half if checkpoint == "half" else final,
                        reference=source if checkpoint == "half" else None,
                    ),
                }
            )

    early = {"nominal": [], "com_x_negative": []}
    for item in t97["traces"]:
        verify(item["trace"], f"t97:{item['trace']['path']}")
        wanted = {8, 16, 32}
        for row in trace_rows(Path(item["trace"]["path"])):
            tick = int(row["tick"])
            if tick in wanted:
                score = source.run(
                    ["hidden_gate_score"], row_feed(row)
                )[0]
                early[item["population"]].append(
                    float(score.reshape(-1)[0])
                )
            if tick >= 32:
                break
    early_summary = {
        population: {
            "rows": len(values),
            "minimum": min(values),
            "maximum": max(values),
            "median": float(np.median(values)),
        }
        for population, values in early.items()
    }
    early_margin = (
        early_summary["com_x_negative"]["minimum"]
        - early_summary["nominal"]["maximum"]
    )
    moving = [row for row in traces if row["command_x_m_s"] > 0.0]
    x0 = [row for row in traces if row["command_x_m_s"] == 0.0]
    half_rows = [row for row in traces if row["checkpoint"] == "half"]
    failed = next(
        row
        for block in t132["blocks"]
        for row in block["result"]["cells"]
        if not row["cell_green"]
    )
    failing_trace = next(
        row
        for row in traces
        if row["checkpoint"] == "half"
        and row["fit_id"] == "p30"
        and row["command_x_m_s"] == 0.08
    )
    thresholds = prereg["thresholds"]
    checks = {
        "t132_sole_failure_exact": (
            t132["status"] == "HOLD_T132B_T129_NOMINAL_MATRIX"
            and t132["condition"]["green_cells"] == 15
            and failed["command_x_m_s"] == 0.08
        ),
        "all_nominal_moving_traces_false_activate": (
            len(moving) == 12
            and all(row["summary"]["gate_ticks"] > 0 for row in moving)
        ),
        "x0_never_activates": (
            len(x0) == 4
            and all(row["summary"]["gate_ticks"] == 0 for row in x0)
        ),
        "gate_off_source_identity_exact": all(
            row["summary"]["maximum_source_delta_gate_inactive"] == 0.0
            for row in half_rows
        ),
        "gate_on_expert_effect_material": (
            max(
                row["summary"]["maximum_source_delta_gate_active"]
                for row in half_rows
            )
            >= thresholds["minimum_gate_active_source_delta"]
        ),
        "failing_trace_uses_expert": (
            failing_trace["summary"]["gate_ticks"] > 0
            and failing_trace["summary"][
                "maximum_source_delta_gate_active"
            ]
            >= thresholds["minimum_gate_active_source_delta"]
        ),
        "early_condition_score_separable": (
            len(early["nominal"]) == 36
            and len(early["com_x_negative"]) == 36
            and early_margin >= thresholds["minimum_early_score_margin"]
        ),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    passed = not failed_checks
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t134_t129_nominal_gate_attribution_result.v1"
        ),
        "status": (
            "PASS_T134_T129_NOMINAL_GATE_ATTRIBUTION"
            if passed
            else "HOLD_T134_T129_NOMINAL_GATE_ATTRIBUTION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "DYNAMIC_GATE_FALSE_POSITIVE_EXPOSES_NEGATIVE_EXPERT"
            if passed
            else "UNRESOLVED_NOMINAL_FAILURE"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "traces": traces,
        "early_score": {
            **early_summary,
            "negative_min_minus_nominal_max": early_margin,
        },
        "failing_trace": failing_trace,
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "trace_rows": sum(row["summary"]["rows"] for row in traces),
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "calibration_context_router_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T134 T129 nominal-gate attribution result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Moving nominal false activations: "
        f"`{sum(row['summary']['gate_ticks'] > 0 for row in moving)}/12`\n"
        f"- Early condition-score margin: `{early_margin:.9f}`\n"
        "- Simulator / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
