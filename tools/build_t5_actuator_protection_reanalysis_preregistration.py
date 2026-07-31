#!/usr/bin/env python3
"""Freeze the read-only T5 STS3215 protection-envelope reanalysis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t5_actuator_protection_reanalysis_preregistration.json"
MARKDOWN = ANALYSIS / "T5_ACTUATOR_PROTECTION_REANALYSIS_PREREGISTRATION_20260725.md"
ARTIFACT_ROOT = Path(r"D:\CodexArtifacts\open-duck-mini-rdkx5")

REPOSITORY_INPUTS = {
    "current_gate_contract": (
        ANALYSIS / "winner_v3_current_gate_application_contract.json"
    ),
    "v10_contract": ANALYSIS / "winner_v10_inward_torque_contract_result.json",
    "v10_nominal": ANALYSIS / "winner_v10_nominal_behavior_result.json",
    "v121_result": ANALYSIS / "winner_v121_nominal_behavior_result.json",
    "v123_result": ANALYSIS / "winner_v123_nominal_behavior_result.json",
    "v124_model_closure": (
        ANALYSIS / "winner_v124_predictive_torque_s0_s2_compact_result.json"
    ),
    "v128_result": ANALYSIS / "winner_v128_nominal_behavior_result.json",
    "v157_result": (
        ANALYSIS / "winner_v157_dual_checkpoint_nominal_result.json"
    ),
    "v162_result": (
        ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
    ),
    "v174_result": ANALYSIS / "winner_v174_tangent_nominal_result.json",
    "v177_result": ANALYSIS / "winner_v177_nominal_behavior_result.json",
    "runner": ROOT / "tools" / "run_t5_actuator_protection_reanalysis.py",
}

RUN_ROOTS = {
    "V121": {
        "root": ARTIFACT_ROOT / "winner-v121-nominal-run-20260724",
        "expected_cells": 16,
        "role": "previously_rejected_complete_decision_population",
    },
    "V123": {
        "root": ARTIFACT_ROOT / "winner-v123-nominal-run-20260724",
        "expected_cells": 16,
        "role": "previously_rejected_complete_decision_population",
    },
    "V128": {
        "root": ARTIFACT_ROOT / "winner-v128-nominal-behavior-20260724",
        "expected_cells": 16,
        "role": "previously_rejected_complete_decision_population",
    },
    "V157": {
        "root": (
            ARTIFACT_ROOT / "winner-v157-dual-checkpoint-nominal-20260725"
        ),
        "expected_cells": 16,
        "role": "early_stopped_partial_diagnostic",
    },
    "V162": {
        "root": ARTIFACT_ROOT / "winner-v162-uniform-trust-nominal-20260725",
        "expected_cells": 16,
        "role": "early_stopped_partial_diagnostic",
    },
    "V174": {
        "root": ARTIFACT_ROOT / "winner-v174-tangent-nominal-20260725",
        "expected_cells": 6,
        "role": "v121_to_v174_endpoint_reference",
    },
    "V177": {
        "root": ARTIFACT_ROOT / "winner-v177-nominal-behavior-20260725",
        "expected_cells": 16,
        "role": "post_handoff_current_candidate_diagnostic_only",
    },
}


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


def line_count(path: Path) -> int:
    with path.open("rb") as stream:
        return sum(1 for _ in stream)


def run_manifest(spec: dict[str, Any]) -> dict[str, Any]:
    root = Path(spec["root"]).resolve()
    files = sorted(
        [
            path
            for path in root.rglob("*")
            if path.is_file()
            and (
                (path.parent.name == "cells" and path.suffix == ".json")
                or (path.parent.name == "traces" and path.suffix == ".jsonl")
            )
        ],
        key=lambda path: path.relative_to(root).as_posix(),
    )
    entries = []
    for path in files:
        entry = {
            "relative_path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        if path.suffix == ".jsonl":
            entry["rows"] = line_count(path)
        entries.append(entry)
    cells = [
        entry
        for entry in entries
        if entry["relative_path"].startswith("cells/")
    ]
    traces = [
        entry
        for entry in entries
        if entry["relative_path"].startswith("traces/")
    ]
    return {
        "root": str(root),
        "expected_cells": int(spec["expected_cells"]),
        "role": spec["role"],
        "cell_files": len(cells),
        "trace_files": len(traces),
        "files": entries,
        "manifest_sha256": canonical_sha256(entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T5 preregistration")

    missing_repo = [
        name
        for name, path in REPOSITORY_INPUTS.items()
        if not path.is_file()
    ]
    missing_roots = [
        name for name, spec in RUN_ROOTS.items() if not spec["root"].is_dir()
    ]
    repository_inputs = {
        name: {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for name, path in REPOSITORY_INPUTS.items()
        if path.is_file()
    }
    manifests = {
        name: run_manifest(spec)
        for name, spec in RUN_ROOTS.items()
        if spec["root"].is_dir()
    }
    failed_checks = []
    for name in ("V121", "V123", "V128", "V177"):
        manifest = manifests.get(name, {})
        if (
            manifest.get("cell_files") != manifest.get("expected_cells")
            or manifest.get("trace_files") != manifest.get("expected_cells")
        ):
            failed_checks.append(f"incomplete_full_matrix:{name}")
    for name, manifest in manifests.items():
        if manifest["cell_files"] != manifest["trace_files"]:
            failed_checks.append(f"cell_trace_count_mismatch:{name}")

    stall_torque_nm = 19.5 * 0.0980665
    overload_threshold_nm = 0.8 * stall_torque_nm
    corrected_contract = {
        "sample_clock_hz": 50,
        "trip_duration_s": 2.0,
        "trip_ticks": 100,
        "pass_max_consecutive_ticks": 99,
        "motor_constant_nm_per_a": 0.784532,
        "overcurrent_threshold_a": 2.0,
        "overcurrent_comparison": "strictly_greater_than",
        "overload_fraction_of_stall": 0.8,
        "stall_torque_kgf_cm_at_7p4v": 19.5,
        "stall_torque_nm_at_7p4v": stall_torque_nm,
        "overload_threshold_kgf_cm": 15.6,
        "overload_threshold_nm": overload_threshold_nm,
        "overload_comparison": "strictly_greater_than",
        "cell_pass": (
            "every joint has fewer than 100 consecutive 50 Hz ticks strictly "
            "above 2 A and fewer than 100 consecutive ticks strictly above "
            "80% of 7.4-V stall torque; all non-protection behavior gates "
            "remain unchanged"
        ),
        "instantaneous_stall_current_a": 2.5,
        "instantaneous_stall_torque_nm": stall_torque_nm,
        "instantaneous_stall_role": (
            "reported capability/saturation diagnostic, not a one-tick "
            "firmware protection trip"
        ),
        "temperature_gate": (
            "not inferable from simulation; firmware protection and runtime "
            "telemetry remain authoritative"
        ),
    }
    clipping_contract = {
        "source": "winner-v124 exact S0 model closure",
        "kp_nm_per_rad": [17.11] * 14,
        "kv_nm_s_per_rad": [0.0] * 14,
        "forcerange_nm": [[-3.23, 3.23] for _ in range(14)],
        "sim_dt_s": 0.002,
        "qpos_indices": [7, 9, 11, 13, 15, 17, 18, 19, 20, 21, 23, 25, 27, 29],
        "qvel_indices": [6, 8, 10, 12, 14, 16, 17, 18, 19, 20, 22, 24, 26, 28],
        "unclipped_equation": (
            "kp*(applied_target-(qpos_post-0.002*qvel_post))-kv*qvel_post"
        ),
        "clipped_equation": "clip(unclipped, -3.23, +3.23)",
        "reconstruction_tolerance_nm": 5.0e-6,
    }
    decision_rule = {
        "previously_rejected_complete_candidates": ["V121", "V123", "V128"],
        "minimum_corrected_passes_to_reopen": 3,
        "trigger": (
            "if at least three previously rejected complete candidates pass "
            "all recorded cells after replacing only the instantaneous "
            "stall gates with the documented duration protections, classify "
            "the V121-V175 campaign as having fought a mis-specified "
            "constraint and reopen its closures"
        ),
        "partial_candidate_rule": (
            "a corrected pass on every completed cell invalidates a stop "
            "caused only by the old instantaneous gates, but missing cells "
            "remain missing and the candidate is not called a full pass"
        ),
        "v174_role": (
            "endpoint reference; it does not count as a previously rejected "
            "candidate"
        ),
        "v177_role": (
            "post-handoff diagnostic; it cannot change the frozen three-"
            "candidate reopen threshold"
        ),
        "no_threshold_or_candidate_selection_after_results": True,
    }
    status = (
        "PREREGISTERED_T5_ACTUATOR_PROTECTION_REANALYSIS"
        if not missing_repo
        and not missing_roots
        and not failed_checks
        else "HOLD_T5_ACTUATOR_PROTECTION_REANALYSIS_PREREGISTRATION"
    )
    payload = {
        "schema_version": (
            "open_duck.t5_actuator_protection_reanalysis_preregistration.v1"
        ),
        "status": status,
        "question": (
            "Was the instantaneous peak-torque/current constraint physically "
            "mis-specified relative to the STS3215's documented duration-"
            "triggered protection, and did it wrongly close at least three "
            "complete candidate matrices?"
        ),
        "missing_repository_inputs": missing_repo,
        "missing_external_run_roots": missing_roots,
        "failed_checks": failed_checks,
        "repository_inputs": repository_inputs,
        "external_run_manifests": manifests,
        "candidate_order": ["V121", "V123", "V128", "V157", "V162", "V174", "V177"],
        "installed_variant": {
            "servo_model": "STS3215 / ST-3215-C001",
            "nominal_voltage_v": 7.4,
            "basis": (
                "project hardware owner confirmed the installed servos are "
                "the 7.4-V variant; this is a model/variant assertion, not a "
                "new live rail-voltage measurement"
            ),
            "live_voltage_measurement_performed": False,
        },
        "manufacturer_evidence": {
            "detailed_specification": {
                "manufacturer": "Shenzhen FEETECH RC Model Co., Ltd.",
                "model": "STS3215",
                "edition": "A/0",
                "date": "2020-04-10",
                "url": (
                    "https://www.feetechrc.com/Data/feetechrc/upload/file/"
                    "20200611/6372749961523760249976542.pdf"
                ),
                "facts": {
                    "stall_current_a_at_7p4v": 2.5,
                    "stall_torque_kgf_cm_at_7p4v": 19.5,
                    "motor_constant_kgf_cm_per_a": 8.0,
                    "overcurrent": (
                        "current greater than 2 A for 2 s disables output"
                    ),
                    "overload": (
                        "blocked above 80% of stall for 2 s enters protection"
                    ),
                    "overtemperature_c": 70,
                },
            },
            "selection_guide": {
                "manufacturer": "Shenzhen FEETECH RC Model Co., Ltd.",
                "model": "STS3215",
                "url": (
                    "https://www.feetechrc.com/Data/feetechrc/upload/file/"
                    "20230218/%E4%BA%A7%E5%93%81%E6%89%8B%E5%86%8C20230217.pdf"
                ),
                "facts": {
                    "voltage_range_v": [6.0, 8.4],
                    "nominal_performance_voltage_v": 7.4,
                },
            },
        },
        "superseded_instantaneous_gate": {
            "current_a": 2.5,
            "torque_nm": stall_torque_nm,
            "torque_source": "19.5 kgf.cm stall torque converted by 0.0980665",
            "reason_for_reanalysis": (
                "the manufacturer describes stall operating points and "
                "duration-triggered electronic protection; it does not "
                "describe a one-tick simulation rejection at stall torque"
            ),
        },
        "corrected_protection_contract": corrected_contract,
        "simulator_force_clipping_contract": clipping_contract,
        "decision_rule": decision_rule,
        "execution_contract": {
            "read_only": True,
            "simulation_cells": 0,
            "training_steps": 0,
            "trace_hashes_and_row_counts_verified": True,
            "recompute_from_actuator_force_every_tick": True,
            "all_original_nonprotection_failure_reasons_preserved": True,
            "old_peak_current_and_peak_torque_values_reported": True,
            "old_peak_values_removed_from_pass_fail": True,
            "force_clipping_reconstructed_from_exact_v124_s0_equation": True,
        },
        "authority": {
            "offline_cpu_read_only": True,
            "policy_or_model_modification": False,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "robot_rdkx5_gate5_torque_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(
        {
            "repository_inputs": payload["repository_inputs"],
            "external_run_manifests": {
                name: {
                    "root": spec["root"],
                    "expected_cells": spec["expected_cells"],
                    "role": spec["role"],
                    "manifest_sha256": spec["manifest_sha256"],
                }
                for name, spec in manifests.items()
            },
            "installed_variant": payload["installed_variant"],
            "manufacturer_evidence": payload["manufacturer_evidence"],
            "superseded_instantaneous_gate": payload[
                "superseded_instantaneous_gate"
            ],
            "corrected_protection_contract": corrected_contract,
            "simulator_force_clipping_contract": clipping_contract,
            "decision_rule": decision_rule,
            "execution_contract": payload["execution_contract"],
        }
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T5 actuator-protection gate reanalysis preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        "- Decision population: complete V121, V123, and V128 matrices.\n"
        "- Frozen reopen trigger: all three pass after replacing only the "
        "instantaneous stall gates with the documented 2-second protection "
        "rules.\n"
        "- Protection proxies: `>2 A` for `100` ticks and `>80%` stall "
        "torque for `100` ticks, evaluated per joint.\n"
        "- Manufacturer evidence: the official [STS3215 A/0 detailed "
        "specification](https://www.feetechrc.com/Data/feetechrc/upload/file/"
        "20200611/6372749961523760249976542.pdf) and [2023 selection guide]"
        "(https://www.feetechrc.com/Data/feetechrc/upload/file/20230218/"
        "%E4%BA%A7%E5%93%81%E6%89%8B%E5%86%8C20230217.pdf).\n"
        "- V157/V162 partial cells, V174, and post-handoff V177 are reported "
        "without changing the trigger.\n"
        "- No simulation, training, policy selection, robot access, or Gate "
        "5 action is authorized.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
