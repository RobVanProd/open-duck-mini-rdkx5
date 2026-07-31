#!/usr/bin/env python3
"""Formal CPU-only checks for the preregistered winner-v2 runtime ABI."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import onnxruntime


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PACKAGE = ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime"
sys.path.insert(0, str(RUNTIME_PACKAGE))
sys.path.insert(0, str(ROOT / "tools"))

from actuator_bridge_model import ActuatorBridgeModel, params_from_fit  # noqa: E402
from winner_v2 import (  # noqa: E402
    FittedBridgeObserver,
    HOME_TARGET_RAD,
    ProjectedReferenceTable,
    WinnerV2ObservationAdapter,
    WinnerV2OnnxPolicy,
    sha256_file,
    validate_winner_command,
)


POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FITS = {
    "p30": ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
BRIDGE_TRACES = ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_eval_traces"
FULL_OBS_MANIFEST = ROOT / "outputs/analysis/ground_up_torso_com_full_obs_replay_manifest.json"
LEGACY_VECTOR = ROOT / "outputs/analysis/legacy_runtime_golden_vector_20260621.json"
LEGACY_CHECKER = ROOT / "tools/verify_legacy_runtime_golden_vector.py"
RUNTIME_SCRIPT = ROOT / "runtime/scripts/v2_rl_walk_mujoco.py"
EXPECTED_FULL_OBS_ROWS = 40520
EXPECTED_BRIDGE_ROWS = 9600


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rejects(callable_) -> bool:
    try:
        callable_()
    except (ValueError, FileNotFoundError, OSError):
        return True
    return False


def cli_default_is_legacy() -> bool:
    tree = ast.parse(RUNTIME_SCRIPT.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        if node.args[0].value != "--policy-contract":
            continue
        defaults = [
            keyword.value.value
            for keyword in node.keywords
            if keyword.arg == "default" and isinstance(keyword.value, ast.Constant)
        ]
        return defaults == ["legacy101_sent_target_v1"]
    return False


def check_legacy() -> tuple[dict, list[dict]]:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "legacy.json"
        completed = subprocess.run(
            [sys.executable, str(LEGACY_CHECKER), str(LEGACY_VECTOR), str(output)],
            cwd=ROOT,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
            capture_output=True,
            text=True,
        )
        result = json.loads(output.read_text()) if output.exists() else {}
    source = RUNTIME_SCRIPT.read_text()
    checks = {
        "legacy_golden_vector_still_exact": completed.returncode == 0
        and result.get("status") == "PASS_LEGACY_RUNTIME_GOLDEN_VECTOR",
        "legacy_cli_is_default": cli_default_is_legacy(),
        "legacy_still_uses_onnx_infer": "self.policy = OnnxInfer(self.onnx_model_path, awd=True)" in source,
        "winner_adapter_is_conditional": "if self.winner_v2_adapter is not None:" in source,
        "canonical_101_concatenation_retained": "obs = np.concatenate" in source
        and "self.motor_targets," in source
        and "self.imitation_phase," in source,
    }
    return checks, [{"group": "legacy", "metrics": result.get("metrics", {}), "checks": checks}]


def check_full_observations() -> tuple[dict, list[dict]]:
    table = ProjectedReferenceTable(REFERENCE)
    manifest = json.loads(FULL_OBS_MANIFEST.read_text())
    entries = manifest["traces"]
    rows_seen = 0
    zero_rows = 0
    max_reference_error = 0.0
    max_applied_timing_error = 0.0
    cells = []
    corpus_hashes_valid = True
    for entry in entries:
        path = Path(entry["path"])
        corpus_hashes_valid &= path.is_file() and sha256(path) == entry["sha256"]
        rows = [json.loads(line) for line in path.read_text().splitlines() if line]
        trace_reference_error = 0.0
        trace_timing_error = 0.0
        previous_applied = None
        for row in rows:
            obs = np.asarray(row["obs_state"], dtype=float)
            command = np.asarray(row["command"], dtype=float)
            tick = int(row["tick"])
            expected_reference = table.lookup(command[:3], tick % 27)
            reference_error = float(np.max(np.abs(obs[101:115] - expected_reference)))
            trace_reference_error = max(trace_reference_error, reference_error)
            max_reference_error = max(max_reference_error, reference_error)
            if float(np.linalg.norm(command[:3])) <= 0.01:
                zero_rows += 1
            if previous_applied is not None:
                timing_error = float(np.max(np.abs(obs[83:97] - previous_applied)))
                trace_timing_error = max(trace_timing_error, timing_error)
                max_applied_timing_error = max(max_applied_timing_error, timing_error)
            previous_applied = np.asarray(row["applied_target_rad"], dtype=float)
            rows_seen += 1
        cells.append(
            {
                "group": "full_observation_trace",
                "path": str(path),
                "rows": len(rows),
                "max_reference_error": trace_reference_error,
                "max_previous_applied_error_rad": trace_timing_error,
            }
        )
    checks = {
        "exact_full_observation_corpus": len(entries) == 144
        and rows_seen == EXPECTED_FULL_OBS_ROWS
        and corpus_hashes_valid,
        "reference_feature_reproduced": max_reference_error <= 1e-7,
        "zero_command_rows_exercised": zero_rows > 0,
        "previous_applied_timing_reproduced": max_applied_timing_error <= 1e-7,
    }
    cells.append(
        {
            "group": "full_observation_summary",
            "trace_count": len(entries),
            "row_count": rows_seen,
            "zero_command_rows": zero_rows,
            "max_reference_error": max_reference_error,
            "max_previous_applied_error_rad": max_applied_timing_error,
            "checks": checks,
        }
    )
    return checks, cells


def check_observers() -> tuple[dict, list[dict]]:
    max_runtime_analysis_error = 0.0
    max_runtime_recorded_error = 0.0
    total_rows = 0
    trace_count = 0
    cells = []
    for fit_name, fit_path in FITS.items():
        fit = json.loads(fit_path.read_text())
        params = params_from_fit(fit)
        for path in sorted((BRIDGE_TRACES / fit_name).rglob("*.jsonl")):
            rows = [json.loads(line) for line in path.read_text().splitlines() if line]
            runtime = FittedBridgeObserver(fit_path, HOME_TARGET_RAD)
            analysis = ActuatorBridgeModel(params, initial_target=HOME_TARGET_RAD)
            trace_analysis_error = 0.0
            trace_recorded_error = 0.0
            for row in rows:
                sent = np.asarray(row["sent_target_rad"], dtype=float)
                recorded = np.asarray(row["applied_target_rad"], dtype=float)
                runtime_value = runtime.step(sent, 0.02)
                analysis_value = analysis.step(sent, 0.02)
                analysis_error = float(np.max(np.abs(runtime_value - analysis_value)))
                recorded_error = float(np.max(np.abs(runtime_value - recorded)))
                trace_analysis_error = max(trace_analysis_error, analysis_error)
                trace_recorded_error = max(trace_recorded_error, recorded_error)
                max_runtime_analysis_error = max(max_runtime_analysis_error, analysis_error)
                max_runtime_recorded_error = max(max_runtime_recorded_error, recorded_error)
            total_rows += len(rows)
            trace_count += 1
            cells.append(
                {
                    "group": "bridge_trace",
                    "fit": fit_name,
                    "path": str(path.relative_to(ROOT)),
                    "rows": len(rows),
                    "runtime_analysis_max_error_rad": trace_analysis_error,
                    "runtime_recorded_max_error_rad": trace_recorded_error,
                }
            )
    checks = {
        "exact_bridge_corpus": trace_count == 16 and total_rows == EXPECTED_BRIDGE_ROWS,
        "runtime_analysis_observers_exact": max_runtime_analysis_error == 0.0,
        "runtime_reproduces_recorded_targets": max_runtime_recorded_error <= 1e-12,
    }
    cells.append(
        {
            "group": "bridge_summary",
            "trace_count": trace_count,
            "row_count": total_rows,
            "runtime_analysis_max_error_rad": max_runtime_analysis_error,
            "runtime_recorded_max_error_rad": max_runtime_recorded_error,
            "checks": checks,
        }
    )
    return checks, cells


def check_stateful_onnx() -> tuple[dict, list[dict]]:
    rng = np.random.default_rng(20260717)
    max_action_error = 0.0
    max_state_error = 0.0
    cells = []
    for policy_path in POLICIES:
        runner = WinnerV2OnnxPolicy(policy_path)
        direct = onnxruntime.InferenceSession(
            str(policy_path), providers=["CPUExecutionProvider"]
        )
        state = np.zeros((1, 14), dtype=np.float32)
        policy_action_error = 0.0
        policy_state_error = 0.0
        for _ in range(256):
            obs = rng.normal(0.0, 0.5, size=115).astype(np.float32)
            direct_action, direct_state = direct.run(
                ["continuous_actions", "previous_action_out"],
                {"obs": obs[None], "previous_action": state},
            )
            runtime_action = runner.infer(obs)
            action_error = float(np.max(np.abs(runtime_action - direct_action[0])))
            state_error = float(np.max(np.abs(runner.previous_action - direct_state)))
            policy_action_error = max(policy_action_error, action_error)
            policy_state_error = max(policy_state_error, state_error)
            max_action_error = max(max_action_error, action_error)
            max_state_error = max(max_state_error, state_error)
            state = direct_state
        cells.append(
            {
                "group": "stateful_onnx",
                "policy": str(policy_path.relative_to(ROOT)),
                "policy_sha256": sha256_file(policy_path),
                "sequence_rows": 256,
                "max_action_error": policy_action_error,
                "max_state_error": policy_state_error,
                "providers": runner.ort_session.get_providers(),
            }
        )
    checks = {
        "both_persistent_checkpoints_exercised": len(cells) == 2,
        "stateful_actions_exact": max_action_error == 0.0,
        "stateful_state_exact": max_state_error == 0.0,
        "cpu_provider_only": all(cell["providers"] == ["CPUExecutionProvider"] for cell in cells),
    }
    return checks, cells


def check_fail_closed() -> tuple[dict, list[dict]]:
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        bad_policy = directory / "bad.onnx"
        bad_table = directory / "bad.npz"
        bad_fit = directory / "bad.json"
        shutil.copy2(POLICIES[0], bad_policy)
        shutil.copy2(REFERENCE, bad_table)
        shutil.copy2(FITS["p30"], bad_fit)
        with bad_policy.open("ab") as handle:
            handle.write(b"contract-hash-change")
        with bad_table.open("ab") as handle:
            handle.write(b"contract-hash-change")
        fit_payload = json.loads(bad_fit.read_text())
        fit_payload["contract_hash_change"] = True
        bad_fit.write_text(json.dumps(fit_payload))
        adapter = WinnerV2ObservationAdapter(FITS["p30"], REFERENCE, HOME_TARGET_RAD)
        checks = {
            "wrong_policy_hash_rejected": rejects(lambda: WinnerV2OnnxPolicy(bad_policy)),
            "wrong_table_hash_rejected": rejects(lambda: ProjectedReferenceTable(bad_table)),
            "wrong_fit_hash_rejected": rejects(lambda: FittedBridgeObserver(bad_fit, HOME_TARGET_RAD)),
            "missing_table_rejected": rejects(lambda: ProjectedReferenceTable(directory / "missing.npz")),
            "missing_fit_rejected": rejects(lambda: FittedBridgeObserver(directory / "missing.json", HOME_TARGET_RAD)),
            "wrong_home_rejected": rejects(lambda: FittedBridgeObserver(FITS["p30"], np.zeros(14))),
            "lateral_command_rejected": rejects(lambda: validate_winner_command([0.077, 0.01, 0, 0, 0, 0, 0])),
            "yaw_command_rejected": rejects(lambda: validate_winner_command([0.077, 0, 0.01, 0, 0, 0, 0])),
            "head_command_rejected": rejects(lambda: validate_winner_command([0.077, 0, 0, 0.01, 0, 0, 0])),
            "out_of_band_command_rejected": rejects(lambda: validate_winner_command([0.081, 0, 0, 0, 0, 0, 0])),
            "nonunit_phase_rejected": rejects(lambda: WinnerV2ObservationAdapter(FITS["p30"], REFERENCE, HOME_TARGET_RAD, phase_step=2)),
            "fractional_phase_rejected": rejects(lambda: adapter.compose(np.zeros(101), [0.077, 0, 0, 0, 0, 0, 0], 0.5)),
            "action_filter_rejected": rejects(lambda: WinnerV2ObservationAdapter(FITS["p30"], REFERENCE, HOME_TARGET_RAD, action_filter_enabled=True)),
            "wrong_observation_shape_rejected": rejects(lambda: adapter.compose(np.zeros(100), [0.077, 0, 0, 0, 0, 0, 0], 0)),
            "nonfinite_observation_rejected": rejects(lambda: adapter.compose(np.full(101, np.nan), [0.077, 0, 0, 0, 0, 0, 0], 0)),
            "non_20ms_observer_step_rejected": rejects(lambda: adapter.observer.step(HOME_TARGET_RAD, 0.01)),
        }
    return checks, [{"group": "fail_closed", "checks": checks}]


def main() -> int:
    groups = {}
    cells = []
    for name, function in (
        ("legacy_default_off", check_legacy),
        ("full_observation", check_full_observations),
        ("bridge_observer", check_observers),
        ("stateful_onnx", check_stateful_onnx),
        ("fail_closed", check_fail_closed),
    ):
        checks, group_cells = function()
        groups[name] = checks
        cells.extend(group_cells)

    failed_checks = [
        f"{group}.{name}"
        for group, checks in groups.items()
        for name, passed in checks.items()
        if not passed
    ]
    status = (
        "PASS_WINNER_V2_RUNTIME_OFFLINE_CONTRACT_HOLD_HARDWARE_FIT_SELECTION"
        if not failed_checks
        else "HOLD_WINNER_V2_RUNTIME_INTEGRATION"
    )
    result = {
        "schema_version": "winner_v2_runtime_contract.v1",
        "status": status,
        "decision": status,
        "checks": groups,
        "failed_checks": failed_checks,
        "measurements": {
            "cell_records": len(cells),
            "full_observation_rows": next(cell["row_count"] for cell in cells if cell["group"] == "full_observation_summary"),
            "bridge_rows": next(cell["row_count"] for cell in cells if cell["group"] == "bridge_summary"),
            "bridge_runtime_recorded_max_error_rad": next(cell["runtime_recorded_max_error_rad"] for cell in cells if cell["group"] == "bridge_summary"),
        },
        "artifacts": {
            "runtime_script": str(RUNTIME_SCRIPT.relative_to(ROOT)),
            "runtime_script_sha256": sha256(RUNTIME_SCRIPT),
            "winner_v2_module": "runtime/mini_bdx_runtime/mini_bdx_runtime/winner_v2.py",
            "winner_v2_module_sha256": sha256(ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime/winner_v2.py"),
            "policies": {str(path.relative_to(ROOT)): sha256(path) for path in POLICIES},
            "fits": {name: sha256(path) for name, path in FITS.items()},
            "reference_table": sha256(REFERENCE),
        },
        "authority": {
            "hardware_fit_selection": False,
            "robot_or_rdk_x5": False,
            "deployment_or_gate5": False,
            "gpu_or_igpu": False,
            "training_or_hosted_compute": False,
        },
    }
    out_json = ROOT / "outputs/analysis/winner_v2_runtime_contract.json"
    out_cells = ROOT / "outputs/analysis/winner_v2_runtime_contract_cells.json"
    out_md = ROOT / "outputs/analysis/WINNER_V2_RUNTIME_CONTRACT_20260717.md"
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    out_cells.write_text(json.dumps(cells, indent=2, sort_keys=True) + "\n")
    out_md.write_text(
        "# Winner v2 Runtime Offline Contract\n\n"
        f"Status: `{status}`\n\n"
        f"Decision: `{status}`\n\n"
        f"- Frozen full-observation rows checked: {result['measurements']['full_observation_rows']}\n"
        f"- Frozen bridge rows checked: {result['measurements']['bridge_rows']}\n"
        f"- Runtime-to-recorded bridge maximum error: {result['measurements']['bridge_runtime_recorded_max_error_rad']:.12g} rad\n"
        f"- Stateful policies checked: {len(POLICIES)}\n"
        f"- Failed checks: {failed_checks}\n\n"
        "The default legacy 101-D path remains selected unless winner-v2 is explicitly requested. "
        "Winner-v2 now has a strict 115-D observation composer, fitted bridge observer, projected-reference lookup, and stateful CPU ONNX runner. "
        "It requires an explicit contracted fit and does not choose a hardware fit.\n\n"
        "This is an offline implementation result only. Hardware fit selection, deployment, Gate 5, robot/RDK-X5 access, and robot clearance remain unauthorized.\n"
    )
    print(json.dumps({"status": status, "failed_checks": failed_checks}, sort_keys=True))
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
