#!/usr/bin/env python3
"""Generate the four frozen CPU full-observation winner-v2 handoff traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
PATCH_HASHES = {
    "ground_up_search_runner.patch": "6a176589b766de65ac2746c66f3387bfca5384d6ce4adf3703c752d8103a5e55",
    "ground_up_reference_conditioned.patch": "4138ecddb9ffc0df468a2780522c1732bc4b0e1a0865d181da1112d1c16902fb",
    "ground_up_recipe_search.patch": "3f5d892f5ce531207de6c86b18c9f5dbea83bc131a3fc2e5085851c2e4e3e5f8",
    "ground_up_stage1_mechanism_stack.patch": "cf5155dfd54a4699865b9823e8bf090f9f54b0e53df5583eb448e315d60053dc",
    "ground_up_nominal_reference_bootstrap.patch": "0d89b85815eb570115ec5f35d677aba68299f977b3e36c60b10dfa869533ebba",
    "ground_up_signed_progress_objective.patch": "13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b",
    "ground_up_reference_residual_actor.patch": "57bcf2394fa47745e9c26c6933e58a06c3799aba35e7000762befc5fac2f7d3b",
    "ground_up_hard_vector_command_support.patch": "900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875",
    "ground_up_measured_actuator_bridge.patch": "133531963abea46cd0394526a2fa88b018fc21ca68c365863304e3e96d6ca0df",
    "ground_up_applied_target_observation.patch": "bdcac27115fcbe855079f5365ac046e863a9b302ff16f560d12a26cd492f2821",
    "ground_up_tracking_tail_exceedance.patch": "9f716243e0c4ef487ef4227ef0cb9f389ed43c0456435987ac0846e1b629811e",
}
NETWORK_HASH = "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630"
POLICY_HASHES = {
    512000: "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
    1024000: "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def prepare_worktree(source: Path, worktree: Path, recreate: bool) -> None:
    if worktree.exists():
        if not recreate:
            raise SystemExit(f"worktree exists; pass --recreate: {worktree}")
        if not str(worktree.resolve()).startswith("/tmp/"):
            raise SystemExit("refusing to remove a worktree outside /tmp")
        run(["git", "worktree", "remove", "--force", str(worktree)], cwd=source)
    run(
        ["git", "worktree", "add", "--detach", str(worktree), CONTROL_COMMIT],
        cwd=source,
    )
    for name, expected in PATCH_HASHES.items():
        patch = REPO_ROOT / "patches" / name
        if sha256(patch) != expected:
            raise SystemExit(f"patch hash mismatch: {name}")
        run(["git", "apply", "--check", str(patch)], cwd=worktree)
        run(["git", "apply", str(patch)], cwd=worktree)
    network = REPO_ROOT / "patches/reference_residual_ppo_networks.py"
    if sha256(network) != NETWORK_HASH:
        raise SystemExit("reference-residual network hash mismatch")
    shutil.copy2(
        network,
        worktree / "playground/common/reference_residual_ppo_networks.py",
    )
    run(["git", "diff", "--check"], cwd=worktree)


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def compare_to_frozen(step: int, command: float, fresh: Path) -> dict:
    frozen = (
        REPO_ROOT
        / "outputs/analysis/ground_up_dual_fit_conservative_envelope_eval_traces"
        / "p30"
        / f"T2_EQUAL_{step}"
        / f"x{command:.3f}_seed167931544_T2_EQUAL_{step}.jsonl"
    )
    left, right = rows(frozen), rows(fresh)
    if len(left) != 600 or len(right) != 600:
        raise ValueError("trace row count is not 600")
    errors = {}
    for key in [
        "action", "sent_target_rad", "applied_target_rad",
        "actual_position_rad", "obs0_6",
    ]:
        errors[key] = max(
            float(
                np.max(
                    np.abs(
                        np.asarray(a[key], dtype=float)
                        - np.asarray(b[key], dtype=float)
                    )
                )
            )
            for a, b in zip(left, right, strict=True)
        )
    return {
        "frozen_path": str(frozen.relative_to(REPO_ROOT)),
        "frozen_sha256": sha256(frozen),
        "fresh_path": str(fresh),
        "fresh_sha256": sha256(fresh),
        "max_abs_errors": errors,
        "exact": max(errors.values()) == 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-repository",
        type=Path,
        default=REPO_ROOT.parent / "Open_Duck_Playground",
    )
    parser.add_argument(
        "--worktree-root",
        type=Path,
        default=Path("/tmp/open-duck-winner-v2-handoff-playground"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("/tmp"))
    parser.add_argument("--recreate", action="store_true")
    args = parser.parse_args()
    source = args.source_repository.resolve()
    worktree = args.worktree_root.resolve()
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    prepare_worktree(source, worktree, args.recreate)

    fit_path = REPO_ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    fit = json.loads(fit_path.read_text())
    reference = REPO_ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
    cells = []
    for step, expected_hash in POLICY_HASHES.items():
        policy = (
            REPO_ROOT
            / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies"
            / f"T2_EQUAL_{step}.onnx"
        )
        if sha256(policy) != expected_hash:
            raise SystemExit(f"policy hash mismatch: {policy}")
        for command in [0.0, 0.08]:
            trace = output / f"winner_v2_{step}_x{command:.3f}_full.jsonl"
            result = run_closed_loop_sim(
                ClosedLoopConfig(
                    policy_path=policy,
                    fit=fit,
                    playground_root=worktree,
                    command_x=command,
                    duration_s=12.0,
                    bridge_mode="fitted",
                    expected_observation_dim=115,
                    expected_action_dim=14,
                    task="flat_terrain_backlash",
                    seed=167931544,
                    eval_role="runtime_handoff_golden",
                    trace_jsonl=trace,
                    trace_full_obs=True,
                    policy_obs_input_name="obs",
                    policy_action_output_name="continuous_actions",
                    policy_state_input_names=("previous_action",),
                    policy_state_output_names=("previous_action_out",),
                    policy_applied_target_observation=True,
                    policy_observer_fit=fit,
                    reference_feature_table_path=reference,
                    reference_start_phase=0,
                    policy_phase_advance_before_observation=False,
                    reset_mode="home-support",
                    trace_oracle_state=True,
                )
            )
            mode = result.get("modes", {}).get("fitted", {})
            if mode.get("samples") != 600 or mode.get("termination_reason") != "duration_complete":
                raise SystemExit(f"incomplete cell: step={step} command={command}")
            comparison = compare_to_frozen(step, command, trace)
            if not comparison["exact"]:
                raise SystemExit(f"fresh trace differs from frozen: {comparison}")
            result_path = output / f"winner_v2_{step}_x{command:.3f}_result.json"
            result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            cells.append(
                {
                    "step": step,
                    "command_x": command,
                    "sim_status": result.get("status"),
                    "samples": mode.get("samples"),
                    "termination_reason": mode.get("termination_reason"),
                    "comparison": comparison,
                }
            )

    summary = {
        "status": "PASS_WINNER_V2_HANDOFF_TRACE_GENERATION",
        "execution": {
            "cpu_only": True,
            "robot_or_rdk": False,
            "gpu_or_igpu": False,
            "training": False,
        },
        "control_commit": CONTROL_COMMIT,
        "patch_hashes": PATCH_HASHES,
        "network_hash": NETWORK_HASH,
        "cells": cells,
    }
    summary_path = output / "winner_v2_handoff_trace_generation.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": summary["status"], "summary": str(summary_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
