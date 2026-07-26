#!/usr/bin/env python3
"""Run the preregistered T7 current-stack universal response-support screen."""

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


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t7_universal_response_support_preregistration.json"
RESULT = ANALYSIS / "t7_universal_response_support_result.json"
MARKDOWN = ANALYSIS / "T7_UNIVERSAL_RESPONSE_SUPPORT_RESULT_20260725.md"


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


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if value.get("status") != "PREREGISTERED_T7_UNIVERSAL_RESPONSE_SUPPORT":
        raise RuntimeError("T7 preregistration status changed")
    basis = {
        key: value[key]
        for key in (
            "repository_inputs",
            "playground",
            "frozen_policy",
            "causal_audit",
            "matrix",
            "behavior_contract",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    if canonical_sha256(basis) != value["preregistered_contract_sha256"]:
        raise RuntimeError("T7 preregistered contract hash mismatch")
    for name, receipt in value["repository_inputs"].items():
        path = Path(receipt["path"])
        if (
            not path.is_file()
            or path.stat().st_size != receipt["bytes"]
            or sha256(path) != receipt["sha256"]
        ):
            raise RuntimeError(f"T7 repository input changed: {name}={path}")
    policy = Path(value["frozen_policy"]["path"])
    if (
        not policy.is_file()
        or policy.stat().st_size != value["frozen_policy"]["bytes"]
        or sha256(policy) != value["frozen_policy"]["sha256"]
    ):
        raise RuntimeError("T7 frozen policy changed")
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"]["required_file_sha256"].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T7 Playground file changed: {relative}")
    for receipt in value["playground"]["composition_manifests"].values():
        path = Path(receipt["path"])
        if not path.is_file() or sha256(path) != receipt["sha256"]:
            raise RuntimeError(f"T7 composition manifest changed: {path}")
    return value


def graph_contract(prereg: dict[str, Any]) -> dict[str, Any]:
    import onnx
    import onnxruntime as ort

    path = Path(prereg["frozen_policy"]["path"])
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    observed_inputs = {item.name: item.shape for item in session.get_inputs()}
    observed_outputs = {item.name: item.shape for item in session.get_outputs()}
    if observed_inputs != prereg["frozen_policy"]["abi"]["inputs"]:
        raise RuntimeError(f"T7 graph input ABI changed: {observed_inputs}")
    if observed_outputs != prereg["frozen_policy"]["abi"]["outputs"]:
        raise RuntimeError(f"T7 graph output ABI changed: {observed_outputs}")
    model = onnx.load(path)
    initializers = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item), dtype=np.float32)
        for item in model.graph.initializer
    }
    maximum_delta = initializers.get("cal_max_action_delta")
    if maximum_delta is None or maximum_delta.shape != (1, 14):
        raise RuntimeError("T7 graph cal_max_action_delta changed")
    target = np.asarray(
        prereg["frozen_policy"]["universal_raw_action"], dtype=np.float32
    )[None, :]
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    chain = []
    for tick in range(8):
        observation = np.random.Generator(np.random.PCG64(tick)).normal(
            size=(1, 115)
        ).astype(np.float32)
        action, previous_out, hidden = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
            },
        )
        lower = np.maximum(previous - maximum_delta, -1.0)
        upper = np.minimum(previous + maximum_delta, 1.0)
        expected = np.maximum(np.minimum(target, upper), lower)
        if not np.array_equal(action, expected) or not np.array_equal(
            previous_out, action
        ):
            raise RuntimeError("T7 graph universal-target chain changed")
        chain.append(action[0].astype(float).tolist())
        previous = previous_out
    return {
        "inputs": observed_inputs,
        "outputs": observed_outputs,
        "maximum_action_delta": maximum_delta[0].astype(float).tolist(),
        "maximum_action_delta_sha256": array_sha256(maximum_delta),
        "first_eight_actions": chain,
        "chain_exact": True,
    }


