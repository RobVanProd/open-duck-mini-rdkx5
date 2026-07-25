#!/usr/bin/env python3
"""Run the frozen V169 V128-final first-R2 robustness-anchor screen."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

from aggregate_ground_up_robustness_r1 import summarize  # noqa: E402
from evaluate_ground_up_policy import evaluate  # noqa: E402
from run_winner_v10_r2_condition1 import (  # noqa: E402
    FIT_PATHS,
    exact_override_readback,
)
from run_winner_v7_full_behavior_revalidation import eval_args  # noqa: E402
from run_winner_v9_nominal_behavior import (  # noqa: E402
    git_head,
    sha256,
    trace_summary,
)

from build_winner_v169_v128_final_r2_anchor_preregistration import (  # noqa: E402
    frozen_paths,
)


PREREG = ANALYSIS / "winner_v169_v128_final_r2_anchor_preregistration.json"
CORRECTION = ANALYSIS / "winner_v169b_execution_input_correction.json"
RESULT = ANALYSIS / "winner_v169_v128_final_r2_anchor_result.json"
MARKDOWN = ANALYSIS / "WINNER_V169_V128_FINAL_R2_ANCHOR_RESULT_20260725.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V169: {path}")
    playground = args.playground_root.resolve()
    policy = args.policy.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    observed_hashes = {
        name: sha256(path) for name, path in frozen_paths().items()
    }
    expected_hashes = dict(prereg["input_hashes"])
    expected_hashes["runner"] = correction["corrected_runner_sha256"]
    observed_playground = {
        name: sha256(playground / name)
        for name in prereg["playground"]["required_file_hashes"]
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V169_V128_FINAL_R2_ANCHOR_SCREEN"
        or prereg.get("failed_checks") != []
        or correction.get("status")
        != "FROZEN_WINNER_V169B_EXECUTION_INPUT_CORRECTION"
        or correction.get("preregistration_sha256") != sha256(PREREG)
        or correction.get("prior_runner_sha256")
        != prereg["input_hashes"]["runner"]
        or expected_hashes != observed_hashes
        or sha256(policy) != prereg["policy"]["sha256"]
        or observed_playground
        != prereg["playground"]["required_file_hashes"]
        or git_head(playground) != prereg["playground"]["required_commit"]
    ):
        raise ValueError("V169 preregistration or frozen input changed")
    work.mkdir(parents=True)
    condition = prereg["condition"]
    override = condition["override"]
    matrix = prereg["matrix"]
    evaluator_matrix = dict(matrix)
    evaluator_matrix["frequency_hz"] = 50
    protection_gate = prereg["protection_gate"]
    matrices = {}
    all_traces = []
    started = time.time()
    for fit_id, fit_path in FIT_PATHS.items():
        block = work / "blocks" / fit_id
        block.mkdir(parents=True)
        eval_path = block / "eval.json"
        trace_dir = block / "traces"
        trace_dir.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            evaluation = evaluate(
                eval_args(
                    policy,
                    playground,
                    fit_path,
                    override,
                    eval_path,
                    trace_dir,
                    evaluator_matrix,
                )
            )
        eval_path.write_text(
            json.dumps(evaluation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        behavior = summarize(
            eval_path, prereg["behavior_gates"]["x0"], matrix["seed"]
        )
        traces = []
        for command in matrix["commands_x"]:
            trace_path = trace_dir / (
                f"x{command:.3f}_seed{matrix['seed']}_{policy.stem}.jsonl"
            )
            trace = trace_summary(trace_path, protection_gate)
            trace["command_x"] = command
            traces.append(trace)
            all_traces.append(trace)
        matrices[fit_id] = {
            "behavior": behavior,
            "protection_pass": all(trace["pass"] for trace in traces),
            "traces": traces,
            "override_and_readbacks_exact": (
                evaluation["inputs"].get("eval_dynamics_override")
                == override
                and exact_override_readback(evaluation, override)
            ),
            "eval_path": str(eval_path),
            "eval_sha256": sha256(eval_path),
        }
    checks = {
        "frozen_input_hashes_exact": observed_hashes
        == expected_hashes,
        "policy_hash_exact": sha256(policy) == prereg["policy"]["sha256"],
        "playground_commit_and_files_exact": (
            git_head(playground) == prereg["playground"]["required_commit"]
            and observed_playground
            == prereg["playground"]["required_file_hashes"]
        ),
        "exact_frozen_first_condition": (
            condition["id"] == "FLOOR_FRICTION_LO"
            and override == {"floor_friction": 0.5}
        ),
        "exactly_eight_complete_contiguous_cells": (
            len(all_traces) == 8
            and all(
                trace["rows"] == 600 and trace["ticks_contiguous"]
                for trace in all_traces
            )
        ),
        "both_behavior_matrices_pass": all(
            row["behavior"]["matrix_pass"] for row in matrices.values()
        ),
        "all_current_torque_duration_and_full_vector_gates_pass": all(
            row["protection_pass"] for row in matrices.values()
        ),
        "all_requested_overrides_and_readbacks_exact": all(
            row["override_and_readbacks_exact"]
            for row in matrices.values()
        ),
        "cpu_only_no_training_or_reward_selection": (
            os.environ["JAX_PLATFORMS"] == "cpu"
            and os.environ["CUDA_VISIBLE_DEVICES"] == ""
            and os.environ["HIP_VISIBLE_DEVICES"] == ""
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v169.v128_final_r2_anchor_result.v1",
        "status": (
            "PASS_WINNER_V169_V128_FINAL_R2_ANCHOR_SCREEN"
            if not failed
            else "HOLD_WINNER_V169_V128_FINAL_R2_ANCHOR_SCREEN"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "execution_input_correction_sha256": sha256(CORRECTION),
        "policy": prereg["policy"],
        "condition": condition,
        "matrices": matrices,
        "wall_seconds": time.time() - started,
        "decision": (
            "EARN_SAFE_SOURCE_ARCHITECTURE_CONTRACT_DESIGN_ONLY"
            if not failed
            else "CLOSE_V128_FINAL_AS_ROBUSTNESS_ANCHOR"
        ),
        "selection_weight": 0,
        "authority": {
            "safe_source_architecture_design": not failed,
            "later_r2_condition": False,
            "training": False,
            "hosted_training": False,
            "candidate_selection": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    worst_torque = max(
        float(trace["peak_torque_nm"])
        for trace in all_traces
        if trace["peak_torque_nm"] is not None
    )
    MARKDOWN.write_text(
        "# Winner V169 V128-final first-R2 anchor result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Worst peak torque: `{worst_torque}` N.m.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only CPU diagnostic with zero candidate-selection weight; "
        "no later R2 condition, training, hardware, torque, motion, or "
        "Gate 5 authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
