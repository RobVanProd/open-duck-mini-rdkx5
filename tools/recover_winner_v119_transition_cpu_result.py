#!/usr/bin/env python3
"""Recover V119 CPU evidence after its reporting-only JSON bool failure."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import tempfile

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    sha256_directory,
    tree_errors,
)
from run_winner_v119_transition_cpu_smoke import (  # noqa: E402
    MARKDOWN,
    METRIC_TAG,
    PREREG,
    PREREG_SHA256,
    RESULT,
    deployed_onnx_contract,
    scalar_events,
    sha256,
)


FAILED_STDERR_SHA256 = (
    "3ee98ae25a5390f91a33f39de9ee0c5b08aca50a8fb8e1f1d416d9341ffb9159"
)
FAILED_STDOUT_SHA256 = (
    "cf0406ec4296d7e2dba1170821db35106e641985a007999a905dae2a5c00ae17"
)
TRAINING_LOG_SHA256 = (
    "6cb2bc6fd45ea77abe1671d4a6add2e0c5584490e329a169a37c250196dc3084"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--launch-stdout", type=Path, required=True)
    parser.add_argument("--launch-stderr", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    work = args.work_root.resolve()
    launch_stdout = args.launch_stdout.resolve()
    launch_stderr = args.launch_stderr.resolve()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V119 recovered result")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("V119 preregistration changed")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    stderr_text = launch_stderr.read_text(encoding="utf-8")
    reporting_failure_exact = (
        sha256(launch_stderr) == FAILED_STDERR_SHA256
        and "TypeError: Object of type bool is not JSON serializable"
        in stderr_text
        and stderr_text.count("Traceback (most recent call last):") == 1
    )
    if (
        sha256(launch_stdout) != FAILED_STDOUT_SHA256
        or sha256(work / "training.log") != TRAINING_LOG_SHA256
        or not reporting_failure_exact
    ):
        raise ValueError("V119 failed-launch evidence changed")

    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        WINNER_V119_GUARD_MARGIN_RAD,
        WINNER_V119_PITCH_MASK,
        WINNER_V119_RATE_LIMITS_RAD_S,
        default_config,
        winner_v119_transition_match,
    )

    rng = np.random.default_rng(20260724)
    proposed = rng.uniform(-1.0, 1.0, (128, 14)).astype(np.float32)
    previous = rng.uniform(-0.5, 0.5, (128, 14)).astype(np.float32)
    actual = rng.uniform(-0.5, 0.5, (128, 14)).astype(np.float32)
    rates = np.asarray(WINNER_V119_RATE_LIMITS_RAD_S, dtype=np.float32)
    disabled = np.asarray(
        winner_v119_transition_match(
            jax.numpy.asarray(proposed),
            jax.numpy.asarray(previous),
            jax.numpy.asarray(actual),
            jax.numpy.asarray(rates),
            0.02,
            False,
        )
    )
    enabled = np.asarray(
        winner_v119_transition_match(
            jax.numpy.asarray(proposed),
            jax.numpy.asarray(previous),
            jax.numpy.asarray(actual),
            jax.numpy.asarray(rates),
            0.02,
            True,
        )
    )
    margin = np.float32(WINNER_V119_GUARD_MARGIN_RAD)
    mask = np.asarray(WINNER_V119_PITCH_MASK, dtype=np.bool_)
    guarded = np.clip(proposed, actual - margin, actual + margin)
    guarded = np.where(mask[None], guarded, proposed)
    expected = np.clip(
        guarded,
        previous - rates[None] * np.float32(0.02),
        previous + rates[None] * np.float32(0.02),
    )
    analytic_error = float(np.max(np.abs(enabled - expected)))
    max_rate_excess = float(
        np.max(
            np.abs(enabled - previous)
            - rates[None] * np.float32(0.02)
        )
    )
    config = default_config()
    expected_rates = np.asarray(
        prereg["transition"]["rate_limits_rad_s"], dtype=np.float32
    )

    output = work / "smoke"
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    raw_graphs = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(
        int(path.name.rsplit("_", 1)[1]) for path in checkpoints
    )
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in raw_graphs
    )
    if checkpoint_steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise ValueError(
            f"unexpected recovered exports: {checkpoint_steps}, {onnx_steps}"
        )
    initial_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_1024")
    )
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_restore_args = orbax_utils.restore_args_from_target(template)
    source_tree = checkpointer.restore(
        str(source), item=template, restore_args=source_restore_args
    )
    initial_restore_args = orbax_utils.restore_args_from_target(source_tree)
    initial_tree = checkpointer.restore(
        str(initial_checkpoint),
        item=source_tree,
        restore_args=initial_restore_args,
    )
    final_tree = checkpointer.restore(
        str(final_checkpoint),
        item=source_tree,
        restore_args=initial_restore_args,
    )
    initial_structure, initial_deltas = tree_errors(
        source_tree, initial_tree
    )
    trained_structure, trained_deltas = tree_errors(
        initial_tree, final_tree
    )
    policy_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("1/params/")
    }
    all_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )
    event_file = next(output.glob("events.out.tfevents*"))
    metric_rows = scalar_events(event_file, METRIC_TAG)

    existing_deployed = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in work.glob("v119_deployed_*.onnx")
    }
    deployed_rows = []
    with tempfile.TemporaryDirectory(prefix="winner_v119_recover_") as tmp:
        temporary = Path(tmp)
        for raw_path in raw_graphs:
            step = int(raw_path.stem.rsplit("_", 1)[1])
            recovered_path = temporary / f"deployed_{step}.onnx"
            row = deployed_onnx_contract(
                raw_path, recovered_path, prereg=prereg
            )
            row["step"] = step
            row["existing_deployed_sha256"] = sha256(
                existing_deployed[step]
            )
            row["recovered_matches_existing"] = (
                row["deployed_sha256"]
                == row["existing_deployed_sha256"]
            )
            deployed_rows.append(row)

    expected_io = {
        "inputs": {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    earliest = min(
        work.stat().st_ctime,
        launch_stdout.stat().st_ctime,
        launch_stderr.stat().st_ctime,
    )
    latest = max(
        path.stat().st_mtime
        for path in (
            [work / "training.log", launch_stdout, launch_stderr]
            + list(work.glob("v119_deployed_*.onnx"))
        )
    )
    wall_upper_bound = float(latest - earliest)
    checks = {
        "failed_launch_is_reporting_only": reporting_failure_exact,
        "training_not_rerun": True,
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "default_off_config_exact_false": (
            config.winner_v119_train_transition_match is False
        ),
        "default_off_transition_bit_exact": bool(
            np.array_equal(disabled, proposed)
        ),
        "enabled_transition_matches_analytic": analytic_error <= 1.0e-7,
        "enabled_final_rate_bound_exact": max_rate_excess <= 1.0e-7,
        "v117_rate_vector_float32_exact": bool(
            np.array_equal(rates, expected_rates)
        ),
        "guard_margin_exact": bool(
            float(margin) == np.float32(0.165)
        ),
        "exact_exports_0_and_1024": checkpoint_steps == [0, 1024]
        and onnx_steps == [0, 1024],
        "source_restore_structure_exact": initial_structure,
        "source_restore_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_structure_exact": trained_structure,
        "trained_tree_all_finite": bool(all_finite),
        "every_policy_leaf_updated": bool(policy_deltas)
        and all(value > 0.0 for value in policy_deltas.values()),
        "objective_metric_exact_steps": [
            row["step"] for row in metric_rows
        ]
        == [0, 1024],
        "objective_metric_finite_nonzero": bool(metric_rows)
        and all(
            math.isfinite(row["value"]) and row["value"] > 0.0
            for row in metric_rows
        ),
        "both_existing_deployed_graphs_reproduce": all(
            row["recovered_matches_existing"] for row in deployed_rows
        ),
        "both_deployed_onnx_abis_exact": all(
            row["graph_io"] == expected_io for row in deployed_rows
        ),
        "both_deployed_onnx_contracts_pass": all(
            row["inference"]["pass"] for row in deployed_rows
        ),
        "both_deployed_initializers_finite": all(
            row["initializers_finite"] for row in deployed_rows
        ),
        "wall_upper_bound_at_most_1800": wall_upper_bound <= 1800.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v119.transition_cpu_result.v1",
        "status": (
            "PASS_WINNER_V119_TRANSITION_CPU_SMOKE_RECOVERED"
            if not failed
            else "HOLD_WINNER_V119_TRANSITION_CPU_SMOKE_RECOVERED"
        ),
        "failed_checks": failed,
        "checks": checks,
        "recovery": {
            "classification": "reporting_only",
            "training_rerun": False,
            "failed_launch_stdout_sha256": sha256(launch_stdout),
            "failed_launch_stderr_sha256": sha256(launch_stderr),
            "cause": (
                "np.bool_ in the completed result payload was not converted "
                "to a native JSON boolean"
            ),
            "wall_seconds_upper_bound": wall_upper_bound,
        },
        "transition_contract": {
            "analytic_max_abs_error": analytic_error,
            "max_rate_excess_rad": max_rate_excess,
            "default_off_bit_exact": bool(
                np.array_equal(disabled, proposed)
            ),
            "rate_limits_float32": rates.tolist(),
            "guard_margin_rad": float(margin),
        },
        "training": {
            "checkpoint_steps": checkpoint_steps,
            "onnx_steps": onnx_steps,
            "initial_checkpoint_sha256": sha256_directory(
                initial_checkpoint
            ),
            "final_checkpoint_sha256": sha256_directory(final_checkpoint),
            "event_sha256": sha256(event_file),
            "log_sha256": sha256(work / "training.log"),
            "objective_metric": {
                "tag": METRIC_TAG,
                "events": metric_rows,
            },
            "policy_leaf_deltas": policy_deltas,
        },
        "deployed_onnx": deployed_rows,
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "source_checkpoint": sha256_directory(source),
            "playground_manifest": sha256(
                playground / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
            ),
        },
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v119 transition CPU result\n\n"
        f"Status: `{value['status']}`\n\n"
        "The 1,024-step training was not rerun. Its exact checkpoints, event "
        "file, raw ONNX, and already-written deployed ONNX were recovered "
        "after a reporting-only NumPy-boolean serialization failure. All "
        "mechanics, restore, update, and graph checks were recomputed. A pass "
        "authorizes only a separate hosted preregistration.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
