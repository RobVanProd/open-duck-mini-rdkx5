#!/usr/bin/env python3
"""Freeze the V127 constrained-continuation CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
ORACLE = ANALYSIS / "winner_v126_all_tick_supreme_clip_behavior_result.json"
RETRO = ANALYSIS / "winner_v126_v115_linear_price_clipping_audit.json"
TRAIN = ROOT / "training/winner_v127_constrained_ppo_train.py"
LOSSES = ROOT / "training/winner_v127_constrained_ppo_losses.py"
PATCH = ROOT / "patches/winner_v127_constrained_cost_channel.patch"
COMPOSER = ROOT / "tools/compose_winner_v127_constrained_playground.py"
RUNNER = ROOT / "tools/run_winner_v127_constrained_cpu_contract.py"
BUILDER = Path(__file__).resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
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
    parser.add_argument("--recovery-work-root", type=Path)
    parser.add_argument("--launch-runner-sha256")
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    recovery_work = (
        args.recovery_work_root.resolve()
        if args.recovery_work_root is not None
        else None
    )
    manifest = playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    retro = json.loads(RETRO.read_text(encoding="utf-8"))
    if (
        oracle.get("status")
        != "PASS_WINNER_V126_ALL_TICK_SUPREME_CLIP_BEHAVIOR_VALID_RESULT"
        or oracle.get("failed_checks") not in (None, [])
        or oracle.get("decision", {}).get("status")
        != "EARN_ONE_V127_CONSTRAINED_CONTINUATION_CPU_CONTRACT"
        or retro.get("status")
        != "PASS_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
        or retro.get("failed_checks") != []
    ):
        raise ValueError("V126 oracle or V115 retro audit is not valid")
    if not manifest.is_file() or not source.is_dir():
        raise FileNotFoundError("V127 composed source or checkpoint missing")
    if (recovery_work is None) != (args.launch_runner_sha256 is None):
        raise ValueError("recovery work and launch-runner hash are paired")
    recovery = None
    if recovery_work is not None:
        recovery_log = recovery_work / "training.log"
        recovery_smoke = recovery_work / "smoke"
        if not recovery_log.is_file() or not recovery_smoke.is_dir():
            raise FileNotFoundError("completed V127 smoke is incomplete")
        log_text = recovery_log.read_text(encoding="utf-8")
        if "STEP: 1024" not in log_text:
            raise ValueError("completed V127 smoke did not reach step 1024")
        launch_lower_bound = recovery_work.stat().st_ctime
        recovery = {
            "authorized": True,
            "reason": (
                "The hash-frozen formal 1024-step subprocess completed, but "
                "the evidence runner exited during postprocessing. Reuse only "
                "these immutable outputs; do not rerun training."
            ),
            "launch_runner_sha256": args.launch_runner_sha256,
            "training_log_sha256": sha256(recovery_log),
            "smoke_directory_sha256": sha256_directory(recovery_smoke),
            "elapsed_upper_bound_seconds": (
                recovery_log.stat().st_mtime - launch_lower_bound + 1.0
            ),
        }

    payload = {
        "schema_version": "winner_v127.constrained_cpu_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V127_CONSTRAINED_CPU_CONTRACT",
        "failed_checks": [],
        "selection": {
            "source_checkpoint": "V121-half raw training state (V119-half)",
            "causal_mechanism": [
                "dense per-tick all-joint torque exceedance",
                "cost never enters the clipped reward",
                "separate cost critic and gamma_C=1 cost GAE",
                "derived adaptive dual price",
            ],
            "oracle_existence_evidence": {
                "cells_passed": "16/16",
                "torque_projections": 15,
                "empty_intersections": 0,
                "max_torque_projection_normalized": 0.049293758384906655,
            },
            "retro_audit_correction": (
                "Frozen V115 evaluation traces show no reward clipping at the "
                "observed event ticks: intended and realized linear-hinge price "
                "are both 0.5862355. V127 is selected for dense adaptive pricing "
                "and separate precursor-state credit, not a false V115 clip claim."
            ),
        },
        "objective": {
            "torque_limit_nm": 1.91229675,
            "cost": "sum_j max(abs(actuator_force_nm[j])-1.91229675,0)",
            "reward_pipeline": "bit-identical V121 reward with old torque scales zero",
            "cost_added_to_reward": False,
            "cost_discount": 1.0,
            "cost_gae_lambda": "same frozen V121 GAE lambda",
            "advantage_normalization": (
                "reward and cost independently use the frozen PPO per-minibatch rule"
            ),
            "actor_advantage": "(A_R-lambda*A_C)/(1+lambda)",
            "cost_value_loss_coefficient": "same frozen reward-value coefficient",
        },
        "dual": {
            "initial_lambda": 0.0,
            "update_order": "collect batch, update dual once, then PPO SGD",
            "batch_cost": "mean over rollout rows of sum_t dense_cost_t",
            "update": "lambda=max(0,lambda+eta*J_C)",
            "eta": "1/(ceil(K/4)*J_C0)",
            "J_C0": "first positive continuation rollout batch cost, used once",
            "K": "total training-step calls fixed by the requested step budget",
            "zero_cost_batches": (
                "leave lambda=eta=0 and the dual uninitialized; the first "
                "violating batch initializes and updates it"
            ),
            "tunable_dual_scalars": 0,
            "development_falsifier": (
                "The initial 1024-step development smoke observed zero cost in "
                "its first batch, disproving the literal first-batch divisor "
                "before preregistration. No hosted run was made."
            ),
        },
        "restore_correction": {
            "source_checkpoint_payload": (
                "normalizer, policy, reward-value only"
            ),
            "restored_bit_exact": [
                "normalizer",
                "policy",
                "reward-value critic",
            ],
            "not_present_in_source": ["optimizer state", "RNG state", "cost critic"],
            "fresh_deterministic_state": [
                "Adam optimizer using frozen V121 continuation semantics",
                "RNG from ppo_seed=100",
                "cost critic from the third deterministic network key",
            ],
            "forbidden_claim": "optimizer or RNG restored from V121",
        },
        "cpu_contract": {
            "default_off": [
                "transition, observation, physics and reward exact",
                "policy export ABI unchanged",
            ],
            "source_law": "dense cost agrees exactly with source actuator_force",
            "synthetic_dual": [
                "zero cost pins lambda and eta at zero without initialization",
                "first positive cost initializes the exact derived eta",
                "persistent J_C0 cost reaches lambda=1 after ceil(K/4) violating batches",
                "lambda is monotone",
            ],
            "smoke": {
                "steps": 1024,
                "num_envs": 4,
                "episode_length": 64,
                "unroll_length": 8,
                "batch_size": 4,
                "num_minibatches": 1,
                "num_updates_per_batch": 2,
            },
            "required": [
                "CPU only",
                "step-0 source normalizer/policy/reward-value bit exact",
                "fresh cost critic deterministic and finite",
                "every policy and cost-critic leaf changes",
                "dual state stays exactly zero if the source smoke has no violation",
                "otherwise J_C0 is finite/positive and eta/lambda follow the rule",
                "step-0 and step-1024 deployment graphs pass the 115/14/64 ABI",
                "step-0 deployed inference equals V121-half",
            ],
        },
        "hosted_gate": {
            "authorized_now": False,
            "earned_only_if": "every CPU-contract check passes",
            "continuations": 1,
            "retry_or_resume": False,
            "exports": [0, 1_003_520, 2_007_040],
            "both_checkpoint_rule": True,
        },
        "input_hashes": {
            "oracle_result": sha256(ORACLE),
            "retro_audit": sha256(RETRO),
            "train": sha256(TRAIN),
            "losses": sha256(LOSSES),
            "patch": sha256(PATCH),
            "composer": sha256(COMPOSER),
            "runner": sha256(RUNNER),
            "builder": sha256(BUILDER),
            "composed_manifest": sha256(manifest),
            "source_checkpoint_directory": sha256_directory(source),
        },
        "external_paths": {
            "playground": str(playground),
            "source_checkpoint": str(source),
        },
        "recovery": recovery,
        "authority": {
            "cpu_contract_authorized": True,
            "colab_authorized": False,
            "robot_or_rdk": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(OUTPUT), "sha256": sha256(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
