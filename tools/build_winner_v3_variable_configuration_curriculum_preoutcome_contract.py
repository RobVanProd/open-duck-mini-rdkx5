#!/usr/bin/env python3
"""Freeze winner-v3 curriculum implementation identities before formal checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RECURRENT = ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json"
IMPLEMENTATION = ROOT / "patches/winner_v3_variable_configuration.py"
INTEGRATION = ROOT / "patches/ground_up_winner_v3_variable_configuration.patch"
COMPOSER = ROOT / "tools/compose_winner_v3_playground.py"
CHECKER = ROOT / "tools/check_winner_v3_variable_configuration_curriculum_contract.py"
OUT_JSON = ANALYSIS / "winner_v3_variable_configuration_curriculum_preoutcome_contract.json"
OUT_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_PREOUTCOME_CONTRACT_20260719.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    recurrent = json.loads(RECURRENT.read_text())
    input_paths = {
        "preregistration": PREREG,
        "recurrent_cpu_contract": RECURRENT,
        "implementation": IMPLEMENTATION,
        "integration_patch": INTEGRATION,
        "composer": COMPOSER,
        "checker": CHECKER,
    }
    input_hashes = {name: sha256(path) for name, path in input_paths.items()}
    checks = {
        "replacement_preregistration_exact": (
            input_hashes["preregistration"]
            == "79ed8e765be72b035d94958c106758d170cb740379abab88d5582ddd7735a96b"
        ),
        "recurrent_cpu_contract_passed": (
            recurrent.get("status")
            == "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT"
        ),
        "single_candidate_unchanged": (
            prereg["single_candidate"]["id"] == "R64_ZERO_INIT_RECURRENT_ADAPTER"
        ),
        "single_cpu_no_retry_schedule_unchanged": (
            prereg["training"]["execution"] == "CPU_ONLY_SINGLE_PROCESS_NO_RETRY"
            and prereg["training"]["seed"] == 100
            and prereg["training"]["stages"]
            == [
                {"id": "DOMAIN_25_PERCENT", "steps": 245760, "deviation_scale": 0.25},
                {"id": "DOMAIN_50_PERCENT", "steps": 245760, "deviation_scale": 0.5},
                {
                    "id": "DOMAIN_100_PERCENT",
                    "steps": 2007040,
                    "deviation_scale": 1.0,
                    "persistent_exports_relative_steps": [1003520, 2007040],
                },
            ]
        ),
        "formal_matrix_unchanged_1024": (
            prereg["evaluation_matrix"]["cell_count_derivation"]["total"] == 1024
        ),
        "formal_training_steps_zero": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V3_CURRICULUM_PREOUTCOME_CONTRACT"
        if not failed
        else "HOLD_WINNER_V3_CURRICULUM_PREOUTCOME_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v3.variable_configuration_curriculum_preoutcome_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": input_hashes,
        "implementation_contract": {
            "model_randomization": [
                "floor friction",
                "per-joint frictionloss scale",
                "per-joint armature scale",
                "single all-link mass scale",
                "torso mass addition",
                "torso XYZ COM offset on trunk_assembly body 2",
                "full symmetric torso inertia represented by principal inertia plus inertial-frame quaternion",
            ],
            "inertia_validity": (
                "sample frozen diagonal/product intervals, repeatedly contract halfway toward "
                "the nominal diagonal/zero products, accept only positive-definite and "
                "principal-triangle-valid tensors"
            ),
            "episode_randomization": [
                "P30-to-P31/34 per-joint gain and tau interval",
                "frozen fitted per-joint delay",
                "fixed per-episode additional action delay",
                "fixed per-episode IMU delay applied to gyro plus accelerometer",
                "declared sensor noise scaled by curriculum fraction",
                "frozen native input quantization sampled per episode",
            ],
            "actuator_transition": (
                "delay sent target; form home + gain*(delayed-home); first-order lag with "
                "sampled tau; apply conservative per-joint velocity envelope"
            ),
            "actor_configuration_input": False,
            "default_off_requirement": (
                "winner_v3 flag false must reproduce the pre-patch reset/step trace bit-exact"
            ),
            "required_readback": (
                "all changed model fields plus per-episode actuator, delay, sensor, "
                "quantization and curriculum values"
            ),
        },
        "formal_training_steps_executed": 0,
        "formal_behavior_cells_executed": 0,
        "next": (
            "compose independent baseline and winner-v3 trees from the pinned control "
            "commit, then execute the hash-locked CPU curriculum implementation contract"
        ),
        "authority": {
            "formal_cpu_implementation_contract": not failed,
            "cpu_curriculum_only_after_formal_contract_pass": True,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
            "robot_clearance": False,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(f"""# Winner-v3 Variable-Configuration Curriculum Pre-outcome Contract — 2026-07-19

Status: `{status}`

The implementation, integration patch, deterministic composer and formal CPU
checker are hash frozen before any curriculum PPO step or behavior cell. The
single candidate, seed, 25%/50%/100% stage schedule, reward, protected restore,
persistent checkpoints, 1,024-cell matrix and no-retry rule remain unchanged.

The implementation represents the full torso inertia tensor through MJX's
principal inertia plus inertial-frame quaternion, targets named inertial body 2,
uses one all-link mass scale, and records exact model and episode readback. The
actor receives no true configuration parameter. Disabling winner-v3 must match
the pre-patch simulator trace bit-exact.

- formal curriculum PPO steps read or executed: `0`
- formal behavior cells read or executed: `0`
- failed checks: `{failed}`

A pass authorizes only the formal CPU implementation contract. It is not a
candidate behavior result and grants no hosted allocation, GPU/iGPU, RDK-X5,
robot, runtime, Gate 5, deployment, torque, motion, or clearance authority.
""")
    print(status)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
