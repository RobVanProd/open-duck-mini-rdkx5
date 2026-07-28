#!/usr/bin/env python3
"""Freeze the T72 signed recurrent-core mirror transform."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T66 = ANALYSIS / "t66_endpoint_core_cpu_result.json"
T68 = ANALYSIS / "t68_t67_postexport_result.json"
T70 = ANALYSIS / "t70_t67_condition7_result.json"
T71 = ANALYSIS / "t71_t67_com_hidden_causal_result.json"
T71_PREREG = ANALYSIS / "t71_t67_com_hidden_causal_preregistration_v2.json"
RUNNER = ROOT / "tools" / "run_t72_signed_core_mirror_transform.py"
DEPLOYMENT = ROOT / "tools" / "run_t31_action_margin_trainthrough_cpu_smoke.py"
TEST = ROOT / "tests" / "test_t72_signed_core_mirror.py"
OUTPUT = ANALYSIS / "t72_signed_core_mirror_preregistration.json"
MARKDOWN = ANALYSIS / "T72_SIGNED_CORE_MIRROR_PREREGISTRATION_20260728.md"

CLOSED_MECHANISMS = {
    "phase_com": ANALYSIS / "oracle_phase_com_compensation_result.json",
    "local_sequence": ANALYSIS / "oracle_com_sequence_rescue_result.json",
    "cold_shooting": (
        ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_result.json"
    ),
    "warm_shooting": (
        ANALYSIS / "winner_v37_warm_started_shooting_feasibility_result.json"
    ),
    "mirrored_shooting": (
        ANALYSIS / "winner_v38_mirrored_pitch_shooting_feasibility_result.json"
    ),
    "balance_endpoint": ANALYSIS / "t65_t62_midpoint_endpoint_screen_result.json",
}
CORE_INITIALIZERS = [
    "adapter_obs_weight",
    "adapter_hidden_weight",
    "adapter_hidden_bias",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T72: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T72 preregistration requires a clean worktree")

    t66 = json.loads(T66.read_text(encoding="utf-8"))
    t68 = json.loads(T68.read_text(encoding="utf-8"))
    t70 = json.loads(T70.read_text(encoding="utf-8"))
    t71 = json.loads(T71.read_text(encoding="utf-8"))
    t71_prereg = json.loads(T71_PREREG.read_text(encoding="utf-8"))
    raw = {
        "source": t68["deployments"]["0"]["raw"],
        "endpoint_half": t68["deployments"]["1003520"]["raw"],
        "endpoint_final": t68["deployments"]["2007040"]["raw"],
    }
    closed = {
        name: receipt(path) for name, path in CLOSED_MECHANISMS.items()
    }
    closed_values = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in CLOSED_MECHANISMS.items()
    }
    checks = {
        "t66_only_core_was_trainable": (
            t66["status"] == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
            and t66["checks"]["every_core_leaf_updated"]
            and t66["checks"]["every_other_actor_leaf_bit_exact"]
            and t66["checks"]["normalizer_bit_exact"]
        ),
        "t67_worsened_prior_com_boundary": (
            t70["status"] == "HOLD_T70_T67_CONDITION7"
            and t70["condition"]["green_cells"] == 6
            and t70["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
        ),
        "t71_classifies_wrong_control_response": (
            t71["status"]
            == "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
            and t71["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
            and t71["decision"] == "SELECT_TRANSITION_CONTROL_RESCUE_FALSIFIER"
        ),
        "raw_graph_receipts_exact": all(
            Path(item["path"]).is_file()
            and Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in raw.values()
        ),
        "closed_mechanism_inventory_exact": all(
            Path(item["path"]).is_file()
            and sha256(Path(item["path"])) == item["sha256"]
            for item in closed.values()
        ),
        "prior_alternative_mechanisms_formally_closed": (
            closed_values["phase_com"]["decision"] == "HOLD_ORACLE_PARTIAL"
            and closed_values["local_sequence"]["decision"]
            == "HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE"
            and closed_values["cold_shooting"]["decision"]
            == "DO_NOT_USE_V36_SHOOTING_CONTROLLER_AS_TEACHER"
            and closed_values["warm_shooting"]["decision"]
            == "CLOSE_WARM_STARTED_SHOOTING_PROPOSAL_MECHANISM"
            and closed_values["mirrored_shooting"]["decision"]
            == "CLOSE_MIRRORED_PITCH_SHOOTING_MECHANISM"
            and closed_values["balance_endpoint"]["decision"]
            == "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
        ),
        "runner_deployment_test_present": all(
            path.is_file() for path in (RUNNER, DEPLOYMENT, TEST)
        ),
        "no_behavior_training_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t72_signed_core_mirror_preregistration.v1",
        "status": (
            "PREREGISTERED_T72_SIGNED_CORE_MIRROR"
            if not failed
            else "HOLD_T72_SIGNED_CORE_MIRROR_PREREGISTRATION"
        ),
        "question": (
            "Because endpoint-core continuation alone worsened the exact COM "
            "boundary, does the single preregistered opposite update direction "
            "create a nearby, deployable transition-control response worth one "
            "formal condition-7 behavior screen?"
        ),
        "mechanism": {
            "formula": "theta_mirror = 2 * theta_T52_half - theta_T67_endpoint",
            "fixed_alpha": -1.0,
            "source": "T52 half / T67 step zero",
            "endpoints": [1_003_520, 2_007_040],
            "changed_initializers": CORE_INITIALIZERS,
            "all_other_initializers": "bit-exact T52 source",
            "deployment_chain": (
                "actual-centered guard -> x0 deadband -> trained final rate "
                "projection -> context ABI -> support homeomorphism -> "
                "external physical rates -> 0.98 margin"
            ),
            "scalar_sweep": False,
            "checkpoint_selection": False,
            "both_mirrored_endpoints_required": True,
        },
        "causal_basis": {
            "observability": "T71 proves the COM signal is present and used.",
            "direction": (
                "The only T67 actor change was the recurrent core, and the "
                "exact prior boundary worsened from T52 8/16 to T67 6/16."
            ),
            "not_repeated": {
                "phase_com_static_compensation": "closed",
                "local_block_sequence_rescue": "closed",
                "cold_warm_mirrored_shooting": "closed",
                "balance_reward_homotopy": "closed",
            },
        },
        "raw_graphs": raw,
        "core_initializers": CORE_INITIALIZERS,
        "direction_contract": {
            "trace_population": t71_prereg["shifted_traces"],
            "sample_ticks": [8, 16, 32, 64, 80],
            "commands": [0.074, 0.077, 0.08],
            "minimum_nonzero_pairs_per_endpoint": 50,
            "minimum_fraction_negative_cosine_per_endpoint": 0.90,
            "maximum_median_cosine_per_endpoint": 0.0,
        },
        "decision_rule": {
            "pass": (
                "Both mirrored raw graphs alter exactly the three frozen core "
                "initializers, both deploy through the unchanged chain, all "
                "graph contracts pass, and both action directions are "
                "predominantly opposite on the frozen T71 shifted states."
            ),
            "pass_decision": (
                "EARN_T73_SIGNED_CORE_MIRROR_CONDITION7_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_SIGNED_CORE_MIRROR_WITHOUT_BEHAVIOR",
            "behavior_cells_now": 0,
            "hosted_run_earned": False,
        },
        "closed_mechanisms": closed,
        "frozen_inputs": {
            "t66_core_contract": receipt(T66),
            "t68_deployment_transform": receipt(T68),
            "t70_condition7": receipt(T70),
            "t71_causal_result": receipt(T71),
            "t71_preregistration": receipt(T71_PREREG),
            "runner": receipt(RUNNER),
            "deployment_helper": receipt(DEPLOYMENT),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_two_exact_onnx_transforms": not failed,
            "condition7_behavior_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T72 signed recurrent-core mirror preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Transform: `theta_mirror = 2*theta_T52 - theta_T67`",
                "- Alpha: exactly `-1`; no sweep or checkpoint selection",
                "- Changed tensors: recurrent obs projection, hidden projection, bias",
                "- Behavior / optimizer / Colab / robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
