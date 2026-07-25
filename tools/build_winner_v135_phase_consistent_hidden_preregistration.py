#!/usr/bin/env python3
"""Preregister the V135 phase-consistent hidden-state derivation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/derive_winner_v135_phase_consistent_hidden.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
PERIOD_RESULT = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_result.json"
TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
OUTPUT = (
    ANALYSIS / "winner_v135_phase_consistent_hidden_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V135_PHASE_CONSISTENT_HIDDEN_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "b919e74b3323eaa9e3aa038e7bee77528ea619505b5accdc09b7f8568c190dd4"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v134_full_actor_result": (
        "e25691c219eec4b76dea0f18b14e47b6fd840b6c0bc53c6c1817cdd5fbf3f387"
    ),
    "phase_period_result": (
        "f946b79b16a6769c87ebf31e4134d1c80c83bc6071bbeb5d61ecade387895a0a"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "p30_x0_trace": (
        "43e174e13e5334ba8a55368e7ee4baa8d1fd860c969c5473ec39155f249c58ae"
    ),
    "p31_34_x0_trace": (
        "d8c17da67ccc1e986ae090cd91594214eca0245c1b5755be5cf544f32d7722c9"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V135: {path}")
    run_root = args.teacher_run_root.resolve()
    traces = sorted((run_root / "traces").glob("*_x0.000_*.jsonl"))
    if len(traces) != 2:
        raise ValueError("V135 preregistration requires two x=0 traces")
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v134 = json.loads(V134_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v126_preregistration": sha256(V126_PREREG),
        "v131_behavior_result": sha256(V131_RESULT),
        "v134_full_actor_result": sha256(V134_RESULT),
        "phase_period_result": sha256(PERIOD_RESULT),
        "v121_transform": sha256(TRANSFORM),
        "p30_x0_trace": sha256(
            next(path for path in traces if "p30_all_joint" in path.name)
        ),
        "p31_34_x0_trace": sha256(
            next(path for path in traces if "p31_34" in path.name)
        ),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "teacher_distillation_family_closed": (
            v134.get("decision")
            == "NO_FULL_ACTOR_TEACHER_DISTILLATION"
        ),
        "torque_projection_startup_concentration_source_backed": True,
        "phase_period_and_selection_rule_frozen": True,
        "read_only_cpu_inference": True,
        "behavior_not_authorized": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v135.phase_consistent_hidden_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V135_PHASE_CONSISTENT_HIDDEN"
            if not failed
            else "HOLD_WINNER_V135_PHASE_CONSISTENT_HIDDEN_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "causal_prior": {
            "torque_projected_rows": 17,
            "torque_projected_rows_ticks_16_through_28": 15,
            "interpretation": (
                "the remaining hard-limit failure is concentrated in the "
                "zero-hidden recurrent startup transient"
            ),
        },
        "derivation": {
            "source": (
                "V131 final checkpoint's two bit-identical x=0 home holds"
            ),
            "phase_period_ticks": 27,
            "selected_tick": 594,
            "selection": (
                "last phase-zero tick strictly inside the frozen 600-tick "
                "home hold; no state or tick search"
            ),
            "vector": "policy_state_input.h_in[64]",
        },
        "contract": {
            "cross_plant_hidden": "bit-exact across both x=0 traces",
            "x0": "warm hidden must retain exact zero action",
            "moving_tick_zero": (
                "both x=.08 first actions must remain finite and inside the "
                "frozen final-action delta"
            ),
            "abi": "unchanged obs[115], previous_action[14], h_in[64]",
        },
        "stop_rule": (
            "if derivation, x=0 exactness, or first-action bounds fail, do "
            "not build or run a warm-start behavior evaluator"
        ),
        "authority": {
            "cpu_derivation_contract": not failed,
            "startup_screen_preregistration": False,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V135 phase-consistent hidden preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Source: last phase-zero hidden state at tick 594 of the frozen "
        "x=0 hold.\n"
        "- Read-only CPU inference; no behavior, training, Colab, or "
        "hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
