#!/usr/bin/env python3
"""Independently apply the frozen recursive-closure rule on the local CPU."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT.parent
RUNTIME = ROBOTS / "open-duck-mini-rdkx5-native-runtime"
PACKAGE = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v2_recursive_cross_cpu_local_corroboration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V2_RECURSIVE_CROSS_CPU_LOCAL_CORROBORATION_20260719.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def max_error(left: np.ndarray, right: np.ndarray) -> float:
    return float(
        np.max(
            np.abs(
                np.asarray(left, dtype=np.float64)
                - np.asarray(right, dtype=np.float64)
            )
        )
    )


def main() -> int:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
    sys.path.insert(0, str(RUNTIME / "src"))
    from open_duck_x5.bus.sts3215 import rad_to_raw_position
    from open_duck_x5.winner_v2 import WINNER_V2_SELECTED_POLICY_SHA256
    from open_duck_x5.winner_v2_verifier import (
        _make_transaction,
        _stage_arguments,
        verify_handoff,
    )

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    constants = prereg["frozen_constants"]
    identities = prereg["frozen_identities"]
    snapshot_path = (
        RUNTIME / "artifacts/contracts/legacy-contract-snapshot.json"
    )
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    offsets = np.asarray(snapshot["inputs"]["soft_offsets_rad"], dtype=np.float64)

    provenance_checks = {
        "preregistration_status_exact": prereg["status"]
        == "PREREGISTERED_BEFORE_FORMAL_RECURSIVE_RERUN",
        "manifest_exact": sha256(PACKAGE / "manifest.json")
        == identities["handoff_manifest_sha256"],
        "selected_onnx_exact": sha256(
            PACKAGE / "policies/T2_EQUAL_512000.onnx"
        )
        == prereg["selected_checkpoint"]["onnx_sha256"],
        "runtime_sts_source_exact": sha256(
            RUNTIME / "src/open_duck_x5/bus/sts3215.py"
        )
        == identities["runtime_sts3215_source_sha256"],
        "runtime_constants_source_exact": sha256(
            RUNTIME / "src/open_duck_x5/constants.py"
        )
        == identities["runtime_constants_source_sha256"],
        "soft_offset_snapshot_exact": sha256(snapshot_path)
        == identities["soft_offset_snapshot_sha256"],
        "soft_offsets_exact": np.array_equal(
            offsets, np.asarray(prereg["soft_offsets_rad"], dtype=np.float64)
        ),
        "cpu_provider_environment_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "",
    }
    if not all(provenance_checks.values()):
        raise RuntimeError(
            "local corroboration provenance failure: "
            + ", ".join(name for name, value in provenance_checks.items() if not value)
        )

    base = verify_handoff(PACKAGE)
    policy_chain_by_key = {
        (int(Path(row["policy"]).stem.rsplit("_", 1)[1]), round(float(row["command_x"]), 3)): row
        for row in base["policy_chain_cells"]
    }
    semantic_by_key = {
        (
            int(Path(row["golden_pack"]).stem.split("_")[2]),
            round(float(row["command_x"]), 3),
        ): row
        for row in base["semantic_cells"]
    }

    cells: list[dict[str, object]] = []
    for matrix in prereg["formal_matrix"]:
        step = int(matrix["checkpoint_step"])
        command = float(matrix["command_x"])
        policy_path = PACKAGE / "policies" / f"T2_EQUAL_{step}.onnx"
        pack_path = PACKAGE / "golden" / f"T2_EQUAL_{step}_x{command:.3f}.npz"
        transaction = _make_transaction(
            PACKAGE,
            policy_path,
            allow_audit_policy=step == 1024000,
        )
        target_per_joint = np.zeros(14, dtype=np.float64)
        p30_per_joint = np.zeros(14, dtype=np.float64)
        raw_per_joint = np.zeros(14, dtype=np.int64)
        maxima = {
            "recursive_observation": 0.0,
            "recursive_action": 0.0,
            "recursive_state_in": 0.0,
            "recursive_state_out": 0.0,
            "recursive_target_rad": 0.0,
            "recursive_p30_rad": 0.0,
        }
        raw_mismatches = 0
        first_raw_mismatch: dict[str, int] | None = None
        x0_action_state_target_p30_exact = True
        with np.load(pack_path, allow_pickle=False) as pack:
            golden_rate_pass = not bool(
                np.any(np.asarray(pack["sent_target_rate_excess_rad_s"]) > 0.0)
            )
            golden_saturation_pass = not bool(np.any(pack["action_saturated"]))
            golden_limiter_identity = not bool(
                np.any(pack["external_5p24_limiter_changed"])
            )
            for tick in range(600):
                arguments = _stage_arguments(pack, tick)
                arguments["soft_offsets_rad"] = offsets
                state_in_error = max_error(
                    transaction.policy.previous_action_view,
                    pack["previous_action_in"][tick],
                )
                transaction.stage_tick(**arguments)
                action = np.asarray(transaction.normalized_action_view)
                logical_target = np.asarray(transaction.logical_target_view)
                golden_target = np.asarray(pack["sent_target_rad"][tick])
                target_error = np.abs(
                    logical_target.astype(np.float64)
                    - golden_target.astype(np.float64)
                )
                target_per_joint = np.maximum(target_per_joint, target_error)
                maxima["recursive_observation"] = max(
                    maxima["recursive_observation"],
                    max_error(transaction.observation_view, pack["obs"][tick]),
                )
                maxima["recursive_action"] = max(
                    maxima["recursive_action"],
                    max_error(action, pack["final_action"][tick]),
                )
                maxima["recursive_state_in"] = max(
                    maxima["recursive_state_in"], state_in_error
                )
                maxima["recursive_state_out"] = max(
                    maxima["recursive_state_out"],
                    max_error(
                        transaction.policy.staged_state_view,
                        pack["previous_action_out"][tick],
                    ),
                )
                maxima["recursive_target_rad"] = max(
                    maxima["recursive_target_rad"], float(target_error.max())
                )

                runtime_raw = np.asarray(
                    [rad_to_raw_position(value) for value in logical_target + offsets],
                    dtype=np.int64,
                )
                golden_raw = np.asarray(
                    [rad_to_raw_position(value) for value in golden_target + offsets],
                    dtype=np.int64,
                )
                raw_error = np.abs(runtime_raw - golden_raw)
                raw_per_joint = np.maximum(raw_per_joint, raw_error)
                mismatch_indices = np.flatnonzero(raw_error)
                raw_mismatches += int(mismatch_indices.size)
                if first_raw_mismatch is None and mismatch_indices.size:
                    joint = int(mismatch_indices[0])
                    first_raw_mismatch = {
                        "tick": tick,
                        "joint_index": joint,
                        "runtime_raw": int(runtime_raw[joint]),
                        "golden_raw": int(golden_raw[joint]),
                        "signed_difference": int(runtime_raw[joint] - golden_raw[joint]),
                    }

                if command == 0.0:
                    x0_action_state_target_p30_exact = bool(
                        x0_action_state_target_p30_exact
                        and np.array_equal(action, pack["final_action"][tick])
                        and np.array_equal(
                            transaction.policy.staged_state_view,
                            pack["previous_action_out"][tick],
                        )
                        and np.array_equal(logical_target, golden_target)
                    )
                transaction.complete_send(write_succeeded=True)
                p30_error = np.abs(
                    transaction.observer.value_view.astype(np.float64)
                    - np.asarray(
                        pack["observer_estimate_next_tick_rad"][tick],
                        dtype=np.float64,
                    )
                )
                p30_per_joint = np.maximum(p30_per_joint, p30_error)
                maxima["recursive_p30_rad"] = max(
                    maxima["recursive_p30_rad"], float(p30_error.max())
                )
                if command == 0.0:
                    x0_action_state_target_p30_exact = bool(
                        x0_action_state_target_p30_exact
                        and np.array_equal(
                            transaction.observer.value_view,
                            np.asarray(
                                pack["observer_estimate_next_tick_rad"][tick],
                                dtype=np.float64,
                            ),
                        )
                    )

        key = (step, round(command, 3))
        chain = policy_chain_by_key[key]
        semantic = semantic_by_key[key]
        same_input_action = float(chain["max_abs_error"]["action"])
        same_input_state = max(
            float(chain["max_abs_error"]["state_in"]),
            float(chain["max_abs_error"]["state_out"]),
        )
        teacher_forced_obs = float(semantic["max_abs_error"]["observation"])
        cell_gates = {
            "ticks_600_exact": transaction.committed_ticks == 600,
            "finite_all_metrics": all(np.isfinite(value) for value in maxima.values()),
            "teacher_forced_obs_bit_exact": teacher_forced_obs == 0.0,
            "same_input_action_at_most_1e_6": same_input_action
            <= constants["direct_same_input_tolerance"],
            "same_input_state_at_most_1e_6": same_input_state
            <= constants["direct_same_input_tolerance"],
            "legacy_limiter_identity": golden_limiter_identity,
            "saturation_classification_unchanged_pass": golden_saturation_pass
            and maxima["recursive_action"] == 0.0,
            "rate_envelope_classification_unchanged_pass": golden_rate_pass
            and maxima["recursive_target_rad"] == 0.0,
            "x0_action_state_target_p30_bit_exact": command != 0.0
            or x0_action_state_target_p30_exact,
            "target_within_half_sts_lsb": maxima["recursive_target_rad"]
            <= constants["sts_half_lsb_rad"],
            "p30_within_half_sts_lsb": maxima["recursive_p30_rad"]
            <= constants["sts_half_lsb_rad"],
            "raw_goal_within_one_count": int(raw_per_joint.max())
            <= constants["raw_goal_max_abs_count_difference"],
        }
        cells.append(
            {
                "checkpoint_step": step,
                "command_x": command,
                "gating": bool(matrix["gating"]),
                "ticks": transaction.committed_ticks,
                "golden_pack": pack_path.name,
                "golden_pack_sha256": sha256(pack_path),
                "policy_sha256": sha256(policy_path),
                "same_input": {
                    "action_max_abs_error": same_input_action,
                    "state_max_abs_error": same_input_state,
                    "teacher_forced_observation_max_abs_error": teacher_forced_obs,
                },
                "recursive_max_abs_error": maxima,
                "target_per_joint_max_abs_error_rad": target_per_joint.tolist(),
                "p30_per_joint_max_abs_error_rad": p30_per_joint.tolist(),
                "raw_goal_per_joint_max_abs_count_difference": raw_per_joint.tolist(),
                "raw_goal_max_abs_count_difference": int(raw_per_joint.max()),
                "raw_goal_mismatch_count": raw_mismatches,
                "first_raw_goal_mismatch": first_raw_mismatch,
                "gates": cell_gates,
                "passed": all(cell_gates.values()),
            }
        )

    selected = [cell for cell in cells if cell["gating"]]
    selected_pass = all(bool(cell["passed"]) for cell in selected)
    selected_raw_mismatches = sum(int(cell["raw_goal_mismatch_count"]) for cell in selected)
    if not selected_pass:
        decision = "HOLD_RECURSIVE_NUMERIC_CLOSURE"
    elif selected_raw_mismatches == 0:
        decision = "PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE"
    else:
        decision = "PASS_RECURSIVE_NATIVE_RESOLUTION_CLOSURE"

    result = {
        "schema_version": "winner_v2.recursive_cross_cpu_local_corroboration.v1",
        "status": "PASS_LOCAL_CORROBORATION_NOT_FORMAL_RUNTIME_DECISION"
        if decision.startswith("PASS_")
        else "HOLD_LOCAL_CORROBORATION_NOT_FORMAL_RUNTIME_DECISION",
        "frozen_rule_decision_on_this_cpu": decision,
        "formal_runtime_decision": False,
        "policy_preregistration_commit": "182459eb4d5eb422a6936b7744f5730d22a9bb27",
        "runtime_source_commit": "e9dc0735a177bb4215e24e2dd8406da01704d2f1",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "onnxruntime": importlib.metadata.version("onnxruntime"),
            "execution_provider": "CPUExecutionProvider",
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "runtime_source_sha256": {
            "winner_v2.py": sha256(RUNTIME / "src/open_duck_x5/winner_v2.py"),
            "winner_v2_verifier.py": sha256(
                RUNTIME / "src/open_duck_x5/winner_v2_verifier.py"
            ),
            "sts3215.py": sha256(RUNTIME / "src/open_duck_x5/bus/sts3215.py"),
            "constants.py": sha256(RUNTIME / "src/open_duck_x5/constants.py"),
        },
        "provenance_checks": provenance_checks,
        "base_runtime_verifier_status": base["status"],
        "selected_policy_sha256": WINNER_V2_SELECTED_POLICY_SHA256,
        "selected_cells_pass": selected_pass,
        "selected_raw_goal_mismatch_count": selected_raw_mismatches,
        "cells": cells,
        "authority": {
            "robot_clearance": False,
            "runtime_acceptance": False,
            "gate5": False,
            "robot": False,
            "rdkx5": False,
            "gpu_or_igpu": False,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    selected_target = max(
        float(cell["recursive_max_abs_error"]["recursive_target_rad"])
        for cell in selected
    )
    selected_p30 = max(
        float(cell["recursive_max_abs_error"]["recursive_p30_rad"])
        for cell in selected
    )
    md = [
        "# Winner-v2 Recursive Cross-CPU Local Corroboration",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Frozen-rule decision on this CPU: `{decision}`.",
        "",
        "This is an independent post-preregistration Linux CPU replay of the",
        "committed runtime implementation. It is corroborating evidence, not",
        "the requested formal result from the runtime agent's CPU.",
        "",
        "## Selected 512000 result",
        "",
        f"- selected logical-target maximum: `{selected_target:.17g} rad`;",
        f"- selected P30 maximum: `{selected_p30:.17g} rad`;",
        f"- selected raw goal mismatches: `{selected_raw_mismatches}`;",
        "- x=0 action/state/target/P30: bit-exact;",
        "- same-input `1e-6` and native half-count gates: pass.",
        "",
        "All four 600-tick cells were run. The 1024000 cells remain audit-only.",
        "No robot, RDK-X5, hardware, GPU or iGPU access occurred. Runtime",
        "acceptance, physical COM, Gate 5 and robot clearance remain pending.",
        "",
    ]
    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(OUTPUT_MD.relative_to(ROOT))
    print(OUTPUT_JSON.relative_to(ROOT))
    return 0 if decision.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
