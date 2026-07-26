#!/usr/bin/env python3
"""Run the preregistered T8 zero-training state-coherent handoff screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np

from run_t6_corrected_robustness_screen import (
    behavior_row,
    classify_behavior,
    trace_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
MARKDOWN = ANALYSIS / "T8_STATE_COHERENT_HANDOFF_RESULT_20260726.md"
DEFAULT_CACHE_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t8_state_coherent_handoff_v1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T8 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if value.get("status") != "PREREGISTERED_T8_STATE_COHERENT_HANDOFF":
        raise RuntimeError("T8 preregistration status changed")
    basis = {
        key: value[key]
        for key in (
            "question",
            "causal_basis",
            "repository_inputs",
            "playground",
            "assets",
            "calibrator",
            "candidate",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    if canonical_sha256(basis) != value["preregistered_contract_sha256"]:
        raise RuntimeError("T8 preregistration canonical hash changed")
    for label, value_receipt in value["repository_inputs"].items():
        verify_receipt(value_receipt, label)
    verify_receipt(value["assets"]["manifest"], "asset_manifest")
    manifest = json.loads(
        Path(value["assets"]["manifest"]["path"]).read_text(encoding="utf-8")
    )
    manifest_basis = {
        key: item for key, item in manifest.items() if key != "manifest_sha256"
    }
    if (
        canonical_sha256(manifest_basis) != manifest["manifest_sha256"]
        or manifest["manifest_sha256"]
        != value["assets"]["manifest_canonical_sha256"]
    ):
        raise RuntimeError("T8 asset manifest changed")
    for policy in value["candidate"]["checkpoints"]:
        verify_receipt(policy["source"], f"{policy['checkpoint_id']}:source")
        verify_receipt(policy["wrapped"], f"{policy['checkpoint_id']}:wrapped")
    verify_receipt(value["calibrator"], "calibrator")
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"][
        "required_file_sha256"
    ].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T8 Playground input changed: {relative}")
    for label, manifest_receipt in value["playground"][
        "composition_manifests"
    ].items():
        verify_receipt(manifest_receipt, f"playground:{label}")
    return value


def block_contract(
    prereg: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
) -> dict[str, Any]:
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checkpoint": checkpoint,
        "fit_id": fit_id,
        "fit": prereg["repository_inputs"][f"fit_{fit_id}"],
        "matrix": prereg["matrix"],
        "handoff_contract": prereg["handoff_contract"],
        "assets_manifest_sha256": prereg["assets"][
            "manifest_canonical_sha256"
        ],
    }


def block_dir(
    cache_root: Path, checkpoint_id: str, fit_id: str
) -> Path:
    return cache_root / checkpoint_id / fit_id


def trace_paths(
    directory: Path,
    policy: Path,
    matrix: dict[str, Any],
) -> list[Path]:
    return [
        directory
        / "traces"
        / (
            f"x{float(command):.3f}_seed{matrix['seed']}_"
            f"{policy.stem}.jsonl"
        )
        for command in matrix["commands_x_m_s"]
    ]


def load_cached_manifest(
    path: Path, contract: dict[str, Any]
) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("block_contract") != contract
        or value.get("block_contract_sha256") != canonical_sha256(contract)
    ):
        return None
    for key in ("evaluation", "stdout"):
        verify_receipt(value[key], f"cached:{key}")
    for index, item in enumerate(value["traces"]):
        verify_receipt(item, f"cached:trace:{index}")
    return value


def run_or_load_block(
    prereg: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
    cache_root: Path,
) -> tuple[dict[str, Any], bool]:
    contract = block_contract(prereg, checkpoint, fit_id)
    directory = block_dir(cache_root, checkpoint["checkpoint_id"], fit_id)
    manifest_path = directory / "manifest.json"
    cached = load_cached_manifest(manifest_path, contract)
    if cached is not None:
        return cached, True
    if directory.exists():
        raise RuntimeError(
            f"T8 block exists without a valid frozen manifest: {directory}"
        )
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    evaluation_path = directory / "evaluation.json"
    stdout_path = directory / "stdout.log"
    matrix = prereg["matrix"]
    policy = Path(checkpoint["wrapped"]["path"])
    command = [
        sys.executable,
        prereg["repository_inputs"]["worker"]["path"],
        "--policy",
        str(policy),
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["repository_inputs"][f"fit_{fit_id}"]["path"],
        "--reference-feature-table",
        prereg["repository_inputs"]["reference_features"]["path"],
        "--calibrator",
        prereg["calibrator"]["path"],
        "--calibrator-sha256",
        prereg["calibrator"]["sha256"],
        "--commands",
        ",".join(str(item) for item in matrix["commands_x_m_s"]),
        "--seed",
        str(matrix["seed"]),
        "--duration-s",
        str(matrix["duration_ticks"] / matrix["frequency_hz"]),
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation_path),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                cache_root.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    with stdout_path.open("w", encoding="utf-8") as stream:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2400,
            check=False,
        )
    traces = trace_paths(directory, policy, matrix)
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or any(not path.is_file() for path in traces)
    ):
        raise RuntimeError(
            "T8 worker failed: "
            f"returncode={completed.returncode}; log={stdout_path}"
        )
    manifest = {
        "schema_version": "open_duck.t8_state_coherent_handoff_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation": receipt(evaluation_path),
        "stdout": receipt(stdout_path),
        "traces": [receipt(path) for path in traces],
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    return manifest, False


def read_trace(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"invalid T8 trace row: {path}:{line_number}"
                ) from exc
    return records


def exact_nominal_com_readback(report: dict[str, Any] | None) -> bool:
    report = report or {}
    readback = report.get("readback") or {}
    before = np.asarray(readback.get("before"), dtype=np.float64)
    after = np.asarray(readback.get("after"), dtype=np.float64)
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [0.0, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and before.shape == (3,)
        and after.shape == (3,)
        and np.array_equal(after, before)
    )


def state_handoff_summary(
    run: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any]:
    fitted = (run.get("modes") or {}).get("fitted") or {}
    audit = fitted.get("response_calibration") or {}
    calibration_action = np.asarray(
        audit.get("calibration_final_action"), dtype=np.float32
    )
    observer_target = np.asarray(
        audit.get("observer_bridge_applied_target_rad"), dtype=np.float32
    )
    handoff_observation = np.asarray(
        audit.get("locomotion_applied_target_observation_rad"),
        dtype=np.float32,
    )
    previous_inputs = np.asarray(
        [
            row["policy_state_input"]["previous_action"][0]
            for row in records
        ],
        dtype=np.float32,
    )
    previous_outputs = np.asarray(
        [
            row["policy_state_output"]["previous_action_out"][0]
            for row in records
        ],
        dtype=np.float32,
    )
    hidden_inputs = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in records],
        dtype=np.float32,
    )
    hidden_outputs = np.asarray(
        [row["policy_state_output"]["h_out"][0] for row in records],
        dtype=np.float32,
    )
    observations = np.asarray(
        [row.get("obs_state") for row in records], dtype=np.float32
    )
    applied = np.asarray(
        [row["applied_target_rad"] for row in records], dtype=np.float32
    )
    expected_context_sha = audit.get("context_sha256")
    checks = {
        "response_enabled": audit.get("enabled") is True,
        "calibration_ticks_exact": audit.get("calibration_ticks") == 250,
        "zero_home_return_ticks": audit.get("home_return_ticks") == 0,
        "calibrator_sha_exact": (
            audit.get("calibrator_sha256")
            == run["response_calibration"]["calibrator_sha256"]
        ),
        "context_shape": audit.get("context_shape") == [1, 64],
        "context_finite": audit.get("context_finite") is True,
        "phase_reset_exact": audit.get("locomotion_phase_reset")
        == [1.0, 0.0],
        "policy_hidden_zero": audit.get("locomotion_hidden_exact_zero")
        is True,
        "previous_action_preserved": (
            audit.get("locomotion_previous_action_matches_calibration")
            is True
        ),
        "handoff_state_preserved": audit.get("handoff_state_preserved")
        is True,
        "applied_target_observer_preserved": (
            audit.get("applied_target_observation_matches_bridge") is True
            and observer_target.shape == (14,)
            and handoff_observation.shape == (14,)
            and np.array_equal(observer_target, handoff_observation)
        ),
        "full_observation_traced": (
            observations.ndim == 2 and observations.shape[1:] == (115,)
        ),
        "first_previous_action_matches_calibration": (
            bool(records)
            and calibration_action.shape == (14,)
            and previous_inputs.shape[1:] == (14,)
            and np.array_equal(previous_inputs[0], calibration_action)
        ),
        "first_hidden_zero": (
            bool(records)
            and hidden_inputs.shape[1:] == (64,)
            and np.count_nonzero(hidden_inputs[0]) == 0
        ),
        "recurrent_state_chains_exact": (
            bool(records)
            and np.array_equal(previous_inputs[1:], previous_outputs[:-1])
            and np.array_equal(hidden_inputs[1:], hidden_outputs[:-1])
        ),
        "context_immutable": (
            isinstance(expected_context_sha, str)
            and all(
                row.get("policy_calibration_context_sha256")
                == expected_context_sha
                for row in records
            )
        ),
        "graph_authoritative_no_host_delta": (
            bool(records)
            and all(
                row.get("policy_graph_authoritative_output") is True
                and row.get("policy_host_action_delta_max_abs") == 0.0
                for row in records
            )
        ),
        "applied_target_slot_continuity": (
            observations.ndim == 2
            and observations.shape[1:] == (115,)
            and applied.shape == (len(records), 14)
            and (
                len(records) <= 1
                or np.array_equal(
                    observations[1:, 83:97],
                    applied[:-1],
                )
            )
        ),
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "response_audit": audit,
        "context_sha256": expected_context_sha,
        "calibration_final_action": (
            None
            if calibration_action.shape != (14,)
            else calibration_action.astype(float).tolist()
        ),
        "observer_bridge_applied_target_rad": (
            None
            if observer_target.shape != (14,)
            else observer_target.astype(float).tolist()
        ),
    }


def extract_block(
    prereg: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    evaluation = json.loads(
        Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
    )
    expected_inputs = {
        "calibration_ticks": 250,
        "home_return_ticks": 0,
        "preserve_handoff_state": True,
        "expected_observation_dim": 115,
        "expected_action_dim": 14,
        "policy_state_input_names": ["previous_action", "h_in"],
        "policy_state_output_names": ["previous_action_out", "h_out"],
        "policy_context_input_name": "calibration_context",
        "policy_graph_authoritative_output": True,
        "policy_applied_target_observation": True,
        "reference_start_phase": 0,
        "eval_dynamics_override": {
            "torso_com_offset_m": [0.0, 0.0, 0.0]
        },
    }
    inputs = evaluation.get("inputs") or {}
    worker_inputs_exact = all(
        inputs.get(key) == expected for key, expected in expected_inputs.items()
    )
    runs = evaluation.get("runs") or []
    commands = [float(item) for item in prereg["matrix"]["commands_x_m_s"]]
    if [float(run["command_x"]) for run in runs] != commands:
        raise RuntimeError("T8 worker returned the wrong command order")
    rows = []
    for run, trace_receipt in zip(runs, manifest["traces"], strict=True):
        path = Path(trace_receipt["path"])
        records = read_trace(path)
        behavior = classify_behavior(
            behavior_row(run), prereg["behavior_contract"]
        )
        protection = trace_summary(path, prereg["protection_contract"])
        handoff = state_handoff_summary(run, records)
        trace_valid = (
            protection["ticks_contiguous_from_zero"]
            and protection["rows"] == behavior["samples"]
            and sha256(path) == trace_receipt["sha256"]
        )
        readback_exact = exact_nominal_com_readback(
            run.get("dynamics_override")
        )
        cell_green = (
            trace_valid
            and behavior["core_pass"]
            and behavior["replacement_quality_pass"]
            and protection["duration_protection_pass"]
            and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
            and handoff["all_checks_pass"]
            and readback_exact
        )
        rows.append(
            {
                "command_x_m_s": float(run["command_x"]),
                "behavior": behavior,
                "protection": protection,
                "handoff": handoff,
                "trace_valid": trace_valid,
                "nominal_com_readback_exact": readback_exact,
                "cell_green": cell_green,
            }
        )
    return {
        "worker_inputs_exact": worker_inputs_exact,
        "execution_platform": (evaluation.get("execution") or {}).get(
            "platform"
        ),
        "cells": rows,
        "block_green": (
            worker_inputs_exact
            and len(rows) == 4
            and all(item["cell_green"] for item in rows)
        ),
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# T8 state-coherent support-to-locomotion handoff result",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        f"- Cells: `{payload['passing_cells']}/{payload['expected_cells']}`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "| checkpoint | fit | green | worst tracking | min moving vx | "
        "overcurrent run | overload run |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for block in payload["blocks"]:
        cells = block["result"]["cells"]
        moving = [
            item for item in cells if item["command_x_m_s"] > 0.0
        ]
        lines.append(
            f"| `{block['checkpoint_id']}` | `{block['fit_id']}` | "
            f"{sum(item['cell_green'] for item in cells)}/4 | "
            f"{max(item['behavior']['pitch_tracking_p95_rad'] for item in cells)} | "
            f"{min(item['behavior']['mean_local_vx_m_s'] for item in moving)} | "
            f"{max(item['protection']['worst_strict_overcurrent_run_ticks'] for item in cells)} | "
            f"{max(item['protection']['worst_strict_overload_run_ticks'] for item in cells)} |"
        )
    lines.extend(
        [
            "",
            "T8 performs 250 unscored universal-support ticks and then starts "
            "the frozen V121 locomotion graph directly: no zero-action "
            "home-return interval, no optimizer update, and no behavior wrapper. "
            "The final support action, applied-target observer state, 64-D "
            "response context, and recurrent chains are audited at the boundary.",
            "",
            "A pass earns only the separately preregistered CPU software "
            "contract for a response-conditioned V121 continuation. It does not "
            "authorize hosted training, robot/RDK-X5 access, Gate 5, torque, "
            "motion, deployment, or grounded replay.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    parser.add_argument("--max-new-blocks", type=int, default=None)
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T8 requires --execute after preregistration review")
    prereg = load_preregistration()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T8 result")
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    blocks = []
    new_blocks = 0
    cache_hits = 0
    for checkpoint in prereg["candidate"]["checkpoints"]:
        for fit_id in prereg["matrix"]["fits"]:
            if (
                args.max_new_blocks is not None
                and new_blocks >= args.max_new_blocks
            ):
                raise RuntimeError(
                    "T8 partial execution has zero decision weight; resume the "
                    "exact preregistered matrix before classification"
                )
            manifest, cached = run_or_load_block(
                prereg, checkpoint, fit_id, cache_root
            )
            cache_hits += int(cached)
            new_blocks += int(not cached)
            result = extract_block(prereg, manifest)
            blocks.append(
                {
                    "checkpoint_id": checkpoint["checkpoint_id"],
                    "fit_id": fit_id,
                    "manifest": receipt(
                        block_dir(
                            cache_root,
                            checkpoint["checkpoint_id"],
                            fit_id,
                        )
                        / "manifest.json"
                    ),
                    "result": result,
                }
            )
    cells = [
        cell for block in blocks for cell in block["result"]["cells"]
    ]
    all_green = (
        len(blocks) == 4
        and len(cells) == prereg["matrix"]["total_cells"]
        and all(block["result"]["block_green"] for block in blocks)
        and all(cell["cell_green"] for cell in cells)
    )
    status = (
        "PASS_T8_STATE_COHERENT_HANDOFF"
        if all_green
        else "HOLD_T8_STATE_COHERENT_HANDOFF"
    )
    decision = (
        "EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT"
        if all_green
        else "CLOSE_DIRECT_STATE_COHERENT_V121_HANDOFF_WITHOUT_TRAINING"
    )
    basis = {
        "schema_version": "open_duck.t8_state_coherent_handoff_result.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "expected_cells": prereg["matrix"]["total_cells"],
        "completed_cells": len(cells),
        "passing_cells": sum(cell["cell_green"] for cell in cells),
        "new_blocks": new_blocks,
        "cache_hits": cache_hits,
        "cache_root": str(cache_root),
        "blocks": blocks,
        "summary": {
            "worst_tracking_p95_rad": max(
                cell["behavior"]["pitch_tracking_p95_rad"] for cell in cells
            ),
            "minimum_moving_vx_m_s": min(
                cell["behavior"]["mean_local_vx_m_s"]
                for cell in cells
                if cell["command_x_m_s"] > 0.0
            ),
            "worst_strict_overcurrent_run_ticks": max(
                cell["protection"]["worst_strict_overcurrent_run_ticks"]
                for cell in cells
            ),
            "worst_strict_overload_run_ticks": max(
                cell["protection"]["worst_strict_overload_run_ticks"]
                for cell in cells
            ),
            "all_handoff_contracts_pass": all(
                cell["handoff"]["all_checks_pass"] for cell in cells
            ),
        },
        "execution": {
            "platform": "cpu",
            "training_steps": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority"],
    }
    payload = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload)
    print(status)
    print(f"decision={decision}")
    print(f"cells={payload['passing_cells']}/{payload['expected_cells']}")
    print(f"result_sha256={payload['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
