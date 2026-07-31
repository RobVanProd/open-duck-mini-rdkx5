#!/usr/bin/env python3
"""Preregister T37's frozen-normalizer 1,024-step CPU smoke."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import run_t20_support_trainthrough_one_update as t20
from run_t37_frozen_normalizer_cpu_smoke import (
    checkpoint_normalizer,
    normalizer_manifest,
    uint64_count,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T31_PREREG = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
T31_RESULT = ANALYSIS / "t31_action_margin_trainthrough_cpu_result.json"
T36_RESULT = ANALYSIS / "t36_t32_actor_block_factorial_result.json"
RUNNER = ROOT / "tools" / "run_t37_frozen_normalizer_cpu_smoke.py"
PATCH = ROOT / "patches" / "winner_t37_frozen_observation_normalizer.patch"
COMPOSED = Path(r"D:\CodexProjects\Open_Duck_Playground-composed-t37-v1")
BRAX_STATS = Path(
    r"D:\CodexArtifacts\venvs\open-duck-policy-py31213"
    r"\Lib\site-packages\brax\training\acme\running_statistics.py"
)
OUTPUT = ANALYSIS / "t37_frozen_normalizer_cpu_preregistration.json"
OUTPUT_MD = (
    ANALYSIS / "T37_FROZEN_NORMALIZER_CPU_PREREGISTRATION_20260727.md"
)


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": t20.sha256(path),
    }


def python_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): t20.sha256(path)
        for path in sorted(root.rglob("*.py"))
    }


def main() -> int:
    t31_prereg = json.loads(T31_PREREG.read_text(encoding="utf-8"))
    t31_result = json.loads(T31_RESULT.read_text(encoding="utf-8"))
    t36 = json.loads(T36_RESULT.read_text(encoding="utf-8"))
    source_cpu = Path(
        t31_result["cpu_topology_remap"]["remapped"]["path"]
    )
    source_manifest = normalizer_manifest(
        checkpoint_normalizer(source_cpu)
    )
    source_count = uint64_count(source_manifest)
    inventory = python_inventory(COMPOSED)
    common_runner = (
        COMPOSED / "playground/common/runner.py"
    ).read_text(encoding="utf-8")
    duck_runner = (
        COMPOSED / "playground/open_duck_mini_v2/runner.py"
    ).read_text(encoding="utf-8")
    freeze_source = (
        COMPOSED
        / "playground/common/t37_frozen_observation_normalizer.py"
    ).read_text(encoding="utf-8")
    brax_source = BRAX_STATS.read_text(encoding="utf-8")

    assets = {
        **t31_prereg["assets"],
        "source_cpu_remapped_checkpoint": {
            "kind": "directory",
            **t20.directory_receipt(source_cpu),
        },
    }
    sources = {
        "reference": t31_prereg["sources"]["reference"],
        "runner": file_receipt(RUNNER),
        "patch": file_receipt(PATCH),
        "t31_result": file_receipt(T31_RESULT),
        "t36_result": file_receipt(T36_RESULT),
        "brax_running_statistics": file_receipt(BRAX_STATS),
    }
    checks = {
        "t31_cpu_contract_green": (
            t31_result["status"]
            == "PASS_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
        ),
        "t36_selected_normalizer_freeze": (
            t36["status"]
            == "PASS_T36_T32_ACTOR_BLOCK_FACTORIAL_WITH_REPAIR"
            and t36["decision"]
            == "EARN_T37_NORMALIZER_HALF_"
            "FREEZE_TRAINING_CPU_CONTRACT_PREREGISTRATION"
            and t36["summary"]["selected_half_groups"] == ["normalizer"]
        ),
        "all_t36_factorial_variants_green": (
            t36["summary"]["green_cells"] == 6
            and all(cell["cell_green"] for cell in t36["cells"])
        ),
        "source_normalizer_count_positive": source_count > 0,
        "source_normalizer_manifest_complete": (
            "count/hi" in source_manifest["leaves"]
            and "count/lo" in source_manifest["leaves"]
            and any(
                name.startswith("mean/")
                for name in source_manifest["leaves"]
            )
            and any(
                name.startswith("std/")
                for name in source_manifest["leaves"]
            )
        ),
        "welford_builtin_cutoff_is_not_a_freeze": (
            "if state.mode == NormalizationMode.EMA:" in brax_source
            and "rate = jnp.where(count_float > until_count, 0.0, rate)"
            in brax_source
            and brax_source.count("until_count") >= 3
        ),
        "explicit_identity_update_present": (
            "return state" in freeze_source
            and "running_statistics.update = _frozen_update"
            in freeze_source
            and "running_statistics.update = original" in freeze_source
        ),
        "normalization_not_disabled": (
            "normalize_observations" not in freeze_source
        ),
        "runner_context_is_default_off": (
            'getattr(\n            self.args, '
            '"winner_t37_freeze_observation_normalizer", False'
            in common_runner
        ),
        "t37_requires_t31": (
            "T37 frozen observation normalizer requires T31" in duck_runner
        ),
        "composed_source_inventory_complete": (
            len(inventory) >= 31
            and "playground/common/t37_frozen_observation_normalizer.py"
            in inventory
        ),
        "all_sources_and_assets_present": all(
            Path(item["path"]).exists()
            for item in (*sources.values(), *assets.values())
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t37_frozen_normalizer_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T37_FROZEN_NORMALIZER_CPU_SMOKE"
            if not failed
            else "HOLD_T37_FROZEN_NORMALIZER_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can the exact T23 half checkpoint take one finite T31 PPO "
            "update while every restored observation-normalizer leaf remains "
            "bit-exact?"
        ),
        "selection_evidence": {
            "source": "T36 frozen six-variant actor-block factorial",
            "all_variants_green": True,
            "selected_variant": "NORMALIZER_HALF",
            "selected_mechanism": (
                "Continue T31 with the mature T23-half observation "
                "normalizer frozen while actor and critic remain trainable."
            ),
            "selection_precedence": (
                "lowest-complexity one-block repair; no hybrid promotion"
            ),
            "reward_changes": 0,
            "new_scalar_search": False,
        },
        "normalizer_contract": {
            "source": "exact T23 half checkpoint",
            "source_count": source_count,
            "source_manifest": source_manifest,
            "mode": "welford",
            "normalization_enabled": True,
            "freeze_mechanism": "temporary_identity_update_context",
            "freeze_scope": "Brax running_statistics.update during train call",
            "restoration": "original update restored in finally",
            "policy_and_critic_trainable": True,
        },
        "transition": {
            "flag": "--winner_t37_freeze_observation_normalizer",
            "default_off": True,
            "requires": "--winner_t31_action_margin_trainthrough",
            "environment_changes": 0,
            "reward_changes": 0,
            "deployment_graph_changes": 0,
        },
        "cpu_smoke": {
            "simulator_steps": 1024,
            "ppo_envs": 4,
            "exports": [0, 1024],
            "restore": "T23_SUPPORT_HALF step 1003520",
            "checks": [
                "source restore and step-zero deployment hashes exact",
                "all normalizer leaves and count bit-exact at step 1024",
                "observation normalization remains enabled",
                "every policy and critic leaf updates and remains finite",
                "T19 and T31 transitions remain enabled",
                "both deployment action-margin contracts pass",
                "no behavior selection, hosted compute, or robot access",
            ],
        },
        "playground": {
            "path": str(COMPOSED.resolve()),
            "python_inventory": inventory,
            "python_inventory_sha256": t20.canonical_sha256(inventory),
        },
        "sources": sources,
        "assets": assets,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Authorize only a separate T38 hosted-continuation "
                "preregistration. Do not launch hosted compute."
            ),
            "fail": (
                "Close T37 without hosted training or behavior evaluation."
            ),
        },
        "authority": {
            "execute_1024_cpu_steps": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = t20.canonical_sha256(
        payload
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T37 frozen-normalizer CPU preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                f"- frozen observation count: `{source_count}`",
                "- CPU simulator steps: `1,024`",
                "- Exports: `0 / 1,024`",
                "- Reward changes / hosted / robot: `0 / 0 / 0`",
                "",
                "Passing authorizes only a separate T38 hosted "
                "preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed}")
    print(f"source_count={source_count}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={t20.sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
