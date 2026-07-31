#!/usr/bin/env python3
"""Freeze the V126 exact-oracle screen and V115 retro-price audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v126_exact_oracle_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_EXACT_ORACLE_PREREGISTRATION_20260724.md"
)
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V124 = ANALYSIS / "winner_v124_predictive_torque_s0_s2_compact_result.json"
V125 = ANALYSIS / "winner_v125_second_order_predictor_result.json"
V115_PREREG = ANALYSIS / "winner_v115_nominal_behavior_preregistration.json"
V115_RESULT = ANALYSIS / "winner_v115_nominal_behavior_result.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PROJECTOR = ROOT / "tools/exact_torque_oracle.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
TEST = ROOT / "tests/test_exact_torque_oracle.py"
POLICY_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v121-deployment-policies-20260724"
)
PLAYGROUND = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v119-train-transition-playground-20260724"
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


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V126 preregistration")
    required = (
        V121_PREREG,
        V121_RESULT,
        V121_TRANSFORM,
        V124,
        V125,
        V115_PREREG,
        V115_RESULT,
        BASE_PREREG,
        REFERENCE,
        PROJECTOR,
        EVALUATOR,
        TEST,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    v121_prereg = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    v121_transform = json.loads(V121_TRANSFORM.read_text(encoding="utf-8"))
    matrix = v121_prereg["matrix"]["rows"]
    policies = []
    for item in v121_prereg["policies"]:
        path = POLICY_ROOT / item["filename"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(f"V121 policy identity changed: {item['id']}")
        policies.append(
            {
                "id": item["id"],
                "step": int(item["step"]),
                "filename": item["filename"],
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    transform = v121_transform["transform"]
    action_delta = [
        float(value)
        for value in transform["exact_train_normalized_action_delta"]
    ]
    if (
        len(matrix) != 16
        or canonical_sha256(matrix) != v121_prereg["matrix"]["sha256"]
        or len(action_delta) != 14
        or float(transform["g3_margin_rad"]) != 0.165
        or float(transform["action_scale_rad"]) != 0.25
        or not PLAYGROUND.joinpath(
            "playground/open_duck_mini_v2/joystick.py"
        ).is_file()
    ):
        raise ValueError("V121 screen basis changed")

    sources = {
        path.name: {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in required
    }
    payload = {
        "schema_version": "winner_v126.exact_oracle_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V126_EXACT_ORACLE_SCREEN_AND_V115_PRICE_AUDIT"
        ),
        "selection": {
            "primary_mechanism_if_earned": (
                "one constrained continuation from exact V121 half with a "
                "separate unclipped dense per-tick torque-exceedance cost, "
                "separate cost critic/GAE, and derived dual update"
            ),
            "next_required_evidence": [
                "nonformal exact-oracle snapshot/causal-closure CPU contract",
                "read-only V115 realized-vs-intended linear price audit",
                "one frozen 16-cell zero-credit oracle screen",
            ],
            "hosted_training_now": 0,
        },
        "oracle": {
            "training_steps": 0,
            "deployment_candidate": False,
            "purpose": (
                "existence and locality screen only; simulator access makes "
                "this oracle unavailable to the RDK runtime"
            ),
            "torque_limit_nm": 1.91229675,
            "force_tolerance_nm": 5.0e-6,
            "monotonicity_tolerance_nm": 5.0e-6,
            "monotonicity_grid_points": 9,
            "bisection_iterations": 32,
            "maximum_coordinate_passes": 14,
            "guard_rad": 0.165,
            "action_scale_rad": 0.25,
            "action_delta": action_delta,
            "force_horizon": (
                "per-joint fitted bridge delay_ticks; offset zero is the "
                "current transition"
            ),
            "rollout": (
                "clone MJX state.info/metrics, physical bridge, observer bridge, "
                "policy recurrent state, previous-action feedback, IMU history, "
                "phase, and RNG; set the candidate at the source tick; run the "
                "unchanged graph on later branch ticks"
            ),
            "bounds": (
                "intersection of absolute [-1,1], exact V121 previous-action "
                "rate vector, and the 0.165-rad G3 actual-centered guard"
            ),
            "projection": (
                "nearest safe coordinate by a nine-point monotonicity proof and "
                "32 fixed bisections; empty intersections are logged, never "
                "claimed safe"
            ),
            "x0": "exact deadband zero bypasses the oracle",
            "causal_closure": (
                "each source-tick predicted per-joint force is queued to t+delay "
                "and compared with the actual closed-loop force; error above "
                "5e-6 N.m invalidates the screen because intervening projected "
                "policy actions made the purported exact branch non-exact"
            ),
            "nonempty_residual_rule": (
                "a torque exceedance with a matured non-empty prediction is an "
                "oracle implementation failure; prehistory and explicitly empty "
                "intersections are logged separately"
            ),
        },
        "cpu_contract": {
            "formal_behavior_cells": 0,
            "cell": {
                **matrix[1],
                "duration_ticks": 8,
            },
            "runs": [
                "eight-tick oracle-disabled baseline",
                "eight-tick 100-N.m default-off oracle",
                "two identical eight-tick exact-limit oracle repeats",
            ],
            "required": [
                "default-off selected transition arrays exact",
                "repeat selected transition arrays exact",
                "all matured predictions within 5e-6 N.m",
                "zero non-empty residual violations",
                "CPU only",
            ],
        },
        "formal_screen": {
            "matrix": {
                "rows": matrix,
                "cells": len(matrix),
                "sha256": canonical_sha256(matrix),
            },
            "policies": policies,
            "rule": (
                "wrap both checkpoints uniformly; the exact V121-half checkpoint "
                "must pass all eight frozen cells, including x=0, with every "
                "original gait/tracking/duration/saturation/rate/guard/current/"
                "torque criterion green"
            ),
            "oracle_validity": [
                "zero prediction mismatches",
                "zero non-empty residual torque violations",
                "all monotonicity checks pass",
                "all policy/source/model/readbacks exact",
            ],
            "final_checkpoint": (
                "evaluated and reported with zero selection weight for earning "
                "the continuation; it does not replace the required half teacher"
            ),
            "hosted_run_earned_only_if": (
                "CPU contract green, V115 audit filed, formal screen valid, and "
                "V121 half passes all eight cells"
            ),
        },
        "v115_retro_price_audit": {
            "training_steps": 0,
            "source_run_root": json.loads(
                V115_RESULT.read_text(encoding="utf-8")
            )["run_root"],
            "threshold_nm": 1.91229675,
            "linear_scale": -307.48131091308585,
            "cost_per_tick": (
                "mean_j max(0, abs(actuator_force_nm_j)-threshold)"
            ),
            "intended_price": (
                "abs(scale) * sum_t(cost_per_tick * 0.02)"
            ),
            "realized_price": (
                "sum_t(clip(base_without_linear_scaled_sum_t*0.02,0,10000) - "
                "clip((base_without_linear_scaled_sum_t + "
                "scale*cost_per_tick)*0.02,0,10000)); the base is reconstructed "
                "from every scaled reward/cost metric except this linear cost"
            ),
            "report": [
                "per-cell intended and realized price",
                "fraction removed by reward clip",
                "event ticks at which the linear cost was nonzero",
            ],
            "selection_weight": 0,
        },
        "sources": sources,
        "external_inputs": {
            "policy_root": str(POLICY_ROOT),
            "playground": str(PLAYGROUND),
            "playground_manifest_sha256": sha256(
                PLAYGROUND / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
            ),
        },
        "authority": {
            "cpu_contract_runs": 4,
            "v115_read_only_audit": True,
            "formal_screen_cells_after_cpu_contract_pass": 16,
            "training": False,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "gate5": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v126 exact-oracle preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The next executable work is CPU-only: a nonformal snapshot/causal "
        "closure contract, the read-only V115 price audit, and—only after the "
        "contract passes—the frozen 16-cell zero-credit oracle screen.\n\n"
        "The screen is invalid if a matured simulator prediction differs from "
        "the actual closed-loop force by more than `5e-6 N.m`; this explicitly "
        "tests the future-policy feedback subtlety instead of assuming it away.\n\n"
        "No training, hosted compute, GPU, Gate 5, RDK-X5, robot, torque, or "
        "motion is authorized.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT),
                "sha256": sha256(OUTPUT),
                "matrix_sha256": payload["formal_screen"]["matrix"]["sha256"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
