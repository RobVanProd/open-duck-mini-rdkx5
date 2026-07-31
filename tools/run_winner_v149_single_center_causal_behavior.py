#!/usr/bin/env python3
"""Run V149's one-cell causal behavior test for the V148 local residual."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v141_projected_final_behavior import (  # noqa: E402
    load_evaluator,
    run_cell,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v149_single_center_causal_behavior_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v149_single_center_causal_behavior_result.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_RESULT_20260725.md"
)
CENTER_TICK = 394
CENTER_JOINT = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def local_gate(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    model = onnx.load(path)
    values = {
        initializer.name: numpy_helper.to_array(initializer)
        for initializer in model.graph.initializer
        if initializer.name
        in {"v148_center", "v148_scale", "v148_radius_squared"}
    }
    center = np.asarray(values["v148_center"], dtype=np.float64)
    scale = np.asarray(values["v148_scale"], dtype=np.float64)
    radius_squared = float(
        np.asarray(values["v148_radius_squared"]).reshape(-1)[0]
    )
    obs = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
    hidden = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in rows],
        dtype=np.float64,
    )
    features = np.concatenate([obs, hidden], axis=1)
    distance = np.sum(
        np.square((features - center) * scale),
        axis=1,
    )
    active = np.flatnonzero(distance <= radius_squared)
    return {
        "active_ticks": active.tolist(),
        "center_distance_squared": float(distance[CENTER_TICK]),
        "minimum_distance_squared": float(np.min(distance)),
        "radius_squared": radius_squared,
    }


def causal_contract(
    *,
    candidate_trace: Path,
    source_trace: Path,
    local_raw: Path,
) -> dict[str, Any]:
    source = load_rows(source_trace)
    candidate = load_rows(candidate_trace)
    source_action = np.asarray(
        [row["action"] for row in source], dtype=np.float32
    )
    candidate_action = np.asarray(
        [row["action"] for row in candidate], dtype=np.float32
    )
    source_obs = np.asarray(
        [row["obs_state"] for row in source], dtype=np.float32
    )
    candidate_obs = np.asarray(
        [row["obs_state"] for row in candidate], dtype=np.float32
    )
    source_hidden = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in source],
        dtype=np.float32,
    )
    candidate_hidden = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in candidate],
        dtype=np.float32,
    )
    delta = candidate_action[CENTER_TICK] - source_action[CENTER_TICK]
    changed_joints = np.flatnonzero(np.abs(delta) > 1.0e-7)
    oracle = source[CENTER_TICK]["exact_torque_oracle"]
    target = np.asarray(oracle["final_action"], dtype=np.float32)
    gate = local_gate(local_raw, candidate)
    checks = {
        "both_traces_complete_600": (
            len(source) == 600 and len(candidate) == 600
        ),
        "state_prefix_through_center_exact": (
            np.array_equal(
                source_obs[: CENTER_TICK + 1],
                candidate_obs[: CENTER_TICK + 1],
            )
            and np.array_equal(
                source_hidden[: CENTER_TICK + 1],
                candidate_hidden[: CENTER_TICK + 1],
            )
        ),
        "action_prefix_before_center_bit_exact": np.array_equal(
            source_action[:CENTER_TICK],
            candidate_action[:CENTER_TICK],
        ),
        "center_changes_only_right_ankle": (
            changed_joints.tolist() == [CENTER_JOINT]
        ),
        "center_matches_exact_oracle": (
            float(
                np.max(
                    np.abs(candidate_action[CENTER_TICK] - target)
                )
            )
            <= 1.0e-7
        ),
        "local_gate_fires_only_at_center": (
            gate["active_ticks"] == [CENTER_TICK]
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "center_tick": CENTER_TICK,
        "center_joint": CENTER_JOINT,
        "center_action_delta": delta.tolist(),
        "center_action_linf_to_oracle": float(
            np.max(np.abs(candidate_action[CENTER_TICK] - target))
        ),
        "state_prefix_obs_linf": float(
            np.max(
                np.abs(
                    source_obs[: CENTER_TICK + 1]
                    - candidate_obs[: CENTER_TICK + 1]
                )
            )
        ),
        "state_prefix_hidden_linf": float(
            np.max(
                np.abs(
                    source_hidden[: CENTER_TICK + 1]
                    - candidate_hidden[: CENTER_TICK + 1]
                )
            )
        ),
        "gate": gate,
        "source_trace": {
            "path": str(source_trace),
            "sha256": sha256(source_trace),
        },
        "candidate_trace": {
            "path": str(candidate_trace),
            "sha256": sha256(candidate_trace),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V149: {path}")
    evaluator_root = args.evaluator_root.resolve()
    shadow_trace = args.shadow_trace.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v148["artifact"]["deployed"]["path"])
    local_raw = Path(v148["artifact"]["raw"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v141_behavior_result": sha256(V141_RESULT),
        "v148_residual_result": sha256(V148_RESULT),
        "v126_preregistration": sha256(V126_PREREG),
        "v141_runner": sha256(
            TOOLS / "run_winner_v141_projected_final_behavior.py"
        ),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "local_raw": sha256(local_raw),
        "shadow_trace": sha256(shadow_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v148.get("decision")
        != "EARN_ONE_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION"
    ):
        raise ValueError("V149 preregistration changed")
    row = prereg["matrix"]["row"]
    evaluator = load_evaluator(evaluator_path)
    playground = Path(
        json.loads(
            V126_PREREG.read_text(encoding="utf-8")
        )["external_inputs"]["playground"]
    )
    run_root.mkdir(parents=True)
    trace_path = run_root / "v149_p30_x0.074_seed167931544.jsonl"
    cell = run_cell(
        evaluator=evaluator,
        row=row,
        policy=policy,
        playground=playground,
        base_prereg=base_prereg,
        trace_path=trace_path,
        cpu_only=(
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
    )
    causal = causal_contract(
        candidate_trace=trace_path,
        source_trace=shadow_trace,
        local_raw=local_raw,
    )
    checks = {
        "cell_all_frozen_gates_pass": bool(cell["pass"]),
        "torque_event_removed": bool(
            cell["torque_gate"]["worst_peak_torque_nm"] <= 1.91229675
        ),
        "causal_contract_green": not causal["failed_checks"],
        "one_cell_only": True,
        "cpu_only": bool(cell["metrics"]["checks"]["cpu_only"]),
        "no_training_hosted_compute_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v149.single_center_causal_behavior_result.v1"
        ),
        "status": (
            "PASS_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "cell": cell,
        "causal_contract": causal,
        "decision": (
            "EARN_V150_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
            if not failed
            else "CLOSE_SINGLE_CENTER_LOCAL_RESIDUAL"
        ),
        "authority": {
            "full_matrix_preregistration": not failed,
            "additional_behavior": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V149 single-center causal behavior\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Peak torque: "
        f"`{cell['torque_gate']['worst_peak_torque_nm']}` N.m.\n"
        f"- Local-gate ticks: "
        f"`{causal['gate']['active_ticks']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- One CPU-only behavior cell; no training, Colab, deployment, "
        "or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
