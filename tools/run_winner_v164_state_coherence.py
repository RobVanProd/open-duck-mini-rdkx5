#!/usr/bin/env python3
"""Run V164's preregistered accepted-state coherence screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np
import onnx
from onnx import numpy_helper
import optax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
from run_winner_v141_projected_final_behavior import (  # noqa: E402
    load_evaluator,
    run_cell,
)
from winner_v164_feasibility_preserving_state import (  # noqa: E402
    compose_accepted_checkpoint,
    finite_tree,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v164_state_coherence_preregistration.json"
OUTPUT = ANALYSIS / "winner_v164_state_coherence_result.json"
MARKDOWN = ANALYSIS / "WINNER_V164_STATE_COHERENCE_RESULT_20260725.md"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def tree_max_error(left: Any, right: Any) -> float:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return max(errors, default=0.0)


def initializer_map(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(path)
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def optimizer_zero_contract(state: Any) -> dict[str, Any]:
    leaves = [np.asarray(leaf) for leaf in jax.tree_util.tree_leaves(state)]
    integer = [leaf for leaf in leaves if np.issubdtype(leaf.dtype, np.integer)]
    floating = [
        leaf for leaf in leaves if np.issubdtype(leaf.dtype, np.floating)
    ]
    return {
        "all_finite": all(np.all(np.isfinite(leaf)) for leaf in leaves),
        "all_integer_counters_zero": all(
            np.count_nonzero(leaf) == 0 for leaf in integer
        ),
        "all_float_moments_zero": all(
            np.count_nonzero(leaf) == 0 for leaf in floating
        ),
        "leaves": len(leaves),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V164: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = {name: Path(path) for name, path in prereg["paths"].items()}
    if (
        evaluator_root / "composition_manifest.json"
    ).resolve() != paths["composition_manifest"].resolve():
        raise ValueError("V164 evaluator root differs from preregistration")
    input_file_names = {
        "builder",
        "runner",
        "state_module",
        "cell_runner",
        "deployer",
        "v121_preregistration",
        "v121_result",
        "v127_preregistration",
        "v127_result",
        "v163_result",
        "v126_preregistration",
        "base_preregistration",
        "composition_manifest",
        "composed_evaluator",
        "proposal_aux",
        "source_raw",
        "proposal_raw",
    }
    input_directory_names = {
        "source_checkpoint",
        "proposal_checkpoint",
        "proposal_cost_checkpoint",
    }
    observed_hashes = {
        **{
            name: sha256(paths[name])
            for name in sorted(input_file_names)
        },
        **{
            name: directory_sha256(paths[name])
            for name in sorted(input_directory_names)
        },
    }
    if (
        prereg["status"] != "PREREGISTERED_WINNER_V164_STATE_COHERENCE"
        or prereg["failed_checks"] != []
        or prereg["input_hashes"] != observed_hashes
    ):
        raise ValueError("V164 preregistration changed")

    checkpointer = ocp.PyTreeCheckpointer()
    source = checkpointer.restore(str(paths["source_checkpoint"]))
    proposal = checkpointer.restore(str(paths["proposal_checkpoint"]))
    proposal_cost = checkpointer.restore(
        str(paths["proposal_cost_checkpoint"])
    )
    alpha = float(prereg["state_rule"]["accepted_alpha"])
    accepted = compose_accepted_checkpoint(source, proposal, alpha)
    run_root.mkdir(parents=True)
    accepted_checkpoint = run_root / "accepted_checkpoint"
    checkpointer.save(str(accepted_checkpoint), accepted)
    restored = checkpointer.restore(str(accepted_checkpoint))

    playground = paths["playground"]
    sys.path.insert(0, str(playground))
    from brax.training.acme import running_statistics  # noqa: E402
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
    )
    from playground.common.winner_v127_constrained_ppo_losses import (  # noqa: E402
        PPONetworkParams,
    )

    normalizer = running_statistics.RunningStatisticsState(**accepted[0])
    accepted_for_export = [normalizer, accepted[1], accepted[2]]
    params = PPONetworkParams(
        policy=accepted[1],
        value=accepted[2],
        cost_value=proposal_cost,
    )
    optimizer = optax.chain(
        optax.clip_by_global_norm(1.0), optax.adam(0.0003)
    )
    optimizer_state = optimizer.init(params)
    optimizer_contract = optimizer_zero_contract(optimizer_state)

    raw_path = run_root / "winner_v164_accepted_raw.onnx"
    deployed_path = run_root / "winner_v164_accepted_deployed.onnx"
    transform = json.loads(V121_TRANSFORM.read_text(encoding="utf-8"))[
        "transform"
    ]
    export_reference_residual_recurrent_adapter_onnx(
        accepted_for_export,
        action_size=14,
        obs_size=115,
        hidden_size=64,
        output_path=raw_path,
        hidden_layer_sizes=(512, 256, 128),
        action_velocity_limits_rad_s=transform[
            "exact_train_effective_rate_rad_s"
        ],
        control_dt=float(transform["control_dt_s"]),
        action_scale=float(transform["action_scale_rad"]),
    )
    deployment = deploy_graph(raw_path, deployed_path, transform)

    source_initializers = initializer_map(paths["source_raw"])
    proposal_initializers = initializer_map(paths["proposal_raw"])
    accepted_initializers = initializer_map(raw_path)
    initializer_errors = {}
    for name, value in accepted_initializers.items():
        if name in {"obs_mean", "obs_std"}:
            expected = source_initializers[name]
        elif name in proposal_initializers:
            left = source_initializers[name]
            right = proposal_initializers[name]
            expected = (
                left.astype(np.float64)
                + alpha
                * (right.astype(np.float64) - left.astype(np.float64))
            ).astype(left.dtype)
        else:
            expected = source_initializers[name]
        initializer_errors[name] = float(
            np.max(np.abs(value - expected))
        )
    initializer_linf = max(initializer_errors.values(), default=0.0)

    aux = json.loads(paths["proposal_aux"].read_text(encoding="utf-8"))
    accepted_aux_path = run_root / "winner_v164_accepted_aux.json"
    accepted_aux = {
        "source": str(paths["proposal_aux"]),
        "source_sha256": sha256(paths["proposal_aux"]),
        "retained_exact": {
            key: aux[key]
            for key in ("eta", "initial_cost", "initialized", "lambda")
        },
        "accepted_alpha": alpha,
        "optimizer_reset": True,
        "normalizer_frozen": True,
    }
    accepted_aux_path.write_text(
        json.dumps(accepted_aux, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    evaluator = load_evaluator(paths["composed_evaluator"])
    v126 = json.loads(paths["v126_preregistration"].read_text(encoding="utf-8"))
    base = json.loads(paths["base_preregistration"].read_text(encoding="utf-8"))
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cells = []
    started = time.time()
    for index, source_row in enumerate(
        prereg["matrix"]["rows_in_source_margin_risk_order"], start=1
    ):
        row = dict(source_row)
        row["checkpoint_id"] = "V164_ACCEPTED_STATE"
        row["policy_sha256"] = sha256(deployed_path)
        stem = (
            f"v164_{str(row['plant']).lower()}_"
            f"x{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = run_cell(
            evaluator=evaluator,
            row=row,
            policy=deployed_path,
            playground=Path(v126["external_inputs"]["playground"]),
            base_prereg=base,
            trace_path=trace_path,
            cpu_only=cpu_only,
        )
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        cell["cell_sha256"] = sha256(cell_path)
        cells.append(cell)
        print(
            json.dumps(
                {
                    "completed": index,
                    "total": 6,
                    "plant": row["plant"],
                    "command_x": row["command_x_m_s"],
                    "pass": cell["pass"],
                    "failures": cell["failure_reasons"],
                    "peak_torque_nm": cell.get("torque_gate", {}).get(
                        "worst_peak_torque_nm"
                    ),
                }
            ),
            flush=True,
        )
        if not cell["pass"]:
            break

    all_six = len(cells) == 6 and all(cell["pass"] for cell in cells)
    worst_torque = max(
        (
            cell["torque_gate"]["worst_peak_torque_nm"]
            for cell in cells
        ),
        default=float("inf"),
    )
    source_worst = float(prereg["source_worst_peak_torque_nm"])
    checks = {
        "cpu_only": cpu_only,
        "accepted_tree_finite": finite_tree(accepted),
        "accepted_checkpoint_restore_exact": (
            tree_max_error(accepted, restored) == 0.0
        ),
        "normalizer_source_bit_exact": (
            tree_max_error(accepted[0], source[0]) == 0.0
        ),
        "reward_critic_proposal_bit_exact": (
            tree_max_error(accepted[2], proposal[2]) == 0.0
        ),
        "cost_critic_proposal_finite": finite_tree(proposal_cost),
        "dual_state_proposal_exact": (
            accepted_aux["retained_exact"]
            == {
                key: aux[key]
                for key in ("eta", "initial_cost", "initialized", "lambda")
            }
        ),
        "optimizer_reset_all_finite": optimizer_contract["all_finite"],
        "optimizer_reset_counters_zero": optimizer_contract[
            "all_integer_counters_zero"
        ],
        "optimizer_reset_moments_zero": optimizer_contract[
            "all_float_moments_zero"
        ],
        "export_initializer_contract_linf_at_most_1e_7": (
            initializer_linf <= 1.0e-7
        ),
        "deployment_contract_green": deployment["inference"]["pass"],
        "x0_deadband_exact": (
            deployment["inference"]["checks"]["zero_action_exact"]
            and deployment["inference"]["checks"]["zero_previous_exact"]
        ),
        "all_six_moving_cells_pass": all_six,
        "source_worst_torque_strictly_improved": worst_torque < source_worst,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    payload = {
        "schema_version": "winner_v164.state_coherence_result.v1",
        "status": (
            "PASS_WINNER_V164_STATE_COHERENCE"
            if passed
            else "HOLD_WINNER_V164_STATE_COHERENCE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "state": {
            "accepted_alpha": alpha,
            "accepted_checkpoint": {
                "path": str(accepted_checkpoint),
                "sha256": directory_sha256(accepted_checkpoint),
            },
            "accepted_aux": {
                "path": str(accepted_aux_path),
                "sha256": sha256(accepted_aux_path),
            },
            "proposal_cost_checkpoint": {
                "path": str(paths["proposal_cost_checkpoint"]),
                "sha256": directory_sha256(
                    paths["proposal_cost_checkpoint"]
                ),
            },
            "optimizer_reset": optimizer_contract,
        },
        "export": {
            "raw": {"path": str(raw_path), "sha256": sha256(raw_path)},
            "deployed": deployment,
            "initializer_linf": initializer_linf,
            "initializer_errors": initializer_errors,
        },
        "cells": cells,
        "summary": {
            "moving_cells_completed": len(cells),
            "moving_cells_passing": sum(cell["pass"] for cell in cells),
            "source_worst_peak_torque_nm": source_worst,
            "candidate_worst_peak_torque_nm": (
                worst_torque if np.isfinite(worst_torque) else None
            ),
            "wall_seconds": time.time() - started,
        },
        "decision": (
            "EARN_V165_FEASIBILITY_PRESERVING_TRAINER_INTEGRATION_CPU_SMOKE"
            if passed
            else "CLOSE_ACTOR_ONLY_FROZEN_NORMALIZER_STATE_NO_RETRY"
        ),
        "authority": {
            "next_cpu_integration_smoke": passed,
            "training": False,
            "hosted_training": False,
            "full_robustness": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V164 state-coherence result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Moving cells: `{len(cells)}/6`; passing "
        f"`{sum(cell['pass'] for cell in cells)}`.\n"
        f"- Source/candidate worst torque: `{source_worst}` / "
        f"`{payload['summary']['candidate_worst_peak_torque_nm']}` N.m.\n"
        f"- Initializer contract L-inf: `{initializer_linf}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only; no new PPO update, Colab, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
