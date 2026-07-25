#!/usr/bin/env python3
"""Preregister the V139 per-event reference-input controllability audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/audit_winner_v139_reference_input_controllability.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V138_RESULT = ANALYSIS / "winner_v138_phase20_start_result_v2.json"
TEACHER = ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
OUTPUT = (
    ANALYSIS / "winner_v139_reference_input_controllability_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "7f1272ad9cbf34b802b8e544313357582facd73c198da01486ddf9a0fb2a5fda"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v138_phase20_result": (
        "8e0ee98ac9208496bc357ede853a2bee3269426b506666359f2a5267fc8a502d"
    ),
    "teacher_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "network_source": (
        "ffd07d0a6e96d846aa1f62a8d131bf892f10db6b2a22710affe3946b7b145ebd"
    ),
    "source_checkpoint": (
        "c1d9b8574c941e2279294de14aca1cb57d4736bdc63635b5aaf1e205fa7f86c1"
    ),
    "cpu_template": (
        "217a1551c4cc778e4b957636a40ca6e01eafa51efeaef905eb73e9debc7c26e5"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V139: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v138 = json.loads(V138_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v131_behavior_result": sha256(V131_RESULT),
        "v138_phase20_result": sha256(V138_RESULT),
        "teacher_loader": sha256(TEACHER),
        "network_source": sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "phase_start_route_closed": (
            v138.get("status") == "HOLD_WINNER_V138_PHASE20_START_SCREEN"
            and v138.get("decision") == "CLOSE_PHASE20_START"
        ),
        "reference_input_route_is_mechanically_distinct": True,
        "per_event_upper_bound_only": True,
        "one_minimum_norm_solve_no_search": True,
        "behavior_not_authorized": True,
        "reference_change_not_authorized": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v139.reference_input_controllability_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
            if not failed
            else "HOLD_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "With policy weights and recurrent state frozen, can each of the "
            "17 robust torque-oracle action corrections be expressed by a "
            "deployment-valid perturbation of obs[101:115]?"
        ),
        "population": {
            "rows": 17,
            "source": "V131 final-checkpoint torque-projected rows",
            "plants": 2,
            "commands_m_s": [0.074, 0.077, 0.08],
            "x0_rows": 0,
        },
        "method": {
            "variable": "reference input obs[101:115] only",
            "fixed": [
                "V121 final actor weights",
                "normalizer",
                "recorded obs[0:101]",
                "recorded previous_action",
                "recorded h_in",
                "deployment transition",
            ],
            "solver": (
                "one actor action Jacobian and one NumPy minimum-L2 "
                "least-squares solve per event; one nonlinear readback"
            ),
            "parameter_or_threshold_search": False,
        },
        "pass_rule": {
            "source_reproduction": "<=1e-6 max error",
            "linear_combined_ratio": "<=0.25",
            "nonlinear_combined_ratio": "<=0.25",
            "each_event": "nonlinear action error strictly improves",
            "reference_box": "every candidate reference value remains [-1,1]",
            "finite": "all Jacobians, solutions, and actions finite",
        },
        "stop_rule": (
            "if any pass rule fails, close reference-input redirection; do "
            "not add Jacobian iterations, regularization, bounds tuning, or "
            "behavior evaluation"
        ),
        "green_followup": (
            "a pass earns only preregistration of a shared phase/command "
            "reference synthesis with preservation testing"
        ),
        "authority": {
            "cpu_audit": not failed,
            "shared_reference_synthesis": False,
            "reference_artifact_change": False,
            "behavior_evaluation": False,
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
        "# Winner V139 reference-input controllability preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Seventeen per-event local inverses through obs[101:115].\n"
        "- No shared reference, behavior, training, Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
