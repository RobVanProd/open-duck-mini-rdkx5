#!/usr/bin/env python3
"""Freeze T168's zero-training nominal-adapter persistence attribution."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


OUTPUT = (
    ANALYSIS / "t168_nominal_adapter_persistence_attribution_preregistration.json"
)
T165 = ANALYSIS / "t165_composed_full_r2_result.json"
T166 = ANALYSIS / "t166_lateral_persistence_autopsy_result.json"
T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T164 = ANALYSIS / "t164_prior_repair_composition_result.json"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
COMPOSED_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t164_prior_repair_composition_v1"
)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite T168: {OUTPUT}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T168 builder requires clean worktree")
    t165 = json.loads(T165.read_text(encoding="utf-8"))
    t166 = json.loads(T166.read_text(encoding="utf-8"))
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t164 = json.loads(T164.read_text(encoding="utf-8"))
    checks = {
        "t164_composition_green": (
            t164["status"] == "PASS_T164_PRIOR_REPAIR_COMPOSITION"
        ),
        "t165_first_failure_is_y_negative_persistence": (
            t165["status"] == "HOLD_T165_COMPOSED_FULL_R2"
            and t165["summary"]["first_failed_condition"]
            == "TORSO_COM_Y_NEG"
            and t165["summary"]["green_cells"] == 139
            and t165["summary"]["completed_cells"] == 144
        ),
        "t166_closed_simple_lateral_overlay": (
            t166["status"] == "HOLD_T166_LATERAL_PERSISTENCE_AUTOPSY"
            and t166["decision"]
            == "HOLD_FOR_DIFFERENT_PERSISTENCE_MECHANISM"
        ),
        "t167_closed_static_y_router_but_preserved_all_prior_hashes": (
            t167["status"] == "HOLD_T167_CALIBRATION_CONTEXT_SEPARABILITY"
            and t167["decision"]
            == "CLOSE_STATIC_CALIBRATION_ROUTING_FOR_Y_NEGATIVE"
            and t167["summary"]["prior_hash_matches"] == 18
            and t167["summary"]["prior_hash_cells"] == 18
            and t167["summary"]["existing_router_y_negative_x_path_count"]
            == 0
        ),
        "all_sixteen_y_negative_traces_available": True,
        "execution_now_zero": True,
    }
    traces = []
    for block in t165["blocks"]:
        if block["condition_id"] != "TORSO_COM_Y_NEG":
            continue
        for cell in block["result"]["cells"]:
            item = receipt(Path(cell["protection"]["path"]))
            item.update(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": cell["command_x_m_s"],
                    "rows": cell["protection"]["rows"],
                    "cell_green": cell["cell_green"],
                }
            )
            traces.append(item)
    checks["all_sixteen_y_negative_traces_available"] = (
        len(traces) == 16
        and sum(item["rows"] for item in traces) == 8152
        and all(Path(item["path"]).is_file() for item in traces)
    )
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "open_duck.t168_nominal_adapter_persistence_attribution_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
            if not failed
            else "HOLD_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION_PREREGISTRATION"
        ),
        "question": (
            "Does T164's Y-negative half/final persistence gap reduce "
            "exactly to the nominal T100C adapter pair, without a new "
            "calibration router or broader actor change?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__).resolve()),
            "runner": receipt(
                ROOT
                / "tools/run_t168_nominal_adapter_persistence_attribution.py"
            ),
            "test": receipt(
                ROOT
                / "tests/test_t168_nominal_adapter_persistence_attribution.py"
            ),
            "t164_result": receipt(T164),
            "t165_result": receipt(T165),
            "t166_result": receipt(T166),
            "t167_result": receipt(T167),
        },
        "graphs": {
            "raw_t100c_half": receipt(
                RAW_ROOT / "2026_07_29_023820_1003520.onnx"
            ),
            "raw_t100c_final": receipt(
                RAW_ROOT / "2026_07_29_024350_2007040.onnx"
            ),
            "composed_half": receipt(
                COMPOSED_ROOT / "1003520/composed_three_way_router.onnx"
            ),
            "composed_final": receipt(
                COMPOSED_ROOT / "2007040/composed_three_way_router.onnx"
            ),
        },
        "traces": traces,
        "frozen_test": {
            "contexts": "both T167 TORSO_COM_Y_NEG fit contexts",
            "population": "all 8,152 protected T165 Y-negative trace rows",
            "variants": [
                "half",
                "final",
                "half plus final negative-expert pair",
                "half plus final nominal-expert pair",
                "half plus final positive-expert pair",
                "half plus final positive-endpoint scalar",
            ],
            "pass_rule": [
                "both Y-negative contexts take the nominal route",
                "raw T100C half/final differ only in negative adapter weight/bias",
                "composed nominal pairs equal their raw T100C sources",
                "nominal-pair hybrid equals final on every stored row and output",
                "all inactive-group hybrids equal half on every stored row and output",
                "half/final final actions differ on at least one stored row",
            ],
            "formal_behavior": False,
            "simulator": False,
            "optimizer": False,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "HOLD_FOR_DIFFERENT_PERSISTENCE_MECHANISM",
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "stored_inference_rows": 0,
            "formal_behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_attribution": not failed,
            "cpu_continuation_contract": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
