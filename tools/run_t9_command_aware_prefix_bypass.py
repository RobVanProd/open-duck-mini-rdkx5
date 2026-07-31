#!/usr/bin/env python3
"""Run the preregistered T9 command-aware x=0 prefix-bypass screen."""

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
PREREG = ANALYSIS / "t9_command_aware_prefix_bypass_preregistration.json"
RESULT = ANALYSIS / "t9_command_aware_prefix_bypass_result.json"
MARKDOWN = ANALYSIS / "T9_COMMAND_AWARE_PREFIX_BYPASS_RESULT_20260726.md"
DEFAULT_CACHE_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t9_command_aware_prefix_bypass_v1"
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
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T9 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if value.get("status") != "PREREGISTERED_T9_COMMAND_AWARE_PREFIX_BYPASS":
        raise RuntimeError("T9 preregistration status changed")
    basis = {
        key: value[key]
        for key in (
            "question",
            "causal_basis",
            "repository_inputs",
            "playground",
            "candidate",
            "matrix",
            "bypass_contract",
            "behavior_contract",
            "protection_contract",
            "reused_t8_evidence",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    if canonical_sha256(basis) != value["preregistered_contract_sha256"]:
        raise RuntimeError("T9 preregistration canonical hash changed")
    for label, frozen in value["repository_inputs"].items():
        verify_receipt(frozen, label)
    for checkpoint in value["candidate"]["checkpoints"]:
        verify_receipt(
            checkpoint["wrapped"], f"{checkpoint['checkpoint_id']}:wrapped"
        )
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"][
        "required_file_sha256"
    ].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T9 Playground input changed: {relative}")
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
        "bypass_contract": prereg["bypass_contract"],
    }


def block_dir(
    cache_root: Path, checkpoint_id: str, fit_id: str
) -> Path:
    return cache_root / checkpoint_id / fit_id


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
    for key in ("evaluation", "trace", "stdout"):
        verify_receipt(value[key], f"cached:{key}")
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
            f"T9 block exists without a valid manifest: {directory}"
        )
    directory.mkdir(parents=True)
    policy = Path(checkpoint["wrapped"]["path"])
    trace_path = (
        directory
        / f"x0.000_seed{prereg['matrix']['seed']}_{policy.stem}.jsonl"
    )
    evaluation_path = directory / "evaluation.json"
    stdout_path = directory / "stdout.log"
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
        "--seed",
        str(prereg["matrix"]["seed"]),
        "--duration-s",
        str(
            prereg["matrix"]["duration_ticks"]
            / prereg["matrix"]["frequency_hz"]
        ),
        "--trace-jsonl",
        str(trace_path),
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
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or not trace_path.is_file()
    ):
        raise RuntimeError(
            "T9 worker failed: "
            f"returncode={completed.returncode}; log={stdout_path}"
        )
    manifest = {
        "schema_version": "open_duck.t9_x0_prefix_bypass_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation": receipt(evaluation_path),
        "trace": receipt(trace_path),
        "stdout": receipt(stdout_path),
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    return manifest, False


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def exact_readback(run: dict[str, Any]) -> bool:
    report = run.get("dynamics_override") or {}
    readback = report.get("readback") or {}
    before = np.asarray(readback.get("before"), dtype=np.float64)
    after = np.asarray(readback.get("after"), dtype=np.float64)
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [0.0, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and before.shape == after.shape == (3,)
        and np.array_equal(before, after)
    )


def bypass_checks(
    run: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, bool]:
    fitted = (run.get("modes") or {}).get("fitted") or {}
    audit = fitted.get("response_calibration") or {}
    zero_context_sha = hashlib.sha256(
        np.zeros((1, 64), dtype=np.float32).tobytes()
    ).hexdigest()
    observations = np.asarray(
        [row["obs_state"] for row in rows], dtype=np.float32
    )
    applied = np.asarray(
        [row["applied_target_rad"] for row in rows], dtype=np.float32
    )
    previous_in = np.asarray(
        [
            row["policy_state_input"]["previous_action"][0]
            for row in rows
        ],
        dtype=np.float32,
    )
    previous_out = np.asarray(
        [
            row["policy_state_output"]["previous_action_out"][0]
            for row in rows
        ],
        dtype=np.float32,
    )
    hidden_in = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in rows],
        dtype=np.float32,
    )
    hidden_out = np.asarray(
        [row["policy_state_output"]["h_out"][0] for row in rows],
        dtype=np.float32,
    )
    actions = np.asarray([row["action"] for row in rows], dtype=np.float32)
    return {
        "prefix_disabled": audit.get("enabled") is False
        and audit.get("calibration_ticks") == 0
        and audit.get("home_return_ticks") == 0,
        "zero_context_bypass_enabled": audit.get("zero_context_bypass")
        is True,
        "zero_context_exact": audit.get("context_sha256")
        == zero_context_sha,
        "context_shape_and_finite": audit.get("context_shape") == [1, 64]
        and audit.get("context_finite") is True,
        "phase_reset_exact": audit.get("locomotion_phase_reset")
        == [1.0, 0.0],
        "initial_hidden_zero": audit.get("locomotion_hidden_exact_zero")
        is True
        and bool(rows)
        and np.count_nonzero(hidden_in[0]) == 0,
        "initial_previous_action_zero": audit.get(
            "locomotion_previous_action_exact_zero"
        )
        is True
        and bool(rows)
        and np.count_nonzero(previous_in[0]) == 0,
        "applied_target_observer_exact": audit.get(
            "applied_target_observation_matches_bridge"
        )
        is True,
        "actions_exact_zero": actions.shape == (len(rows), 14)
        and np.count_nonzero(actions) == 0,
        "recurrent_chains_exact": bool(rows)
        and np.array_equal(previous_in[1:], previous_out[:-1])
        and np.array_equal(hidden_in[1:], hidden_out[:-1]),
        "context_immutable": all(
            row.get("policy_calibration_context_sha256")
            == zero_context_sha
            for row in rows
        ),
        "graph_authoritative_no_host_delta": bool(rows)
        and all(
            row.get("policy_graph_authoritative_output") is True
            and row.get("policy_host_action_delta_max_abs") == 0.0
            for row in rows
        ),
        "full_observation_traced": observations.shape
        == (len(rows), 115),
        "applied_target_slot_continuity": observations.shape
        == (len(rows), 115)
        and applied.shape == (len(rows), 14)
        and (
            len(rows) <= 1
            or np.array_equal(observations[1:, 83:97], applied[:-1])
        ),
    }


