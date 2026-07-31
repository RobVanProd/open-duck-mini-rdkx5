#!/usr/bin/env python3
"""Preregister the parameter-free V125 second-order predictor falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v125_second_order_predictor_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V125_SECOND_ORDER_PREDICTOR_PREREGISTRATION_20260724.md"
)
INPUTS = {
    "v124_compact_result": (
        ANALYSIS / "winner_v124_predictive_torque_s0_s2_compact_result.json"
    ),
    "v124_preregistration": (
        ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
    ),
    "v124_amendment": ANALYSIS / "winner_v124_s0_ctrl_tolerance_amendment.json",
    "v124_runner": ROOT / "tools/run_winner_v124_predictive_torque_s0_s2.py",
    "bridge_model": ROOT / "tools/actuator_bridge_model.py",
    "v121_transform": (
        ANALYSIS / "winner_v121_deployment_transform_contract.json"
    ),
    "plant_preregistration": (
        ANALYSIS
        / "winner_v3_variable_configuration_replacement_preregistration.json"
    ),
}
EXPECTED = {
    "v124_compact_result": (
        "85f1313fe02a6feb2d4e34a94c07ff755c178c117470fe8e8b92cfe365b1bc29"
    ),
    "v124_preregistration": (
        "61364c864ef3bf97d13df92a79645140a3918ecc8923f52810dd360f16b8042f"
    ),
    "v124_amendment": (
        "46e6c08864ba143b724975528c942f4cc822955a5334407a526580be197290b6"
    ),
    "v124_runner": (
        "a04863a35e738c95613c09848a63c61f309be27e730ede8f8c296213ff6814ed"
    ),
    "bridge_model": (
        "82184df17195cf7241a70e806741a0fdb4e49904fd12b4ee8fe7a38617602472"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "plant_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V125: {path}")
    hashes = {name: sha256(path) for name, path in INPUTS.items()}
    prior = json.loads(
        INPUTS["v124_compact_result"].read_text(encoding="utf-8")
    )
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "v124_source_and_event_causality_passed": (
            prior["s0"]["pass"] is True and prior["s1"]["pass"] is True
        ),
        "v124_constant_velocity_box_failed_only_before_rollout": (
            prior["s2"]["pass"] is False
            and prior["s2"]["summary"]["empty_intersections"] == 20048
            and prior["execution"]["behavior_rollouts"] == 0
        ),
        "v124_hosted_compute_zero": (
            prior["execution"]["training_steps"] == 0
            and prior["execution"]["colab_compute_units"] == 0
        ),
        "v124_s3_not_authorized": (
            prior["authority"]["s3_preregistration_authorized"] is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v125.second_order_predictor_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V125_SECOND_ORDER_PREDICTOR"
            if not failed
            else "HOLD_WINNER_V125_SECOND_ORDER_PREDICTOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "causal_basis": (
            "V124 proved the exact bridge/torque/current model and local action "
            "reachability, but its constant-velocity q predictor produced "
            "0.119-0.153 rad p99.9 errors on five pitch-chain joints. The "
            "unique next Taylor term uses measured acceleration from the "
            "existing velocity history and introduces no fitted scalar."
        ),
        "predictor": {
            "name": "backward_difference_constant_acceleration",
            "equation": (
                "qhat=q_pre+h*qdot_pre+0.5*h^2*qddot_pre; "
                "qddot_pre=(qdot_pre-qdot_previous_pre)/0.02"
            ),
            "initial_tick": "qddot_pre=0 when no previous velocity exists",
            "horizon": "(delay_ticks+1)*0.02-0.002",
            "inputs_runtime_available": [
                "current measured position",
                "current measured velocity",
                "one previous measured velocity",
                "sent-target history",
                "dual frozen bridge state",
            ],
            "fit_parameters": 0,
            "clipping_or_tuned_smoothing": False,
        },
        "unchanged_from_v124": {
            "trace_population": (
                "same six moving V121-half cells and all 15 V121 event precursors"
            ),
            "bridge_transition": "exact delayed/home-gain/lag/rate-clipped model",
            "reserve": (
                "max(p99.9 passing prediction error, maximum V121-event "
                "precursor error) plus the same frozen measurement/goal floor"
            ),
            "torque_box": "same kp=17.11 and 1.91229675 N.m gate",
            "robust_fit_intersection": "same P30 and P31-34 intersection",
            "supreme_constraints": "same [-1,1], G3=0.165 rad, and final rate box",
            "dwell_gate": "same strict >2 A maximum 99 consecutive ticks",
        },
        "decision_rule": {
            "pass": (
                "all 14 reserve-aware half-widths are positive, every V121 "
                "event precursor has a nonempty robust intersection, the six "
                "passing cells have zero empty joint-tick intersections, and "
                "existing >2 A-equivalent dwell remains <=99 ticks"
            ),
            "pass_authority": (
                "authorize only a separate zero-credit uniform wrapper "
                "preregistration; no behavior execution yet"
            ),
            "fail": (
                "close the low-order kinematic predictive-box family without "
                "rollout or Colab; do not try smoothing, clipping, coefficient "
                "search, or a third Taylor-order variant"
            ),
            "comparison_to_v124": "diagnostic only; no closest-result selection",
        },
        "execution_now": {
            "training_steps": 0,
            "behavior_rollouts": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "v125_trace_analysis_authorized": not failed,
            "behavior_screen_authorized": False,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v125 second-order predictor preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "V125 makes one parameter-free change to the failed V124 predictor: "
        "it adds the exact constant-acceleration Taylor term using the current "
        "and previous measured velocity. The bridge, reserve formula, torque "
        "box, fit intersection, constraints, traces, and stop rules do not "
        "change.\n\n"
        "Failure closes the low-order kinematic predictive-box family. No "
        "smoothing, coefficient search, higher-order retry, rollout, training, "
        "Colab, RDK-X5, robot, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
