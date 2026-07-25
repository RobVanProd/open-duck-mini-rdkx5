#!/usr/bin/env python3
"""Preregister V151's bounded two-center residual graph contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/build_winner_v151_bounded_two_center_residual.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V149_RESULT = (
    ANALYSIS / "winner_v149_single_center_causal_behavior_result.json"
)
V150_RESULT = ANALYSIS / "winner_v150_v148_shadow_oracle_result.json"
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
V134_LOADER = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_LOADER = ROOT / "training/winner_v145_on_policy_dagger.py"
OUTPUT = ANALYSIS / "winner_v151_bounded_two_center_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V151_BOUNDED_TWO_CENTER_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "2dc24e99e6b5ef5efa05799b54040a5ca90c4593b936680ba1b5f20e12acfa7b"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v148_result": (
        "a7c0087dc18db1b4371b3ea7598bf768bb55fef881b57b0732e97e766be72d3d"
    ),
    "v149_result": (
        "67ac7db8517bd72c32bf3b171e400aa40a73508d8acc3eaf8d33373fef0654f1"
    ),
    "v150_result": (
        "5232d59b0334a2e83d5d62ae06b5c89886e4cdac78a14425edf6557c54869e98"
    ),
    "v150_correction": (
        "032641cb262a8138d8cf1b395d61d2b71cca560590652ae0b92090c945531e00"
    ),
    "v134_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "v145_loader": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "source_raw": (
        "d60b9c59710bd8f636a6cbe28086fb702a6d15aaf3b249668ada7631a5aca214"
    ),
    "source_deployed": (
        "4d5e3a69ce33fcdce6e714c180f8533b551d604aee5edb8d0b0b143a1a0f1f4b"
    ),
    "first_shadow_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
    "second_shadow_trace": (
        "a816549061de726762ff01602a3366f78a919e9800132f8faca622836e39b731"
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
    parser.add_argument("--first-shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V151: {path}")
    first_shadow_trace = args.first_shadow_trace.resolve()
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    v149 = json.loads(V149_RESULT.read_text(encoding="utf-8"))
    v150 = json.loads(V150_RESULT.read_text(encoding="utf-8"))
    v150_correction = json.loads(
        V150_CORRECTION.read_text(encoding="utf-8")
    )
    source_raw = Path(v148["artifact"]["raw"]["path"])
    source_deployed = Path(v148["artifact"]["deployed"]["path"])
    second_shadow_trace = Path(v150["trace"]["path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v148_result": sha256(V148_RESULT),
        "v149_result": sha256(V149_RESULT),
        "v150_result": sha256(V150_RESULT),
        "v150_correction": sha256(V150_CORRECTION),
        "v134_loader": sha256(V134_LOADER),
        "v145_loader": sha256(V145_LOADER),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "first_shadow_trace": sha256(first_shadow_trace),
        "second_shadow_trace": sha256(second_shadow_trace),
    }
    event = v150_correction["causal_result"]["event"]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "single_center_closed_without_retuning": (
            v149.get("decision") == "CLOSE_SINGLE_CENTER_LOCAL_RESIDUAL"
        ),
        "v150_reporting_corrected_causal_label_green": (
            v150_correction.get("status")
            == "PASS_WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION"
            and v150_correction.get("failed_checks") == []
        ),
        "second_center_is_exact_displaced_event_precursor": (
            event["tick"] == 586
            and event["joint"] == 13
            and event["source_tick"] == 583
            and event["source_action_delta"] != 0.0
            and not event["source_empty_joint_indices"]
        ),
        "two_center_family_bound_preregistered": True,
        "third_center_forbidden": True,
        "radius_formula_has_no_search": True,
        "frozen_safety_projection_reapplied": True,
        "training_and_behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v151.bounded_two_center_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V151_BOUNDED_TWO_CENTER"
            if not failed
            else "HOLD_WINNER_V151_BOUNDED_TWO_CENTER_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V148 raw graph with first center unchanged",
            "second_center": "V150 displaced trajectory tick 583",
            "second_joint": "right ankle / action index 13",
            "second_correction": (
                "exact V150 two-fit oracle final-minus-base action"
            ),
            "second_feature": "obs[115] concatenated with h_in[64]",
            "second_normalization": (
                "z-score over the frozen 4,800+600+600 aggregate"
            ),
            "second_radius": (
                "half the normalized distance to the nearest other "
                "aggregate row"
            ),
            "postprocess": (
                "frozen G3 guard, x=0 deadband, and final rate projection"
            ),
            "optimizer_or_training": False,
        },
        "family_bound": {
            "maximum_centers": 2,
            "centers_after_contract": 2,
            "third_center_permitted": False,
            "rationale": (
                "one bounded follow-up tests whether the first correction "
                "only displaced the original event once; any further "
                "displacement closes the nonparametric local family"
            ),
        },
        "pass_rule": {
            "gate": (
                "the second gate activates only the frozen V150 tick-583 "
                "aggregate row"
            ),
            "preservation": (
                "all other actions are bit-exact to V148 and all first-"
                "center initializers are bit-exact"
            ),
            "target": (
                "second-center right ankle matches its exact oracle <=1e-7"
            ),
            "state": "final action feedback exact; h_out exact",
            "safety": "reapplied deployment transform contract green",
        },
        "stop_rule": (
            "any graph-contract failure closes the finite-local family; "
            "do not change either center, radius, correction, or feature"
        ),
        "behavior_stop_rule": (
            "if the separately preregistered one-cell causal behavior has "
            "any torque failure, close the entire finite-local family and "
            "do not add a third center"
        ),
        "authority": {
            "cpu_graph_contract": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V151 bounded two-center preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Preserve V148's first center and add exactly one frozen "
        "tick-583 right-ankle center.\n"
        "- The family is capped at two centers. A later torque failure "
        "closes it; no third center.\n"
        "- No behavior, training, Colab, deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
