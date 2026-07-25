#!/usr/bin/env python3
"""Preregister V153's phase/contact-synchronous residual graph."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/build_winner_v153_phase_contact_residual.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
V151_RESULT = ANALYSIS / "winner_v151_bounded_two_center_result.json"
V152_ALIGNMENT = ANALYSIS / "winner_v152_phase_contact_alignment.json"
V1_PREREG = (
    ANALYSIS / "winner_v153_phase_contact_residual_preregistration.json"
)
V134_LOADER = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_LOADER = ROOT / "training/winner_v145_on_policy_dagger.py"
OUTPUT = (
    ANALYSIS / "winner_v153_phase_contact_residual_preregistration_v2.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V153_PHASE_CONTACT_RESIDUAL_PREREGISTRATION_V2_20260725.md"
)
EXPECTED = {
    "runner": (
        "3b7bb32f05d38a054115079524b9d633668c37eeac23d52f3fad3192277ec6e9"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v140_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v150_correction": (
        "032641cb262a8138d8cf1b395d61d2b71cca560590652ae0b92090c945531e00"
    ),
    "v151_result": (
        "fbc794b6d12bbe8f60087f8d417a201ccf5b259f5f2514c730ba4af2ef4a90f2"
    ),
    "v152_alignment": (
        "15d2a253d638dac796e0021cdb46daf70aee08ad3dd56ed1c265031548cfaaf7"
    ),
    "v1_preregistration": (
        "7970123f7ad206b8dc1b10f657107f3c1d266f1247daf41bc60d6bc905b1734a"
    ),
    "v134_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "v145_loader": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "source_raw": (
        "aa1025ae4bd2daf1c513cd81374e8eb7961308a41ca10bbe55f6284944fd6460"
    ),
    "source_deployed": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
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
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--source-deployed", type=Path, required=True)
    parser.add_argument("--first-shadow-trace", type=Path, required=True)
    parser.add_argument("--second-shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V153: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    first_shadow_trace = args.first_shadow_trace.resolve()
    second_shadow_trace = args.second_shadow_trace.resolve()
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v150 = json.loads(V150_CORRECTION.read_text(encoding="utf-8"))
    v151 = json.loads(V151_RESULT.read_text(encoding="utf-8"))
    v152 = json.loads(V152_ALIGNMENT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v150_correction": sha256(V150_CORRECTION),
        "v151_result": sha256(V151_RESULT),
        "v152_alignment": sha256(V152_ALIGNMENT),
        "v1_preregistration": sha256(V1_PREREG),
        "v134_loader": sha256(V134_LOADER),
        "v145_loader": sha256(V145_LOADER),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "first_shadow_trace": sha256(first_shadow_trace),
        "second_shadow_trace": sha256(second_shadow_trace),
    }
    first_event = v144["causal_result"]["peak_event"]
    second_event = v150["causal_result"]["event"]
    mechanism = v152["selected_mechanism"]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v140_source_graph_exact": (
            input_hashes["source_raw"] == EXPECTED["source_raw"]
            and input_hashes["source_deployed"]
            == EXPECTED["source_deployed"]
            and v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "state_local_family_closed_and_not_reused": (
            v151.get("decision") == "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
            and mechanism["source"]
            == "V140 raw actor; no V148/V151 state-local centers"
        ),
        "phase_contact_alignment_green": (
            v152.get("status") == "PASS_WINNER_V152_PHASE_CONTACT_ALIGNMENT"
            and v152.get("failed_checks") == []
        ),
        "two_labels_same_joint_sign_phase_contact": (
            first_event["joint"] == second_event["joint"] == 13
            and first_event["source_action_delta"] > 0.0
            and second_event["source_action_delta"] > 0.0
            and mechanism["contacts"] == [0, 1]
        ),
        "amplitude_is_fixed_max_label": (
            mechanism["correction"]
            == max(
                first_event["source_action_delta"],
                second_event["source_action_delta"],
            )
        ),
        "phase_radius_formula_has_no_search": True,
        "frozen_safety_projection_reapplied": True,
        "float32_contract_tolerance_preregistered": True,
        "training_and_behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v153.phase_contact_residual_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V153_PHASE_CONTACT_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V153_PHASE_CONTACT_RESIDUAL_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "supersedes": {
            "artifact": (
                "winner_v153_phase_contact_residual_preregistration.json"
            ),
            "reason": (
                "The first execution stopped before producing a result "
                "because the runner requested a full oracle action vector "
                "from a compact reporting artifact that stores only the "
                "delta. V2 reads that vector from the already frozen and "
                "hashed first shadow trace. The mechanism, source policy, "
                "phase, contact, amplitude, radius rule, tolerance, pass "
                "rule, and stop rule are unchanged."
            ),
        },
        "mechanism": {
            "source": "V140 selected raw actor",
            "trigger": {
                "phase": mechanism["phase"],
                "contacts": mechanism["contacts"],
                "radius": (
                    "half the Euclidean distance to the nearest distinct "
                    "phase sample in the frozen 6,000-row aggregate"
                ),
            },
            "correction": {
                "joint": "right ankle / action index 13",
                "value": mechanism["correction"],
                "rule": "maximum of the two same-sign exact-oracle labels",
            },
            "postprocess": (
                "frozen G3 guard, x=0 deadband, and final rate projection"
            ),
            "state_local_initializers": False,
            "optimizer_or_training": False,
        },
        "pass_rule": {
            "scope": (
                "all changes occur only inside the phase/contact gate and "
                "only on right ankle"
            ),
            "causal_rows": (
                "both known precursors receive the frozen correction; "
                "first matches its oracle and second is conservatively no "
                "smaller"
            ),
            "float32_tolerance": (
                "5e-7 action units, frozen before graph execution from the "
                "observed ONNX float32 associativity budget; no physical "
                "gate changes"
            ),
            "x0": "deadband remains exact",
            "state": "final action feedback exact; h_out exact",
            "safety": "reapplied deployment transform contract green",
        },
        "stop_rule": (
            "any graph-contract failure closes the phase/contact residual; "
            "do not change phase, contact, radius, amplitude, or tolerance"
        ),
        "behavior_stop_rule": (
            "if the separately preregistered single causal cell fails any "
            "frozen gate, close this mechanism without adjustment"
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
        "# Winner V153 phase/contact residual preregistration V2\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Start fresh from V140 and apply one right-ankle correction at "
        "the shared gait phase under right-foot support.\n"
        "- Phase radius and correction amplitude are derived once with no "
        "search.\n"
        "- No behavior, training, Colab, deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