def longest_true_run_per_joint(mask: np.ndarray) -> list[int]:
    if mask.ndim != 2 or mask.shape[1] != 14:
        raise ValueError(f"unexpected protection mask shape: {mask.shape}")
    longest = np.zeros(14, dtype=np.int64)
    current = np.zeros(14, dtype=np.int64)
    for row in mask:
        current = np.where(row, current + 1, 0)
        longest = np.maximum(longest, current)
    return longest.astype(int).tolist()


def read_trace(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid T7 trace row {path}:{line_number}") from exc
            records.append(record)
    return records


def block_contract(
    prereg: dict[str, Any],
    configuration: dict[str, Any],
    fit_id: str,
    repeat: int,
) -> dict[str, Any]:
    return {
        "preregistered_contract_sha256": prereg["preregistered_contract_sha256"],
        "configuration": configuration,
        "fit_id": fit_id,
        "repeat": repeat,
        "command_x_m_s": prereg["matrix"]["command_x_m_s"],
        "seed": prereg["matrix"]["seed"],
        "duration_ticks": prereg["matrix"]["duration_ticks"],
        "policy_sha256": prereg["frozen_policy"]["sha256"],
    }


def block_directory(
    cache_root: Path,
    configuration: dict[str, Any],
    fit_id: str,
    repeat: int,
) -> Path:
    return cache_root / configuration["id"] / fit_id / f"repeat_{repeat}"


def load_cached_manifest(
    manifest_path: Path, expected_contract: dict[str, Any]
) -> dict[str, Any] | None:
    if not manifest_path.exists():
        return None
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if value.get("block_contract") != expected_contract:
        raise RuntimeError(f"T7 cached block contract changed: {manifest_path}")
    if value.get("block_contract_sha256") != canonical_sha256(expected_contract):
        raise RuntimeError(f"T7 cached block hash changed: {manifest_path}")
    for key in ("evaluation", "trace", "stdout"):
        receipt = value[key]
        path = Path(receipt["path"])
        if not path.is_file() or sha256(path) != receipt["sha256"]:
            raise RuntimeError(f"T7 cached {key} changed: {path}")
    return value


def run_or_load_block(
    prereg: dict[str, Any],
    configuration: dict[str, Any],
    fit_id: str,
    repeat: int,
    cache_root: Path,
) -> tuple[dict[str, Any], bool]:
    contract = block_contract(prereg, configuration, fit_id, repeat)
    directory = block_directory(cache_root, configuration, fit_id, repeat)
    manifest_path = directory / "manifest.json"
    cached = load_cached_manifest(manifest_path, contract)
    if cached is not None:
        return cached, True
    if directory.exists():
        raise RuntimeError(
            f"T7 block exists without a valid frozen manifest: {directory}"
        )
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    evaluation_path = directory / "evaluation.json"
    stdout_path = directory / "stdout.log"
    policy = Path(prereg["frozen_policy"]["path"])
    matrix = prereg["matrix"]
    fit = Path(prereg["repository_inputs"][f"fit_{fit_id}"]["path"])
    command = [
        sys.executable,
        prereg["repository_inputs"]["evaluator"]["path"],
        "--policy",
        str(policy),
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        str(fit),
        "--reference-feature-table",
        prereg["repository_inputs"]["reference_features"]["path"],
        "--reference-start-phase",
        "0",
        "--expected-observation-dim",
        "115",
        "--policy-state-input-names",
        "previous_action,h_in",
        "--policy-state-output-names",
        "previous_action_out,h_out",
        "--policy-applied-target-observation",
        "--trace-dir",
        str(trace_dir),
        "--commands",
        str(matrix["command_x_m_s"]),
        "--seeds",
        str(matrix["seed"]),
        "--duration-s",
        str(matrix["duration_ticks"] / matrix["frequency_hz"]),
        "--minimum-emergence-duration-s",
        "1.08",
        "--task",
        "flat_terrain_backlash",
        "--eval-dynamics-override-json",
        json.dumps(
            configuration["override"], separators=(",", ":"), sort_keys=True
        ),
        "--reset-mode",
        "home-support",
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
    trace_path = (
        trace_dir
        / f"x{matrix['command_x_m_s']:.3f}_seed{matrix['seed']}_{policy.stem}.jsonl"
    )
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or not trace_path.is_file()
    ):
        raise RuntimeError(
            f"T7 evaluator failed: returncode={completed.returncode}; "
            f"log={stdout_path}"
        )
    manifest = {
        "schema_version": "open_duck.t7_universal_response_support_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation": {
            "path": str(evaluation_path),
            "sha256": sha256(evaluation_path),
        },
        "trace": {"path": str(trace_path), "sha256": sha256(trace_path)},
        "stdout": {"path": str(stdout_path), "sha256": sha256(stdout_path)},
    }
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(manifest_path)
    return manifest, False


def exact_com_readback(
    evaluation: dict[str, Any], expected: list[float]
) -> tuple[bool, dict[str, Any] | None]:
    runs = evaluation.get("runs") or []
    if len(runs) != 1:
        return False, None
    dynamics = runs[0].get("dynamics_override")
    if not isinstance(dynamics, dict) or dynamics.get("value") != expected:
        return False, dynamics
    readback = dynamics.get("readback") or {}
    before = np.asarray(readback.get("before"), dtype=np.float64)
    after = np.asarray(readback.get("after"), dtype=np.float64)
    offset = np.asarray(expected, dtype=np.float64)
    valid = bool(
        readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and before.shape == (3,)
        and after.shape == (3,)
        and np.array_equal(after - before, offset)
    )
    return valid, dynamics


def analyze_cell(
    prereg: dict[str, Any],
    graph: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    contract = manifest["block_contract"]
    records = read_trace(Path(manifest["trace"]["path"]))
    evaluation = json.loads(
        Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
    )
    expected_ticks = prereg["matrix"]["duration_ticks"]
    ticks_exact = len(records) == expected_ticks and all(
        row.get("tick") == index for index, row in enumerate(records)
    )
    if not records:
        raise RuntimeError("T7 trace is empty")

    actions = np.asarray([row["action"] for row in records], dtype=np.float32)
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
    target = np.asarray(
        prereg["frozen_policy"]["universal_raw_action"], dtype=np.float32
    )
    delta = np.asarray(graph["maximum_action_delta"], dtype=np.float32)
    expected_actions = []
    previous = np.zeros(14, dtype=np.float32)
    for _ in records:
        lower = np.maximum(previous - delta, -1.0)
        upper = np.minimum(previous + delta, 1.0)
        expected = np.maximum(np.minimum(target, upper), lower)
        expected_actions.append(expected.copy())
        previous = expected
    expected_actions_np = np.asarray(expected_actions, dtype=np.float32)
    action_chain_exact = bool(
        np.array_equal(actions, expected_actions_np)
        and np.array_equal(previous_outputs, actions)
        and np.array_equal(previous_inputs[0], np.zeros(14, dtype=np.float32))
        and np.array_equal(previous_inputs[1:], previous_outputs[:-1])
        and np.array_equal(hidden_inputs[0], np.zeros(64, dtype=np.float32))
        and np.array_equal(hidden_inputs[1:], hidden_outputs[:-1])
    )

    base_height = np.asarray([row["base_height_m"] for row in records], dtype=float)
    local_vx = np.asarray(
        [row["local_linvel_m_s"][0] for row in records], dtype=float
    )
    pitch = np.asarray([row["body_pitch_rad"] for row in records], dtype=float)
    saturation = np.asarray(
        [row["action_saturated"] for row in records], dtype=np.int64
    )
    sent_rate_excess = np.asarray(
        [row["sent_target_rate_excess_rad_s"] for row in records], dtype=float
    )
    conservative_rate_excess = np.asarray(
        [row["conservative_rate_excess_rad_s"] for row in records], dtype=float
    )
    forces = np.abs(
        np.asarray([row["actuator_force_nm"] for row in records], dtype=float)
    )
    current = forces / prereg["behavior_contract"]["servo_protection"][
        "motor_constant_nm_per_a"
    ]
    overcurrent = longest_true_run_per_joint(
        current
        > prereg["behavior_contract"]["servo_protection"][
            "strict_overcurrent_threshold_a"
        ]
    )
    overload = longest_true_run_per_joint(
        forces
        > prereg["behavior_contract"]["servo_protection"][
            "strict_overload_threshold_nm"
        ]
    )
    context_tick = prereg["matrix"]["response_context_tick"]
    context = hidden_outputs[context_tick]
    readback_exact, dynamics_readback = exact_com_readback(
        evaluation, contract["configuration"]["override"]["torso_com_offset_m"]
    )
    runs = evaluation.get("runs") or []
    termination = (
        None
        if len(runs) != 1
        else (runs[0].get("emergence") or {}).get("termination_reason")
    )
    thresholds = prereg["behavior_contract"]["all_cells"]
    protection = prereg["behavior_contract"]["servo_protection"]
    checks = {
        "ticks_exact": ticks_exact,
        "duration_complete": termination == "duration_complete",
        "all_values_finite": bool(
            np.all(np.isfinite(actions))
            and np.all(np.isfinite(hidden_outputs))
            and np.all(np.isfinite(base_height))
            and np.all(np.isfinite(local_vx))
            and np.all(np.isfinite(pitch))
            and np.all(np.isfinite(forces))
        ),
        "action_and_state_chains_exact": action_chain_exact,
        "host_action_delta_zero": all(
            row.get("policy_host_action_delta_max_abs") == 0.0 for row in records
        ),
        "model_com_readback_exact": readback_exact,
        "minimum_base_height": float(np.min(base_height))
        >= thresholds["minimum_base_height_m"],
        "absolute_mean_local_vx": abs(float(np.mean(local_vx)))
        <= thresholds["maximum_absolute_mean_local_vx_m_s"],
        "body_pitch_p95": float(np.percentile(np.abs(pitch), 95))
        <= thresholds["maximum_body_pitch_p95_rad"],
        "zero_saturation": int(np.count_nonzero(saturation)) == 0,
        "zero_sent_rate_excess": float(np.max(sent_rate_excess))
        <= thresholds["maximum_sent_or_conservative_rate_excess_rad_s"],
        "zero_conservative_rate_excess": float(np.max(conservative_rate_excess))
        <= thresholds["maximum_sent_or_conservative_rate_excess_rad_s"],
        "corrected_overcurrent_duration": max(overcurrent)
        <= protection["maximum_consecutive_ticks"],
        "corrected_overload_duration": max(overload)
        <= protection["maximum_consecutive_ticks"],
        "context_finite": bool(np.all(np.isfinite(context))),
    }
    return {
        "configuration_id": contract["configuration"]["id"],
        "fit_id": contract["fit_id"],
        "repeat": contract["repeat"],
        "pass": all(checks.values()),
        "checks": checks,
        "trace": manifest["trace"],
        "evaluation": manifest["evaluation"],
        "dynamics_readback": dynamics_readback,
        "metrics": {
            "minimum_base_height_m": float(np.min(base_height)),
            "mean_local_vx_m_s": float(np.mean(local_vx)),
            "body_pitch_p95_rad": float(np.percentile(np.abs(pitch), 95)),
            "maximum_abs_body_pitch_rad": float(np.max(np.abs(pitch))),
            "action_saturation_pct": float(np.mean(saturation) * 100.0),
            "maximum_sent_rate_excess_rad_s": float(np.max(sent_rate_excess)),
            "maximum_conservative_rate_excess_rad_s": float(
                np.max(conservative_rate_excess)
            ),
            "maximum_torque_nm_diagnostic": float(np.max(forces)),
            "maximum_current_a_diagnostic": float(np.max(current)),
            "maximum_overcurrent_run_ticks": max(overcurrent),
            "maximum_overload_run_ticks": max(overload),
            "per_joint_overcurrent_run_ticks": overcurrent,
            "per_joint_overload_run_ticks": overload,
        },
        "response_context_tick": context_tick,
        "response_context": context.astype(float).tolist(),
        "response_context_sha256": array_sha256(context),
        "hidden_trace_sha256": array_sha256(hidden_outputs),
        "action_trace_sha256": array_sha256(actions),
    }


def response_checks(
    prereg: dict[str, Any], cells: list[dict[str, Any]]
) -> tuple[dict[str, bool], dict[str, Any]]:
    by_key = {
        (cell["configuration_id"], cell["fit_id"], cell["repeat"]): cell
        for cell in cells
    }
    repeat_checks = []
    for configuration in prereg["matrix"]["configurations"]:
        for fit_id in prereg["matrix"]["fits"]:
            first = by_key[(configuration["id"], fit_id, 0)]
            second = by_key[(configuration["id"], fit_id, 1)]
            repeat_checks.append(
                {
                    "configuration_id": configuration["id"],
                    "fit_id": fit_id,
                    "trace_sha256_equal": (
                        first["trace"]["sha256"] == second["trace"]["sha256"]
                    ),
                    "context_sha256_equal": (
                        first["response_context_sha256"]
                        == second["response_context_sha256"]
                    ),
                    "hidden_trace_sha256_equal": (
                        first["hidden_trace_sha256"]
                        == second["hidden_trace_sha256"]
                    ),
                }
            )
    separation = []
    signal = prereg["behavior_contract"]["response_signal"]
    for fit_id in prereg["matrix"]["fits"]:
        negative = np.asarray(
            by_key[("TORSO_COM_X_NEG", fit_id, 0)]["response_context"], dtype=float
        )
        positive = np.asarray(
            by_key[("TORSO_COM_X_POS", fit_id, 0)]["response_context"], dtype=float
        )
        nominal = np.asarray(
            by_key[("NOMINAL", fit_id, 0)]["response_context"], dtype=float
        )
        signed = float(np.max(np.abs(negative - positive)))
        nominal_negative = float(np.max(np.abs(nominal - negative)))
        nominal_positive = float(np.max(np.abs(nominal - positive)))
        separation.append(
            {
                "fit_id": fit_id,
                "signed_endpoint_linf": signed,
                "nominal_to_negative_linf": nominal_negative,
                "nominal_to_positive_linf": nominal_positive,
                "signed_endpoint_pass": (
                    signed
                    >= signal[
                        "minimum_signed_com_endpoint_linf_separation_per_fit"
                    ]
                ),
                "nominal_to_negative_pass": (
                    nominal_negative >= signal["nominal_difference_floor_linf"]
                ),
                "nominal_to_positive_pass": (
                    nominal_positive >= signal["nominal_difference_floor_linf"]
                ),
            }
        )
    checks = {
        "all_repeat_traces_bit_exact": all(
            item["trace_sha256_equal"] for item in repeat_checks
        ),
        "all_repeat_contexts_bit_exact": all(
            item["context_sha256_equal"] for item in repeat_checks
        ),
        "all_repeat_hidden_traces_bit_exact": all(
            item["hidden_trace_sha256_equal"] for item in repeat_checks
        ),
        "all_signed_endpoint_separations_pass": all(
            item["signed_endpoint_pass"] for item in separation
        ),
        "all_nominal_endpoint_separations_pass": all(
            item["nominal_to_negative_pass"] and item["nominal_to_positive_pass"]
            for item in separation
        ),
    }
    return checks, {"repeatability": repeat_checks, "separation": separation}


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# T7 universal response-support result",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        f"- Cells: `{payload['passing_cells']}/{payload['expected_cells']}`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "| configuration | fit | repeat | pass | min z | mean vx | pitch p95 | "
        "current run | overload run | context |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for cell in payload["cells"]:
        metrics = cell["metrics"]
        lines.append(
            f"| `{cell['configuration_id']}` | `{cell['fit_id']}` | "
            f"{cell['repeat']} | `{cell['pass']}` | "
            f"{metrics['minimum_base_height_m']:.9f} | "
            f"{metrics['mean_local_vx_m_s']:.9f} | "
            f"{metrics['body_pitch_p95_rad']:.9f} | "
            f"{metrics['maximum_overcurrent_run_ticks']} | "
            f"{metrics['maximum_overload_run_ticks']} | "
            f"`{cell['response_context_sha256'][:12]}…` |"
        )
    lines.extend(["", "## Response separation", ""])
    for item in payload["response_evidence"]["separation"]:
        lines.append(
            f"- `{item['fit_id']}`: signed `{item['signed_endpoint_linf']:.9f}`, "
            f"nominal→negative `{item['nominal_to_negative_linf']:.9f}`, "
            f"nominal→positive `{item['nominal_to_positive_linf']:.9f}`."
        )
    lines.extend(
        [
            "",
            "This result has zero training steps and no robot/RDK-X5 access. "
            "A pass authorizes only the separately preregistered, zero-training "
            "state-coherent handoff screen; it does not authorize hosted "
            "training, Gate 5, torque, motion, or deployment.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t7_universal_response_support_v1"
        ),
    )
    parser.add_argument("--max-new-blocks", type=int, default=None)
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T7 requires --execute after preregistration review")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T7 result")
    prereg = load_preregistration()
    graph = graph_contract(prereg)
    cache_root = args.cache_root.resolve()
    if str(cache_root) != prereg["execution_contract"]["cache_root"]:
        raise RuntimeError("T7 cache root differs from the preregistration")
    cache_root.mkdir(parents=True, exist_ok=True)

    manifests = []
    cache_hits = 0
    new_blocks = 0
    for configuration in prereg["matrix"]["configurations"]:
        for fit_id in prereg["matrix"]["fits"]:
            for repeat in prereg["matrix"]["repeats"]:
                if (
                    args.max_new_blocks is not None
                    and new_blocks >= args.max_new_blocks
                ):
                    raise RuntimeError(
                        "T7 stopped at --max-new-blocks; partial cache has zero "
                        "decision weight and no result was written"
                    )
                manifest, cached = run_or_load_block(
                    prereg, configuration, fit_id, repeat, cache_root
                )
                manifests.append(manifest)
                cache_hits += int(cached)
                new_blocks += int(not cached)

    cells = [analyze_cell(prereg, graph, manifest) for manifest in manifests]
    response, response_evidence = response_checks(prereg, cells)
    global_checks = {
        "exact_cell_count": len(cells) == prereg["matrix"]["cells"],
        "all_cells_pass": all(cell["pass"] for cell in cells),
        **response,
    }
    passed = all(global_checks.values())
    status = (
        "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
        if passed
        else "HOLD_T7_UNIVERSAL_RESPONSE_SUPPORT"
    )
    decision = (
        "EARN_STATE_COHERENT_SUPPORT_TO_LOCOMOTION_CPU_SCREEN"
        if passed
        else "CLOSE_V91_V96_CURRENT_STACK_TRANSFER"
    )
    basis = {
        "schema_version": "open_duck.t7_universal_response_support_result.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg["preregistered_contract_sha256"],
        "graph_contract": graph,
        "global_checks": global_checks,
        "expected_cells": prereg["matrix"]["cells"],
        "passing_cells": sum(cell["pass"] for cell in cells),
        "cells": cells,
        "response_evidence": response_evidence,
        "execution": {
            "cache_root": str(cache_root),
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "block_manifests": manifests,
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
    print(f"file_sha256={sha256(RESULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
