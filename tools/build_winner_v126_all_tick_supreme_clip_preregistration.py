#!/usr/bin/env python3
"""Preregister the supreme-feasibility correction to the all-tick oracle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ALL_TICK_PREREG = (
    ANALYSIS / "winner_v126_all_tick_oracle_preregistration.json"
)
ALL_TICK_HOLD = (
    ANALYSIS / "winner_v126_all_tick_oracle_cpu_contract.json"
)
PROJECTOR = ROOT / "tools/exact_torque_oracle_all_tick.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
OUTPUT = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V126_ALL_TICK_SUPREME_CLIP_PREREGISTRATION_20260724.md"
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
        raise FileExistsError("refusing to overwrite supreme-clip preregistration")
    source = json.loads(ALL_TICK_PREREG.read_text(encoding="utf-8"))
    hold = json.loads(ALL_TICK_HOLD.read_text(encoding="utf-8"))
    if (
        source.get("status")
        != "PREREGISTERED_WINNER_V126_ALL_TICK_EXACT_ORACLE"
        or hold.get("status")
        != "HOLD_WINNER_V126_ALL_TICK_ORACLE_CPU_CONTRACT"
        or hold.get("simulator_diagnostic", {}).get("tick") != 38
        or hold.get("simulator_diagnostic", {}).get("error")
        != "base action violates the supreme oracle interval"
        or hold.get("formal_behavior_cells_executed") != 0
    ):
        raise ValueError("supreme-clip causal prerequisite changed")
    payload = {
        "schema_version": (
            "winner_v126.all_tick_supreme_clip_preregistration.v1"
        ),
        "status": "PREREGISTERED_WINNER_V126_ALL_TICK_SUPREME_CLIP",
        "causal_correction": {
            "held_contract": {
                "path": str(ALL_TICK_HOLD.relative_to(ROOT)),
                "sha256": sha256(ALL_TICK_HOLD),
                "simulator_status": hold["simulator_status"],
                "tick": hold["simulator_diagnostic"]["tick"],
                "error": hold["simulator_diagnostic"]["error"],
            },
            "defect": (
                "The all-tick projector required the graph's requested base "
                "action to already lie inside the intersection of absolute, "
                "frozen G3, and frozen rate bounds. The selected oracle "
                "specification instead requires clipping the requested action "
                "to that supreme feasible intersection before the torque test."
            ),
            "single_correction": (
                "Compute feasible_base=clip(requested_base, low, high), then "
                "run the unchanged exact torque projection from feasible_base. "
                "Log the base-feasibility clip separately from the torque clip."
            ),
            "no_parameter_change": True,
            "no_threshold_change": True,
            "no_matrix_change": True,
        },
        "nonformal_contract": source["nonformal_contract"],
        "matrix": source["matrix"],
        "policies": source["policies"],
        "oracle": {
            **source["oracle"],
            "requested_base_rule": (
                "clip into the supreme feasible interval and log exact "
                "per-joint displacement before torque projection"
            ),
        },
        "external_inputs": source["external_inputs"],
        "formal_rule": source["formal_rule"],
        "evidence": {
            "source_preregistration": {
                "path": str(ALL_TICK_PREREG.relative_to(ROOT)),
                "sha256": sha256(ALL_TICK_PREREG),
            },
            "projector": {
                "path": str(PROJECTOR.relative_to(ROOT)),
                "sha256": sha256(PROJECTOR),
            },
            "evaluator": {
                "path": str(EVALUATOR.relative_to(ROOT)),
                "sha256": sha256(EVALUATOR),
            },
        },
        "authority": {
            "nonformal_contract_runs": 1,
            "formal_screen_cells_after_contract_pass": 16,
            "training": False,
            "hosted_or_colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    if (
        payload["matrix"]["cells"] != 16
        or canonical_sha256(payload["matrix"]["rows"])
        != payload["matrix"]["sha256"]
    ):
        raise ValueError("supreme-clip matrix changed")
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# V126 all-tick supreme-clip preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The tick-38 HOLD exposed an implementation mismatch: the requested "
        "graph action was rejected before the specified supreme feasibility "
        "clip. The correction performs and separately logs that exact clip; "
        "no threshold, matrix, policy, or torque logic changes.\n\n"
        "This authorizes one 64-tick CPU contract and no training.\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    print(sha256(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
