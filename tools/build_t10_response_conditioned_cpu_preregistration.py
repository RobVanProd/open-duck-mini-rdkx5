#!/usr/bin/env python3
"""Preregister the T10 response-conditioned V121 CPU software contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS
    / "t10_response_conditioned_continuation_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T10_RESPONSE_CONDITIONED_CONTINUATION_CPU_PREREGISTRATION_"
    "20260726.md"
)
DEFAULT_PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-t10-response-conditioned-v2"
)
DEFAULT_ASSETS = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t10_response_conditioned_assets_v1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--playground-root",
        type=Path,
        default=DEFAULT_PLAYGROUND,
    )
    parser.add_argument(
        "--assets-root",
        type=Path,
        default=DEFAULT_ASSETS,
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("T10 preregistration requires --write")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T10 preregistration")
    playground = args.playground_root.resolve()
    assets = args.assets_root.resolve()
    composed_manifest_path = (
        playground / "T10_COMPOSED_SOURCE_MANIFEST.json"
    )
    asset_manifest_path = assets / "manifest.json"
    composed = json.loads(
        composed_manifest_path.read_text(encoding="utf-8")
    )
    asset_manifest = json.loads(
        asset_manifest_path.read_text(encoding="utf-8")
    )
    if (
        composed.get("status") is not None
        or composed.get("manifest_sha256")
        != canonical_sha256(
            {
                key: value
                for key, value in composed.items()
                if key != "manifest_sha256"
            }
        )
    ):
        raise RuntimeError("T10 composed manifest changed")
    if (
        asset_manifest.get("status")
        != "PASS_T10_RESPONSE_CONDITIONED_ASSETS"
        or asset_manifest.get("failed_checks") != []
        or asset_manifest.get("manifest_sha256")
        != canonical_sha256(
            {
                key: value
                for key, value in asset_manifest.items()
                if key != "manifest_sha256"
            }
        )
        or not asset_manifest["step_zero_parity"][
            "all_outputs_bit_exact"
        ]
    ):
        raise RuntimeError("T10 zero-update assets are not green")

    repository_sources = {
        "builder": Path(__file__),
        "composer": (
            ROOT / "tools" / "compose_t10_response_conditioned_playground.py"
        ),
        "asset_builder": (
            ROOT / "tools" / "build_t10_response_conditioned_assets.py"
        ),
        "runner": (
            ROOT / "tools" / "run_t10_response_conditioned_cpu_contract.py"
        ),
        "independent_auditor": (
            ROOT / "tools" / "audit_t10_response_conditioned_cpu_contract.py"
        ),
        "network_source": (
            ROOT / "patches" / "t10_response_conditioned_v121_networks.py"
        ),
        "wrapper_source": (
            ROOT / "patches" / "t10_command_aware_response_wrapper.py"
        ),
        "t9_result": (
            ANALYSIS / "t9_command_aware_prefix_bypass_result.json"
        ),
        "t9_independent_audit": (
            ANALYSIS
            / "t9_command_aware_prefix_bypass_independent_audit_v2.json"
        ),
        "v119_recovered_validation": (
            ANALYSIS / "winner_v119_recovered_training_validation.json"
        ),
        "v121_deployment_contract": (
            ANALYSIS / "winner_v121_deployment_transform_contract.json"
        ),
        "reference_features": (
            ANALYSIS / "ground_up_projected_reference_feature_table.npz"
        ),
        "playground_manifest": composed_manifest_path,
        "asset_manifest": asset_manifest_path,
    }
    sources = {
        name: receipt(path) for name, path in repository_sources.items()
    }
    external_assets = {
        "expanded_checkpoint": directory_receipt(
            assets / "expanded_checkpoint"
        ),
        "step_zero_onnx": receipt(
            assets / "t10_v121_half_step_zero.onnx"
        ),
        "calibrator": asset_manifest["sources"]["calibrator"],
        "v121_half_policy": asset_manifest["sources"][
            "v121_half_policy"
        ],
    }
    basis = {
        "schema_version": "open_duck.t10_response_cpu_preregistration.v1",
        "status": "PREREGISTERED_T10_RESPONSE_CONDITIONED_CPU_CONTRACT",
        "question": (
            "Can the T9-selected command-aware response architecture be "
            "expanded from V121-half, preserve the complete step-zero policy "
            "and recurrent state exactly, execute one finite 1,024-step CPU "
            "PPO smoke, update both context paths, and export the complete "
            "stateful V121 graph without spending hosted compute?"
        ),
        "causal_basis": {
            "t7": (
                "universal support produces stable configuration-sensitive "
                "64-D response context"
            ),
            "t8": (
                "state-coherent direct handoff passes every moving cell"
            ),
            "t9": (
                "command-aware x=0 bypass completes the 16/16 architecture"
            ),
            "minimal_trainable_delta": (
                "add only zero-initialized context-to-hidden and "
                "context-to-action kernels to the restored V121-half actor"
            ),
        },
        "sources": sources,
        "assets": external_assets,
        "software_contract": {
            "source": "V121_TRAIN_MATCHED_HALF",
            "source_step": 1003520,
            "policy_observation_dim": 115,
            "runtime_observation_contract_dim": 101,
            "action_dim": 14,
            "recurrent_state_dim": 64,
            "calibration_context_dim": 64,
            "onnx_inputs_in_order": [
                "obs",
                "previous_action",
                "h_in",
                "calibration_context",
            ],
            "onnx_outputs_in_order": [
                "continuous_actions",
                "previous_action_out",
                "h_out",
            ],
            "step_zero": {
                "source_actor_and_normalizer": "bit exact",
                "context_kernels": "exact float32 zero",
                "arbitrary_context_effect": "exact zero",
                "complete_outputs": "bit exact to V121-half for 1,024 cases",
            },
            "moving_reset": {
                "universal_response_ticks": 250,
                "home_return_ticks": 0,
                "locomotion_hidden": "exact zero",
                "previous_action": "realized final response action",
                "applied_target_slot": "exact bridge-applied target",
                "phase": [1.0, 0.0],
            },
            "x0_reset": {
                "universal_response_ticks": 0,
                "context": "exact zero [64]",
                "hidden": "exact zero [64]",
                "previous_action": "exact zero [14]",
                "phase": [1.0, 0.0],
            },
            "deployment_hierarchy": [
                "raw recurrent response-conditioned actor",
                "exact trained rate vector",
                "0.165-rad actual-centered pitch guard",
                "x=0 deadband",
                "final exact trained rate projection",
                "restored x=0 deadband",
                "graph-owned previous_action_out",
            ],
        },
        "cpu_smoke": {
            "optimizer_steps_exact": 1024,
            "device": "CPU only",
            "seed": 100,
            "num_envs": 4,
            "num_evals": 2,
            "episode_length": 64,
            "unroll_length": 8,
            "batch_size": 4,
            "num_minibatches": 1,
            "updates_per_batch": 2,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "export_steps": [0, 1024],
            "maximum_wall_seconds": 3600,
            "required_checks": [
                "expanded checkpoint restores bit exactly at step 0",
                "all policy leaves update and remain finite",
                "both new context parameter families update",
                "critic updates and remains finite",
                "step-0 export remains bit exact to frozen zero-update asset",
                "step-1,024 graph has finite CPU inference",
                "context changes both recurrent state and final action",
                "x=0 remains exact zero",
                "moving rate and state feedback remain graph-owned",
                "moving and x=0 reset receipts match T9",
            ],
        },
        "decision_rule": {
            "pass": (
                "every runner check and every independently recomputed audit "
                "check passes"
            ),
            "pass_next_action": (
                "earn only one separately preregistered hosted continuation "
                "from the expanded V121-half source; do not launch it yet"
            ),
            "fail": (
                "hold hosted continuation, file the exact software-contract "
                "failure, and spend no Colab credits"
            ),
            "partial_results_selection_weight": 0,
            "no_closest_result_promotion": True,
        },
        "authority": {
            "cpu_optimizer_steps_authorized": 1024,
            "hosted_or_colab_compute": False,
            "formal_behavior_cells": 0,
            "policy_checkpoint_selection": False,
            "robot_or_rdkx5_access": False,
            "gate5": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T10 response-conditioned V121 CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: `V121_TRAIN_MATCHED_HALF`\n"
        "- Formal CPU optimizer steps authorized: `1,024`\n"
        "- Export steps: `0`, `1,024`\n"
        "- Hosted/Colab compute authorized: `no`\n"
        "- Behavior cells authorized: `0`\n"
        "- Robot/RDK-X5 access: `0`\n"
        "- Pass earns only a separately preregistered hosted continuation.\n"
        f"- Canonical contract SHA-256: "
        f"`{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"file_sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