def extract_block(
    prereg: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    evaluation = json.loads(
        Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
    )
    run = evaluation["run"]
    rows = read_trace(Path(manifest["trace"]["path"]))
    behavior = classify_behavior(
        behavior_row(run), prereg["behavior_contract"]
    )
    protection = trace_summary(
        Path(manifest["trace"]["path"]),
        prereg["protection_contract"],
    )
    checks = bypass_checks(run, rows)
    trace_valid = (
        protection["ticks_contiguous_from_zero"]
        and protection["rows"] == behavior["samples"]
        and len(rows) == prereg["matrix"]["duration_ticks"]
    )
    readback = exact_readback(run)
    worker_inputs = evaluation.get("inputs") or {}
    inputs_exact = (
        worker_inputs.get("command_x_m_s") == 0.0
        and worker_inputs.get("calibration_ticks") == 0
        and worker_inputs.get("home_return_ticks") == 0
        and worker_inputs.get("zero_context_bypass") is True
        and worker_inputs.get("policy_state_input_names")
        == ["h_in", "previous_action"]
        and worker_inputs.get("policy_state_output_names")
        == ["h_out", "previous_action_out"]
        and worker_inputs.get("policy_context_input_name")
        == "calibration_context"
    )
    green = (
        trace_valid
        and readback
        and inputs_exact
        and behavior["core_pass"]
        and behavior["replacement_quality_pass"]
        and protection["duration_protection_pass"]
        and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
        and all(checks.values())
    )
    return {
        "worker_inputs_exact": inputs_exact,
        "trace_valid": trace_valid,
        "nominal_com_readback_exact": readback,
        "behavior": behavior,
        "protection": protection,
        "bypass_checks": checks,
        "cell_green": green,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# T9 command-aware x=0 prefix-bypass result",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        f"- New x=0 cells: `{payload['new_passing_cells']}/4`",
        f"- Combined cells: `{payload['combined_passing_cells']}/16`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "| checkpoint | fit | green | tracking p95 | rate excess | "
        "overcurrent run | overload run |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for block in payload["blocks"]:
        cell = block["cell"]
        lines.append(
            f"| `{block['checkpoint_id']}` | `{block['fit_id']}` | "
            f"`{cell['cell_green']}` | "
            f"{cell['behavior']['pitch_tracking_p95_rad']} | "
            f"{cell['protection']['maximum_full_measured_vector_excess_rad_s']} | "
            f"{cell['protection']['worst_strict_overcurrent_run_ticks']} | "
            f"{cell['protection']['worst_strict_overload_run_ticks']} |"
        )
    lines.extend(
        [
            "",
            "T9 changes only startup orchestration: paused/x=0 begins directly "
            "from home with immutable zero context and no response excitation. "
            "The V121 graph, exact-zero deadband, action/history/applied-target "
            "semantics, dynamics, and gates are unchanged. The twelve audited "
            "T8 moving cells are reused without rerunning.",
            "",
            "A pass earns only the separately preregistered response-conditioned "
            "continuation CPU software contract. It does not authorize hosted "
            "training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, "
            "or grounded replay.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T9 requires --execute after preregistration review")
    prereg = load_preregistration()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T9 result")
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    blocks = []
    new_blocks = 0
    cache_hits = 0
    for checkpoint in prereg["candidate"]["checkpoints"]:
        for fit_id in prereg["matrix"]["fits"]:
            manifest, cached = run_or_load_block(
                prereg, checkpoint, fit_id, cache_root
            )
            cache_hits += int(cached)
            new_blocks += int(not cached)
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
                    "cell": extract_block(prereg, manifest),
                }
            )
    new_green = sum(block["cell"]["cell_green"] for block in blocks)
    reused = prereg["reused_t8_evidence"]["green_moving_cells"]
    combined = new_green + reused
    passed = len(blocks) == 4 and new_green == 4 and combined == 16
    status = (
        "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
        if passed
        else "HOLD_T9_COMMAND_AWARE_PREFIX_BYPASS"
    )
    decision = (
        "EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT"
        if passed
        else "CLOSE_COMMAND_AWARE_PREFIX_BYPASS_WITHOUT_TRAINING"
    )
    basis = {
        "schema_version": "open_duck.t9_command_aware_prefix_bypass_result.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "new_expected_cells": 4,
        "new_completed_cells": len(blocks),
        "new_passing_cells": new_green,
        "reused_t8_moving_cells": reused,
        "combined_expected_cells": 16,
        "combined_passing_cells": combined,
        "new_blocks": new_blocks,
        "cache_hits": cache_hits,
        "cache_root": str(cache_root),
        "blocks": blocks,
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
    print(f"new_cells={new_green}/4")
    print(f"combined_cells={combined}/16")
    print(f"result_sha256={payload['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
