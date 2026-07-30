#!/usr/bin/env python3
"""Freeze T202's predicted-roll-risk CPU training contract."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t202_predicted_roll_risk_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T202_PREDICTED_ROLL_RISK_CPU_PREREGISTRATION_20260730.md"
)
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_original_driver_wrapper_package_v1/"
    "t100c_original_driver_wrapper_bundle/playground"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t202_predicted_roll_risk_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t170_colab_recovery_20260729/extracted/"
    "t170_eight_stratum_head_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_003907_1003520"
SOURCE_RAW = TRAINING / "2026_07_30_003907_1003520.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/t100c_half_cpu_remap"
)
REFERENCE_FEATURES = (
    ANALYSIS / "ground_up_projected_reference_feature_table.npz"
)
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
COMPOSED_MANIFEST = PLAYGROUND / "T202_COMPOSED_SOURCE_MANIFEST.json"
T201B_PREREG = (
    ANALYSIS / "t201b_roll_risk_source_transfer_preregistration.json"
)
T201B_RESULT = ANALYSIS / "t201b_roll_risk_source_transfer_result.json"
T199_RESULT = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
T198_RESULT = ANALYSIS / "t198_t194_targeted_y_negative_result.json"
BUILDER = Path(__file__).resolve()
MODULE = ROOT / "patches/t202_predicted_roll_risk.py"
PATCH = ROOT / "patches/winner_t202_predicted_roll_risk.patch"
COMPOSER = ROOT / "tools/compose_t202_predicted_roll_risk_playground.py"
ENV_WORKER = ROOT / "tools/run_t202_environment_contract_worker.py"
RUNNER = ROOT / "tools/run_t202_predicted_roll_risk_cpu_contract.py"
TEST = ROOT / "tests/test_t202_predicted_roll_risk.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode())
            digest.update(b"\0")
            with item.open("rb") as stream:
                for block in iter(
                    lambda: stream.read(1024 * 1024), b""
                ):
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


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "directory",
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def load_module():
    spec = importlib.util.spec_from_file_location("t202_contract", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load T202 module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T202: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T202 preregistration requires clean worktree")
    required_dirs = (BASE, PLAYGROUND, SOURCE, TOPOLOGY)
    required_files = (
        SOURCE_RAW,
        REFERENCE_FEATURES,
        GATE,
        COMPOSED_MANIFEST,
        T201B_PREREG,
        T201B_RESULT,
        T199_RESULT,
        T198_RESULT,
        BUILDER,
        MODULE,
        PATCH,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
    )
    if not all(path.is_dir() for path in required_dirs):
        raise FileNotFoundError("T202 required directory missing")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("T202 required file missing")

    t201b_prereg = load(T201B_PREREG)
    t201b = load(T201B_RESULT)
    t199 = load(T199_RESULT)
    t198 = load(T198_RESULT)
    module = load_module()
    failure_rows = sum(
        int(item["exceedance_rows"])
        for item in t201b["failure_summaries"].values()
    )
    failure_integral = sum(
        float(item["squared_excess_integral"])
        for item in t201b["failure_summaries"].values()
    )
    derived_scale = 0.4 * failure_rows / failure_integral
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    checks = {
        "t201b_earns_only_t202_cpu_preregistration": (
            t201b["status"] == "PASS_T201B_ROLL_RISK_SOURCE_TRANSFER"
            and t201b["separation_rule_passed"]
            and t201b["decision"]
            == (
                "EARN_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "combined_population_is_eighteen_passes_two_failures": (
            len(t201b["trace_summaries"]) == 20
            and sum(
                bool(item["cell_green"])
                for item in t201b["trace_summaries"].values()
            )
            == 18
            and len(t201b["failure_summaries"]) == 2
        ),
        "module_horizon_and_envelope_exact": (
            module.PREDICTION_HORIZON_S
            == t201b["prediction_horizon_s"]
            == t201b_prereg["analysis"]["prediction_horizon_s"]
            and module.PASSING_ENVELOPE_RAD
            == t201b["combined_passing_envelope_rad"]
        ),
        "scale_is_alive_derived_once_from_both_failures": (
            failure_rows == 45
            and module.FROZEN_FAILURE_EXCEEDANCE_ROWS == failure_rows
            and module.FROZEN_FAILURE_SQUARED_EXCESS_INTEGRAL
            == failure_integral
            and module.ROLL_RISK_SCALE == derived_scale
            and derived_scale * failure_integral / failure_rows == 0.4
        ),
        "support_objective_continuation_is_closed": (
            t199["decision"]
            == (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_"
                "OBJECTIVE_CONTINUATION"
            )
        ),
        "t194_is_closed_without_checkpoint_selection": (
            t198["decision"]
            == (
                "CLOSE_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
                "CONTINUATION"
            )
        ),
        "source_is_exact_protected_t170_half": (
            SOURCE.name == "2026_07_30_003907_1003520"
            and SOURCE_RAW.stem == SOURCE.name
        ),
        "objective_is_after_existing_reward_clip": (
            "objective=original_clipped_reward_minus_cost"
            in PATCH.read_text(encoding="utf-8")
            and "reward = t202.curriculum_reward(reward, roll_risk_cost)"
            in PATCH.read_text(encoding="utf-8")
        ),
        "composed_source_inventory_present": bool(python_inventory),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": file_receipt(BUILDER),
        "module": file_receipt(MODULE),
        "source_patch": file_receipt(PATCH),
        "composer": file_receipt(COMPOSER),
        "environment_worker": file_receipt(ENV_WORKER),
        "runner": file_receipt(RUNNER),
        "unit_test": file_receipt(TEST),
    }
    assets = {
        "source_checkpoint": directory_receipt(SOURCE),
        "source_raw_onnx": file_receipt(SOURCE_RAW),
        "cpu_topology_template": directory_receipt(TOPOLOGY),
        "reference_features": file_receipt(REFERENCE_FEATURES),
        "hidden_gate_static_asset": file_receipt(GATE),
        "t201b_preregistration": file_receipt(T201B_PREREG),
        "t201b_result": file_receipt(T201B_RESULT),
        "t199_support_closure": file_receipt(T199_RESULT),
        "t198_t194_closure": file_receipt(T198_RESULT),
        "composed_source_manifest": file_receipt(COMPOSED_MANIFEST),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t202_predicted_roll_risk_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT",
        "mechanism": {
            "source": "T170_HALF",
            "risk": "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)",
            "prediction_horizon_s": module.PREDICTION_HORIZON_S,
            "passing_envelope_rad": module.PASSING_ENVELOPE_RAD,
            "unscaled_cost": "square(max(0, risk - envelope))",
            "scale": module.ROLL_RISK_SCALE,
            "scale_derivation": (
                "0.4 alive reward/tick * 45 frozen failure "
                "exceedance rows / 22.450151776859293 frozen squared "
                "excess integral"
            ),
            "objective": (
                "original_clipped_reward - scale * squared_excess"
            ),
            "cost_placement": "outside_existing_positive_reward_clip",
            "support_objective": False,
            "deployment_graph_change": False,
            "policy_abi_change": False,
            "trainable_actor_groups": ["negative_adapter_location"],
            "critic_trainable": True,
            "protected": [
                "mature actor outside negative_adapter_location",
                "observation normalizer",
                "policy ABI",
                "deployment action graph",
            ],
            "scalar_sweep": False,
        },
        "training_smoke": {
            "timesteps": 1024,
            "num_envs": 8,
            "environments_per_stratum": 1,
            "source_checkpoint": str(SOURCE),
            "export_steps": [0, 1024],
            "all_other_ppo_values": "bit_exact_T170",
        },
        "environment_contract": {
            "default_off_steps": 8,
            "enabled_source_policy_ticks": 108,
            "enabled_seed": 202,
            "synthetic_roll_rate_rad_s": 10.0,
            "metric_module_error": 0.0,
            "objective_subtraction_error": 0.0,
            "formal_behavior_cells": 0,
        },
        "expected_runner_readback": (
            "T202_PREDICTED_ROLL_RISK="
            "horizon_s=0.08,envelope_rad=0.3541802655745987,"
            "scale=0.80177631665518045,"
            "objective=original_clipped_reward_minus_cost,"
            "deployment_graph=unchanged"
        ),
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "base_path": str(BASE.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(
                python_inventory
            ),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T202_PREDICTED_ROLL_RISK_AND_RETURN_TO_"
                "MECHANISM_SELECTION"
            ),
            "no_hosted_run_from_preregistration_alone": True,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_cpu_contract": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T202 predicted-roll risk CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Source: exact protected T170 half\n"
        f"- Envelope / scale: `{module.PASSING_ENVELOPE_RAD:.12f}` / "
        f"`{module.ROLL_RISK_SCALE:.12f}`\n"
        "- Objective: derived squared predicted-roll excess, subtracted "
        "after the original positive reward clip\n"
        "- CPU optimizer / formal behavior / hosted / robot now: "
        "`0/0/0/0`\n"
        f"- Failed checks: `{failed}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
