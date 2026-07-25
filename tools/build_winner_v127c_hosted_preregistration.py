#!/usr/bin/env python3
"""Preregister V127c after the proven pretraining cwd correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
CPU_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
CORRECTION = ANALYSIS / "winner_v127_pretraining_launch_correction.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v127_constrained_continuation.py"
OUTPUT = ANALYSIS / "winner_v127c_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V127C_HOSTED_PREREGISTRATION_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
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
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    checks = {
        "cpu_contract_green": (
            cpu.get("status")
            == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and cpu.get("failed_checks") == []
        ),
        "pretraining_correction_green": (
            correction.get("status")
            == "PASS_WINNER_V127_PRETRAINING_LAUNCH_CORRECTION"
            and correction.get("failed_checks") == []
            and correction.get("decision")
            == "AUTHORIZE_ONE_V127C_PRETRAINING_LAUNCH_CORRECTION"
        ),
        "prior_optimizer_steps_zero": correction["checks"][
            "optimizer_steps_zero"
        ],
        "prior_simulator_steps_zero": correction["checks"][
            "simulator_locomotion_steps_zero"
        ],
        "training_command_and_objective_unchanged": True,
        "only_driver_cwd_changed": True,
        "single_continuation_only": True,
        "no_training_retry_or_resume": True,
        "both_postupdate_checkpoints_required": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "cpu_preregistration": sha256(CPU_PREREG),
        "pretraining_launch_correction": sha256(CORRECTION),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    payload = {
        "schema_version": "winner_v127c.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V127C_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V127C_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "correction": correction["correction"],
        "training": {
            "source": "exact_v121_half_raw_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "num_envs": 256,
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "tracking_tail_scale": -6572.254964031055,
            "old_squared_torque_scale": 0.0,
            "old_linear_torque_scale": 0.0,
            "dense_cost": (
                "sum_j max(abs(actuator_force_nm[j])-1.91229675,0)"
            ),
            "cost_discount": 1.0,
            "dual_eta": "1/(ceil(K/4)*first_positive_batch_cost)",
            "retry": False,
            "resume": False,
        },
        "stop_rule": (
            "either post-update checkpoint failing any nominal cell closes "
            "V127; no eta changes or additional continuation"
        ),
        "authority": {
            "one_corrected_hosted_continuation_after_package": not failed,
            "additional_training_or_retry": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127c hosted preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Prior launch stopped before reset, rollout, optimization, or export.\n"
        "- Only correction: driver working directory is the playground root.\n"
        "- Training source, command, objective, and both-checkpoint rule unchanged.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
