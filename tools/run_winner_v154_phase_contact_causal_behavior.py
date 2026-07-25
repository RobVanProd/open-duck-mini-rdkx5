#!/usr/bin/env python3
"""Run V154's one-cell phase/contact causal behavior test."""

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
    / "winner_v154_phase_contact_causal_behavior_preregistration.json"
)
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V153_RESULT = ANALYSIS / "winner_v153_phase_contact_residual_result.json"
OUTPUT = ANALYSIS / "winner_v154_phase_contact_causal_behavior_result.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_RESULT_20260725.md"
)
RIGHT_ANKLE = 13


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


def gate_from_graph(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    model = onnx.load(path)
    values = {
        initializer.name: numpy_helper.to_array(initializer)
        for initializer in model.graph.initializer
        if initializer.name
        in {
            "v153_phase",
            "v153_contact",
            "v153_phase_radius_squared",
            "v153_correction",
        }
    }
    phase = np.asarray(values["v153_phase"], dtype=np.float64)
    contact = np.asarray(values["v153_contact"], dtype=np.float64)
    radius_squared = float(
        np.asarray(values["v153_phase_radius_squared"]).reshape(-1)[0]
    )
    correction = np.asarray(
        values["v153_correction"], dtype=np.float32
    ).reshape(-1)
    obs = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
    phase_distance = np.sum(
        np.square(obs[:, 99:101] - phase), axis=1
    )
    active = (
        (phase_distance <= radius_squared)
        & np.all(obs[:, 97:99] == contact, axis=1)
    )
    return {
        "active_ticks": np.flatnonzero(active).tolist(),
        "phase": phase.reshape(-1).tolist(),
        "contact": contact.reshape(-1).tolist(),
        "radius_squared": radius_squared,
        "correction": correction.tolist(),
    }


def causal_contract(
    *,
    candidate_trace: Path,
    source_trace: Path,
    local_raw: Path,
) -> dict[str, Any]:
    source = load_rows(source_trace)
    candidate = load_rows(candidate_trace)
    gate = gate_from_graph(local_raw, candidate)
    active = gate["active_ticks"]
    first_tick = int(active[0]) if active else -1
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
    first_delta = candidate_action[first_tick] - source_action[first_tick]
    changed_joints = np.flatnonzero(np.abs(first_delta) > 1.0e-7)
    correction = float(gate["correction"][RIGHT_ANKLE])
    checks = {
        "both_traces_complete_600": (
            len(source) == len(candidate) == 600
        ),
        "first_activation_is_phase43_right_support": (
            first_tick == 43
            and candidate[first_tick]["foot_contacts"] == [0, 1]
        ),
        "state_prefix_through_first_activation_exact": (
            np.array_equal(
                source_obs[: first_tick + 1],
                candidate_obs[: first_tick + 1],
            )
            and np.array_equal(
                source_hidden[: first_tick + 1],
                candidate_hidden[: first_tick + 1],
            )
        ),
        "action_prefix_before_first_activation_bit_exact": np.array_equal(
            source_action[:first_tick],
            candidate_action[:first_tick],
        ),
        "first_activation_changes_only_right_ankle": (
            changed_joints.tolist() == [RIGHT_ANKLE]
        ),
        "first_activation_uses_frozen_correction": (
            abs(float(first_delta[RIGHT_ANKLE]) - correction) <= 5.0e-7
        ),
        "gate_remains_27_tick_periodic": (
            len(active) == 21
            and active[0] == 43
            and active[-1] == 583
            and set(np.diff(active).tolist()) == {27}
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "first_activation_tick": first_tick,
        "first_action_delta": first_delta.tolist(),
        "state_prefix_obs_linf": float(
            np.max(
                np.abs(
                    source_obs[: first_tick + 1]
                    - candidate_obs[: first_tick + 1]
                )
            )
        ),
        "state_prefix_hidden_linf": float(
            np.max(
                np.abs(
                    source_hidden[: first_tick + 1]
                    - candidate_hidden[: first_tick + 1]
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
    parser.add_argument("--source-trace", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V154: {path}")
    evaluator_root = args.evaluator_root.resolve()
    source_trace = args.source_trace.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v153 = json.loads(V153_RESULT.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v153["artifact"]["deployed"]["path"])
    local_raw = Path(v153["artifact"]["raw"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v141_result": sha256(V141_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v153_result": sha256(V153_RESULT),
        "v141_runner": sha256(
            TOOLS / "run_winner_v141_projected_final_behavior.py"
        ),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "local_raw": sha256(local_raw),
        "source_trace": sha256(source_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v153.get("decision")
        != "EARN_ONE_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_PREREGISTRATION"
    ):
        raise ValueError("V154 preregistration changed")
    row = prereg["matrix"]["row"]
    evaluator = load_evaluator(evaluator_path)
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    run_root.mkdir(parents=True)
    trace_path = run_root / "v154_p30_x0.074_seed167931544.jsonl"
    cell = run_cell(
        evaluator=evaluator,
        row=row,
        policy=policy,
        playground=Path(v126["external_inputs"]["playground"]),
        base_prereg=base_prereg,
        trace_path=trace_path,
        cpu_only=(
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
    )
    causal = causal_contract(
        candidate_trace=trace_path,
        source_trace=source_trace,
        local_raw=local_raw,
    )
    checks = {
        "cell_all_frozen_gates_pass": bool(cell["pass"]),
        "torque_gate_green": bool(
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
            "winner_v154.phase_contact_causal_behavior_result.v1"
        ),
        "status": (
            "PASS_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "cell": cell,
        "causal_contract": causal,
        "decision": (
            "EARN_V155_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
            if not failed
            else "CLOSE_PHASE_CONTACT_RESIDUAL"
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
        "# Winner V154 phase/contact causal behavior\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Peak torque: "
        f"`{cell['torque_gate']['worst_peak_torque_nm']}` N.m.\n"
        f"- Gate ticks: `{causal['gate']['active_ticks']}`.\n"
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
