#!/usr/bin/env python3
"""Validate the frozen recursive cross-CPU study before its formal rerun."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT.parent
RUNTIME = ROBOTS / "open-duck-mini-rdkx5-native-runtime"
ANALYSIS = ROOT / "outputs" / "analysis"
PACKAGE = ROOT / "artifacts" / "runtime_handoff" / "rdkx5_native_20260719"
PREREG_JSON = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_preregistration.json"
PREREG_MD = ANALYSIS / "WINNER_V2_RECURSIVE_CROSS_CPU_CLOSURE_PREREGISTRATION_20260719.md"
OUTPUT_JSON = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_preoutcome_contract.json"
OUTPUT_MD = ANALYSIS / "WINNER_V2_RECURSIVE_CROSS_CPU_CLOSURE_PREOUTCOME_CONTRACT_20260719.md"

RUNTIME_FORMAL_RESULT = (
    RUNTIME
    / "artifacts/gates/phase_5_policy"
    / "winner_v2_recursive_cross_cpu_closure_20260719.json"
)
RUNTIME_FORMAL_VERIFIER = (
    RUNTIME / "tools" / "verify_winner_v2_recursive_cross_cpu_closure.py"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    prereg = load_json(PREREG_JSON)
    identities = prereg["frozen_identities"]
    constants = prereg["frozen_constants"]
    manifest = load_json(PACKAGE / "manifest.json")
    manifest_files = {row["path"]: row for row in manifest["files"]}

    expected_paths = {
        "golden/T2_EQUAL_512000_x0.000.npz": identities[
            "selected_512000_x0_golden_sha256"
        ],
        "golden/T2_EQUAL_512000_x0.080.npz": identities[
            "selected_512000_x0080_golden_sha256"
        ],
        "golden/T2_EQUAL_1024000_x0.000.npz": identities[
            "audit_1024000_x0_golden_sha256"
        ],
        "golden/T2_EQUAL_1024000_x0.080.npz": identities[
            "audit_1024000_x0080_golden_sha256"
        ],
    }

    checks: dict[str, bool] = {}
    checks["preregistration_status_exact"] = (
        prereg["status"] == "PREREGISTERED_BEFORE_FORMAL_RECURSIVE_RERUN"
        and "PREREGISTERED_BEFORE_FORMAL_RECURSIVE_RERUN"
        in PREREG_MD.read_text(encoding="utf-8")
    )
    checks["prior_runtime_report_excluded_from_formal_outcome"] = (
        prereg["previous_runtime_report_has_formal_outcome_weight"] is False
    )
    checks["package_manifest_exact"] = (
        sha256(PACKAGE / "manifest.json") == identities["handoff_manifest_sha256"]
        and manifest["schema_version"] == prereg["package_schema"]
    )
    checks["selected_onnx_exact"] = (
        sha256(PACKAGE / "policies/T2_EQUAL_512000.onnx")
        == prereg["selected_checkpoint"]["onnx_sha256"]
    )
    checks["audit_onnx_exact"] = (
        sha256(PACKAGE / "policies/T2_EQUAL_1024000.onnx")
        == prereg["audit_checkpoint"]["onnx_sha256"]
    )
    checks["observer_and_p30_exact"] = (
        sha256(PACKAGE / "observer/winner_v2_contract.py")
        == identities["observer_contract_source_sha256"]
        and sha256(PACKAGE / "observer/p30_actuator_fit.json")
        == identities["p30_fit_sha256"]
    )
    checks["runtime_conversion_sources_exact"] = (
        sha256(RUNTIME / "src/open_duck_x5/bus/sts3215.py")
        == identities["runtime_sts3215_source_sha256"]
        and sha256(RUNTIME / "src/open_duck_x5/constants.py")
        == identities["runtime_constants_source_sha256"]
    )
    snapshot_path = RUNTIME / "artifacts/contracts/legacy-contract-snapshot.json"
    snapshot = load_json(snapshot_path)
    offsets = np.asarray(snapshot["inputs"]["soft_offsets_rad"], dtype=np.float64)
    checks["soft_offset_snapshot_exact"] = (
        sha256(snapshot_path) == identities["soft_offset_snapshot_sha256"]
        and offsets.shape == (14,)
        and np.array_equal(offsets, np.asarray(prereg["soft_offsets_rad"]))
    )

    lsb = 2.0 * math.pi / 4096.0
    checks["native_resolution_constants_exact"] = (
        constants["sts_position_counts_per_revolution"] == 4096
        and constants["sts_position_lsb_rad"] == lsb
        and constants["sts_half_lsb_rad"] == lsb / 2.0
        and constants["raw_goal_max_abs_count_difference"] == 1
        and constants["action_scale_rad"] == 0.25
        and constants["direct_same_input_tolerance"] == 1.0e-6
    )
    checks["formal_matrix_exact"] = prereg["formal_matrix"] == [
        {"checkpoint_step": 512000, "command_x": 0.0, "gating": True, "ticks": 600},
        {"checkpoint_step": 512000, "command_x": 0.08, "gating": True, "ticks": 600},
        {"checkpoint_step": 1024000, "command_x": 0.0, "gating": False, "ticks": 600},
        {"checkpoint_step": 1024000, "command_x": 0.08, "gating": False, "ticks": 600},
    ]
    checks["history_semantics_exact"] = prereg["history_semantics"] == {
        "obs_41_55": "final_action_t_minus_2",
        "obs_55_69": "final_action_t_minus_3",
        "obs_69_83": "final_action_t_minus_4",
        "previous_action_input": "final_action_t_minus_1",
    }

    pack_rows: list[dict] = []
    packs_valid = True
    for relative, expected_sha in expected_paths.items():
        path = PACKAGE / relative
        manifest_row = manifest_files.get(relative)
        entry_valid = bool(
            manifest_row
            and manifest_row["sha256"] == expected_sha
            and sha256(path) == expected_sha
            and manifest_row["bytes"] == path.stat().st_size
        )
        with np.load(path, allow_pickle=False) as pack:
            shapes = {
                key: list(np.asarray(pack[key]).shape)
                for key in (
                    "tick",
                    "obs",
                    "previous_action_in",
                    "previous_action_out",
                    "final_action",
                    "sent_target_rad",
                    "observer_estimate_next_tick_rad",
                )
            }
            required_shapes = {
                "tick": [600],
                "obs": [600, 115],
                "previous_action_in": [600, 14],
                "previous_action_out": [600, 14],
                "final_action": [600, 14],
                "sent_target_rad": [600, 14],
                "observer_estimate_next_tick_rad": [600, 14],
            }
            shape_valid = shapes == required_shapes
            finite = all(
                np.isfinite(np.asarray(pack[key])).all()
                for key in required_shapes
                if key != "tick"
            )
            ticks_exact = np.array_equal(
                np.asarray(pack["tick"], dtype=np.int64), np.arange(600)
            )
        valid = entry_valid and shape_valid and finite and ticks_exact
        packs_valid = packs_valid and valid
        pack_rows.append(
            {
                "path": relative,
                "sha256": expected_sha,
                "bytes": path.stat().st_size,
                "shapes": shapes,
                "valid": valid,
            }
        )
    checks["all_four_golden_packs_exact_complete_and_finite"] = packs_valid
    checks["selected_and_audit_roles_frozen"] = (
        prereg["selected_checkpoint"]["gating"] is True
        and prereg["audit_checkpoint"]["gating"] is False
    )
    checks["formal_runtime_outputs_absent_before_preregistration_commit"] = (
        not RUNTIME_FORMAL_RESULT.exists() and not RUNTIME_FORMAL_VERIFIER.exists()
    )
    checks["authority_remains_offline_only"] = all(
        value is False for value in prereg["authority"].values()
    )

    failures = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_RECURSIVE_CROSS_CPU_PREOUTCOME_CONTRACT"
        if not failures
        else "HOLD_RECURSIVE_CROSS_CPU_PREOUTCOME_CONTRACT"
    )
    result = {
        "schema_version": "winner_v2.recursive_cross_cpu_preoutcome_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failures,
        "formal_runtime_result_read": False,
        "recursive_ticks_executed": 0,
        "frozen_native_resolution": {
            "sts_position_lsb_rad": lsb,
            "sts_half_lsb_rad": lsb / 2.0,
            "raw_goal_max_abs_count_difference": 1,
        },
        "packs": pack_rows,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Winner-v2 Recursive Cross-CPU Pre-outcome Contract",
        "",
        f"Status: `{status}`",
        "",
        "Formal runtime result read: `NO`.",
        "",
        "Recursive ticks executed: `0`.",
        "",
        "The frozen physical-space boundary is half one native STS3215",
        f"position count: `{lsb / 2.0:.17g} rad`; maximum raw difference is",
        "one count. The existing same-input direct ONNX boundary remains `1e-6`.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{'PASS' if passed else 'FAIL'}`"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "The selected 512000 cells are gating; the 1024000 cells are",
            "audit-only. No result may promote the audit sibling, tune a",
            "threshold, change the graph, or expand robot authority.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_MD.relative_to(ROOT))
    print(OUTPUT_JSON.relative_to(ROOT))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
