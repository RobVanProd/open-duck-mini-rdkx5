#!/usr/bin/env python3
"""Validate the metadata-only winner-v2 action-history correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
PREREG = ROOT / "outputs/analysis/winner_v2_action_history_semantics_correction_preregistration.json"
PREIDENTITY = ROOT / "outputs/analysis/winner_v2_action_history_correction_preidentity.json"
CONTRACT_JSON = ROOT / "outputs/analysis/winner_v2_action_history_semantics_correction_contract.json"
CONTRACT_MD = ROOT / "outputs/analysis/WINNER_V2_ACTION_HISTORY_SEMANTICS_CORRECTION_CONTRACT_20260719.md"
SELECTED_SHA = "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity_matches(root: Path, rows: list[dict]) -> bool:
    return all(
        (root / row["path"]).is_file()
        and (root / row["path"]).stat().st_size == row["bytes"]
        and sha256(root / row["path"]) == row["sha256"]
        for row in rows
    )


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    baseline = json.loads(PREIDENTITY.read_text())
    manifest_path = PACKAGE / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    observation_map = json.loads((PACKAGE / "observation_map.json").read_text())
    policy_contract = json.loads((PACKAGE / "policy_contract.json").read_text())
    slices = {int(row["start"]): row for row in observation_map["slices"]}

    external_current = {row["path"]: row for row in manifest["external_source_artifacts"]}
    unchanged_external = baseline["unchanged_external_source_artifacts"]
    unchanged_external_exact = all(
        row["path"] in external_current
        and external_current[row["path"]]["bytes"] == row["bytes"]
        and external_current[row["path"]]["sha256"] == row["sha256"]
        and (ROOT / row["path"]).is_file()
        and sha256(ROOT / row["path"]) == row["sha256"]
        for row in unchanged_external
    )

    smoke = subprocess.run(
        [sys.executable, str(PACKAGE / "inspect_and_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    try:
        smoke_payload = json.loads(smoke.stdout)
    except json.JSONDecodeError:
        smoke_payload = {"status": "UNPARSEABLE", "failures": [smoke.stderr]}

    expected_slices = {
        41: (55, "final_action_t_minus_2", "final graph/environment action from control tick t-2", "two-tick history"),
        55: (69, "final_action_t_minus_3", "control tick t-3", "three-tick history"),
        69: (83, "final_action_t_minus_4", "control tick t-4", "four-tick history"),
    }
    slice_metadata_exact = all(
        start in slices
        and slices[start]["end_exclusive"] == expected[0]
        and slices[start]["name"] == expected[1]
        and slices[start]["source_timing"] == expected[2]
        and slices[start]["delay_filter"] == expected[3]
        for start, expected in expected_slices.items()
    )
    readme = (PACKAGE / "README.md").read_text()
    checks = {
        "preregistration_status_exact": prereg.get("status")
        == "PREREGISTERED_METADATA_ONLY_HISTORY_ORDER_CORRECTION",
        "preidentity_source_commit_exact": baseline.get("source_commit")
        == "e0dc826b06f63a9f5c4a9b083b939de83bec5362",
        "all_unchanged_package_identities_exact": identity_matches(
            PACKAGE, baseline["unchanged_package_files"]
        ),
        "all_unchanged_external_identities_exact": unchanged_external_exact,
        "selected_onnx_byte_identity_exact": sha256(
            PACKAGE / "policies/T2_EQUAL_512000.onnx"
        )
        == SELECTED_SHA,
        "package_schema_corrected_to_v1_1": manifest.get("schema_version")
        == "winner_v2_rdkx5_native_handoff.v1.1"
        and policy_contract.get("schema_version")
        == "winner_v2_rdkx5_native_handoff.v1.1",
        "selected_checkpoint_metadata_exact": manifest.get("selected_checkpoint_step")
        == 512000
        and manifest.get("selected_onnx_sha256") == SELECTED_SHA
        and policy_contract.get("single_selected_deployment_checkpoint") == 512000
        and policy_contract.get("selected_onnx_sha256") == SELECTED_SHA,
        "observation_slice_metadata_exact": slice_metadata_exact,
        "readme_history_table_corrected": all(
            value in readme
            for value in (
                "`41:55` | final action t−2",
                "`55:69` | final action t−3",
                "`69:83` | final action t−4",
                "It contains final action `t-1`",
            )
        ),
        "manifest_hashes_and_sizes_self_consistent": identity_matches(
            PACKAGE, manifest["files"]
        ),
        "cpu_package_smoke_passes": smoke.returncode == 0
        and smoke_payload.get("status")
        == "PASS_CPU_HANDOFF_INSPECTION_BLOCKED_FOR_RUNTIME_REVIEW",
        "all_2400_obs_history_ticks_exact": smoke_payload.get("history_semantics", {}).get(
            "obs_t_minus_2_3_4_max_abs_error"
        )
        == 0.0
        and smoke_payload.get("history_semantics", {}).get("ticks") == 2400,
        "all_2400_previous_action_ticks_exact": smoke_payload.get(
            "history_semantics", {}
        ).get("previous_action_t_minus_1_max_abs_error")
        == 0.0,
        "zero_behavior_or_simulator_ticks_executed_by_correction": baseline.get(
            "formal_behavior_or_simulator_ticks_executed"
        )
        == 0,
    }
    failed = sorted(key for key, value in checks.items() if not value)
    status = (
        "PASS_WINNER_V2_ACTION_HISTORY_SEMANTICS_CORRECTED"
        if not failed
        else "INVALID_WINNER_V2_ACTION_HISTORY_CORRECTION"
    )
    payload = {
        "checks": checks,
        "corrected_files": {
            row["path"]: {
                "bytes": (PACKAGE / row["path"]).stat().st_size,
                "post_sha256": sha256(PACKAGE / row["path"]),
                "pre_sha256": row["sha256"],
            }
            for row in baseline["correction_target_preidentity"]
        },
        "failed_checks": failed,
        "manifest": {
            "post_sha256": sha256(manifest_path),
            "pre_sha256": baseline["pre_manifest_sha256"],
            "schema_version": manifest.get("schema_version"),
        },
        "package_smoke": smoke_payload,
        "schema_version": "winner_v2.action_history_semantics_correction_contract.v1",
        "selected_checkpoint_step": 512000,
        "selected_onnx_sha256": SELECTED_SHA,
        "status": status,
    }
    CONTRACT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v2 Action-History Semantics Correction Contract",
        "",
        f"Status: `{status}`",
        "",
        "| field | corrected control-tick source |",
        "|---|---|",
        "| `obs[41:55]` | final action `t-2` |",
        "| `obs[55:69]` | final action `t-3` |",
        "| `obs[69:83]` | final action `t-4` |",
        "| `previous_action[t]` | final action `t-1` |",
        "",
        f"Replacement manifest SHA-256: `{sha256(manifest_path)}`.",
        f"Selected original ONNX SHA-256: `{SELECTED_SHA}`.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{key}`: `{'PASS' if value else 'FAIL'}`" for key, value in checks.items())
    lines.extend(
        [
            "",
            "This is a metadata/hash-chain correction only. It executes no simulator or",
            "behavior ticks and changes no policy, golden trace, P30 fit, reference table,",
            "selection rule, robot authority, Gate 5, COM result, or hardware state.",
            "",
        ]
    )
    CONTRACT_MD.write_text("\n".join(lines))
    print(CONTRACT_MD.relative_to(ROOT))
    print(CONTRACT_JSON.relative_to(ROOT))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
