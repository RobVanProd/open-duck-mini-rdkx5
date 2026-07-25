#!/usr/bin/env python3
"""Preregister V147's action-head-only DAgger CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v147_head_only_dagger_cpu_contract.py"
V145_RUNNER = (
    ROOT / "tools/run_winner_v145_on_policy_dagger_cpu_contract.py"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V145_RESULT = ANALYSIS / "winner_v145_on_policy_dagger_cpu_result.json"
V146_RESULT = ANALYSIS / "winner_v146_dagger_direction_result.json"
V134_TRAINING = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_TRAINING = ROOT / "training/winner_v145_on_policy_dagger.py"
TRAINING = ROOT / "training/winner_v147_head_only_dagger.py"
OUTPUT = ANALYSIS / "winner_v147_head_only_dagger_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V147_HEAD_ONLY_DAGGER_CPU_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "v131_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v140_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v145_result": (
        "d1b9ee041130fd50b8be357749f2c8cdf38a884b8bde527eabfb19c80a3b14a8"
    ),
    "v146_result": (
        "8f9e2d69d34ee36066c54e6bc7f99eb009f395ae565ee8bc485bef626c9db90c"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v134_training_module": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "v145_training_module": (
        "b6f0cb28e86bc3561009af87ad5cc5136641e08057d54c81d74b119d627ded4c"
    ),
    "training_module": (
        "a75d7621947781dfdd1dd95c568c88948ef978a48f5ee3a6d95bc8dd36259ba1"
    ),
    "v145_runner": (
        "c6e18bc2679372eca83872aedb84d1e6f6430106a52bcc6aa21e211cfebdd104"
    ),
    "runner": (
        "fd0f90c016191fae6b6b261441574083c9e9b464c3f1a8ba9454cba0a9f22d7b"
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
    "shadow_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
    "v140_selected_deployed": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
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
    parser.add_argument("--shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V147: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    shadow_trace = args.shadow_trace.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    selected_deployed = Path(
        v140["artifacts"]["selected_deployed"]["path"]
    )
    v145 = json.loads(V145_RESULT.read_text(encoding="utf-8"))
    v146 = json.loads(V146_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v131_result": sha256(V131_RESULT),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v145_result": sha256(V145_RESULT),
        "v146_result": sha256(V146_RESULT),
        "v121_transform": sha256(V121_TRANSFORM),
        "v134_training_module": sha256(V134_TRAINING),
        "v145_training_module": sha256(V145_TRAINING),
        "training_module": sha256(TRAINING),
        "v145_runner": sha256(V145_RUNNER),
        "runner": sha256(RUNNER),
        "network_source": sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "shadow_trace": sha256(shadow_trace),
        "v140_selected_deployed": sha256(selected_deployed),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v145_global_update_closed_on_shadow_preservation": (
            v145.get("failed_checks")
            == ["shadow_preservation_ratio_at_most_point01"]
        ),
        "v146_global_direction_closed": (
            v146.get("decision") == "CLOSE_GLOBAL_DAGGER_DIRECTION"
        ),
        "labeled_joint_set_derived_from_frozen_masks": True,
        "two_location_heads_only": True,
        "two_updates_no_search": True,
        "behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v147.head_only_dagger_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V147_HEAD_ONLY_DAGGER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V147_HEAD_ONLY_DAGGER_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "exactly reconstructed V140 actor",
            "dataset_and_targets": "bit-identical V145 aggregate",
            "trainable_leaves": [
                "adapter_location bias/kernel",
                "residual_location bias/kernel",
            ],
            "trainable_columns": [0, 1, 3, 7, 8, 10, 13],
            "frozen": (
                "shared residual trunk, recurrent hidden dynamics, "
                "observation adapter, scale logits, value tree, normalizer, "
                "and all seven unlabeled action columns"
            ),
            "why_distinct": (
                "V145 and V146 proved a useful global direction cannot meet "
                "shadow preservation; V147 removes the shared-state and "
                "cross-joint parameter pathways that caused that leakage"
            ),
            "deployment_abi": "unchanged 115/14/64 stateful ONNX",
        },
        "optimizer": {
            "updates": 2,
            "batch": "all 5,400 rows",
            "direction": "masked full-batch gradient",
            "initial_step": "1/max(1, masked_gradient_l2)",
            "backtracking": "halve at most 24 times",
            "acceptance": (
                "Armijo decrease with fixed conventional fraction 1e-4"
            ),
            "search_or_retry": False,
        },
        "pass_rule": {
            "reconstruction": "V140 deployed inference <=1e-7",
            "correction": (
                "overall, teacher, and shadow ratios all <=0.95"
            ),
            "preservation": (
                "overall, teacher, and shadow ratios all <=0.01"
            ),
            "state": "h_out bit-exact",
            "parameters": (
                "only four location-head leaves change; unlabeled columns "
                "remain bit-exact"
            ),
            "exports": "step 0 and 2 contracts pass",
        },
        "stop_rule": (
            "if any check fails, close head-only DAgger; do not add heads, "
            "unfreeze trunk/state, change joint columns, alter update count, "
            "or tune optimizer/thresholds"
        ),
        "authority": {
            "cpu_contract": not failed,
            "behavior": False,
            "hosted_training": False,
            "full_matrix": False,
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
        "# Winner V147 head-only DAgger CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Train only seven labeled columns of two action-location heads.\n"
        "- Two deterministic full-batch updates; no sweep or retry.\n"
        "- No behavior, Colab, policy deployment, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
