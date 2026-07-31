#!/usr/bin/env python3
"""Freeze T185's distinct in-episode single-support CPU contract."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS
    / "t185_in_episode_single_support_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185_IN_EPISODE_SINGLE_SUPPORT_CPU_PREREGISTRATION_20260730.md"
)
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_original_driver_wrapper_package_v1/"
    "t100c_original_driver_wrapper_bundle/playground"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t185_in_episode_single_support_cpu_source_v1"
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
POLY = (
    BASE
    / "playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"
)
POLY_MODULE = (
    BASE / "playground/common/poly_reference_motion_numpy.py"
)
CONSTANTS = BASE / "playground/open_duck_mini_v2/constants.py"
BASE_JOYSTICK = BASE / "playground/open_duck_mini_v2/joystick.py"
T55_MODULE = ROOT / "patches/t55_dynamic_single_support_curriculum.py"
T55_RESULT = ANALYSIS / "t55_dynamic_single_support_cpu_result.json"
T56_VALIDATION = ANALYSIS / "t56_recovered_training_validation.json"
T60_RESULT = ANALYSIS / "t60_t59_persistence_hold_attribution.json"
T61_RESULT = ANALYSIS / "t61_midpoint_gait_transfer_cpu_result.json"
T64_RESULT = ANALYSIS / "t64_t62_nominal_matrix_result.json"
T65_RESULT = ANALYSIS / "t65_t62_midpoint_endpoint_screen_result.json"
T171_VALIDATION = ANALYSIS / "t171_t170_recovered_training_validation.json"
T173_RESULT = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
T179_RESULT = ANALYSIS / "t179_source_vs_t175_positive_z_result.json"
T184B_RESULT = (
    ANALYSIS / "t184b_bilateral_single_support_anatomy_result.json"
)
BUILDER = Path(__file__).resolve()
MODULE = ROOT / "patches/t185_in_episode_single_support_prefix.py"
PATCH = (
    ROOT / "patches/winner_t185_in_episode_single_support_prefix.patch"
)
COMPOSER = (
    ROOT / "tools/compose_t185_in_episode_single_support_playground.py"
)
ENV_WORKER = ROOT / "tools/run_t185_environment_contract_worker.py"
RUNNER = ROOT / "tools/run_t185_in_episode_single_support_cpu_contract.py"
TEST = ROOT / "tests/test_t185_in_episode_single_support_prefix.py"


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


def load_poly_module():
    spec = importlib.util.spec_from_file_location("t185_poly_numpy", POLY_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen reference-motion module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def circular_runs(
    rows: Sequence[tuple[int, int]], target: tuple[int, int]
) -> list[list[int]]:
    indices = [index for index, value in enumerate(rows) if value == target]
    if not indices:
        return []
    period = len(rows)
    starts = [
        index
        for index in indices
        if rows[(index - 1) % period] != target
    ]
    if not starts:
        return [list(range(period))]
    runs = []
    for start in starts:
        run = []
        cursor = start
        while rows[cursor] == target:
            run.append(cursor)
            cursor = (cursor + 1) % period
            if cursor == start:
                break
        runs.append(run)
    return runs


def reference_contract() -> dict[str, Any]:
    module = load_poly_module()
    prm = module.PolyReferenceMotion(str(POLY))
    command = (0.077, 0.0, 0.0)
    nearest = (
        float(prm.dxs[int(np.argmin(np.abs(np.asarray(prm.dxs) - command[0])))]),
        float(prm.dys[int(np.argmin(np.abs(np.asarray(prm.dys) - command[1])))]),
        float(
            prm.dthetas[
                int(np.argmin(np.abs(np.asarray(prm.dthetas) - command[2])))
            ]
        ),
    )
    contacts = []
    for phase in range(prm.nb_steps_in_period):
        frame = np.asarray(
            prm.get_reference_motion(*command, phase), dtype=np.float64
        )
        contacts.append(
            tuple(int(value) for value in (frame[32:34] > 0.5))
        )
    longest: dict[str, list[int]] = {}
    anchors: dict[str, int] = {}
    for name, target in (
        ("left", (1, 0)),
        ("right", (0, 1)),
    ):
        runs = circular_runs(contacts, target)
        maximum = max(len(run) for run in runs)
        candidates = [run for run in runs if len(run) == maximum]
        if len(candidates) != 1:
            raise RuntimeError(f"nonunique {name} reference support run")
        run = candidates[0]
        anchor = run[(len(run) - 1) // 2]
        longest[name] = run
        anchors[name] = anchor
    old_mapping = {
        str(phase): (
            "left"
            if math.sin(phase / prm.nb_steps_in_period * 2 * math.pi)
            <= 0.0
            else "right"
        )
        for phase in anchors.values()
    }
    return {
        "period_s": float(prm.period),
        "fps": int(prm.fps),
        "period_ticks": int(prm.nb_steps_in_period),
        "query_command": list(command),
        "nearest_reference_cell": list(nearest),
        "contact_channels": [32, 34],
        "contact_order": ["left", "right"],
        "contact_sequence": [list(value) for value in contacts],
        "longest_circular_single_support_runs": longest,
        "lower_midpoint_rule": "run[(len(run)-1)//2]",
        "support_phase_anchors": anchors,
        "t55_phase_sign_mapping_at_t185_anchors": old_mapping,
        "t55_mapping_disagrees_with_reference_at_both_anchors": (
            old_mapping[str(anchors["left"])] == "right"
            and old_mapping[str(anchors["right"])] == "left"
        ),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T185: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185 preregistration requires clean worktree")
    required = (
        BASE,
        PLAYGROUND,
        SOURCE,
        TOPOLOGY,
    )
    if not all(path.is_dir() for path in required):
        raise FileNotFoundError("T185 directory input missing")
    files = (
        SOURCE_RAW,
        REFERENCE_FEATURES,
        GATE,
        POLY,
        POLY_MODULE,
        CONSTANTS,
        BASE_JOYSTICK,
        T55_MODULE,
        T55_RESULT,
        T56_VALIDATION,
        T60_RESULT,
        T61_RESULT,
        T64_RESULT,
        T65_RESULT,
        T171_VALIDATION,
        T173_RESULT,
        T179_RESULT,
        T184B_RESULT,
        BUILDER,
        MODULE,
        PATCH,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
    )
    if not all(path.is_file() for path in files):
        missing = [str(path) for path in files if not path.is_file()]
        raise FileNotFoundError(missing)
    histories = {
        "t55": load(T55_RESULT),
        "t56": load(T56_VALIDATION),
        "t60": load(T60_RESULT),
        "t61": load(T61_RESULT),
        "t64": load(T64_RESULT),
        "t65": load(T65_RESULT),
        "t171": load(T171_VALIDATION),
        "t173": load(T173_RESULT),
        "t179": load(T179_RESULT),
        "t184b": load(T184B_RESULT),
    }
    reference = reference_contract()
    manifest = load(PLAYGROUND / "T185_COMPOSED_SOURCE_MANIFEST.json")
    inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted((PLAYGROUND / "playground").rglob("*.py"))
    }
    source_validation = histories["t171"]["exports"]["checkpoints"][1]
    checks = {
        "t184b_earned_cpu_contract_only": (
            histories["t184b"]["status"]
            == "PASS_T184_BILATERAL_SINGLE_SUPPORT_ANATOMY"
            and histories["t184b"]["decision"]
            == (
                "EARN_T185_BILATERAL_SINGLE_SUPPORT_CURRICULUM_CPU_"
                "CONTRACT_PREREGISTRATION_ONLY"
            )
        ),
        "closed_prior_family_recorded": (
            histories["t55"]["status"]
            == "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            and histories["t60"]["status"]
            == "PASS_T60_T59_PERSISTENCE_HOLD_ATTRIBUTION"
            and histories["t61"]["status"]
            == "PASS_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
            and histories["t64"]["decision"]
            == "CLOSE_T62_MIDPOINT_GAIT_TRANSFER_CURRICULUM"
            and histories["t65"]["decision"]
            == "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
        ),
        "reference_period_exact": (
            reference["period_s"] == 0.54
            and reference["fps"] == 50
            and reference["period_ticks"] == 27
        ),
        "reference_anchors_unique_and_exact": (
            reference["support_phase_anchors"] == {
                "left": 2,
                "right": 15,
            }
            and reference["longest_circular_single_support_runs"]["left"]
            == [25, 26, 0, 1, 2, 3, 4, 5, 6]
            and reference["longest_circular_single_support_runs"]["right"]
            == [12, 13, 14, 15, 16, 17, 18, 19]
        ),
        "t55_support_mapping_is_reference_inverted": reference[
            "t55_mapping_disagrees_with_reference_at_both_anchors"
        ],
        "t170_half_source_identity_exact": (
            source_validation["path"] == str(SOURCE)
            and source_validation["directory_sha256"]
            == directory_sha256(SOURCE)
        ),
        "t170_half_is_near_green_source": (
            histories["t173"]["condition"]["green_cells"] == 15
            and histories["t173"]["blocks"][0]["checkpoint_id"]
            == "T170_COMPOSED_HALF"
            and histories["t179"]["summary"]["source_green_cells"] == 15
        ),
        "composed_manifest_exact": (
            manifest["schema_version"]
            == "open_duck.t185_composed_source.v1"
            and manifest["sources"]["patch"]["sha256"] == sha256(PATCH)
            and manifest["sources"]["module"]["sha256"] == sha256(MODULE)
            and manifest["final_python_hashes"] == inventory
        ),
        "no_behavior_optimizer_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t185_in_episode_single_support_cpu_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T185_IN_EPISODE_SINGLE_SUPPORT_CPU_CONTRACT"
            if not failed
            else "HOLD_T185_IN_EPISODE_SINGLE_SUPPORT_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can a reference-correct, bilateral, one-period support prefix "
            "transition into unchanged locomotion inside every episode while "
            "remaining default-off exact and trainable from T170 half?"
        ),
        "reference_contract": reference,
        "prior_family_distinction": {
            "t55_t56": (
                "phase kept cycling; phase-sign-selected support reward was "
                "trained in a separate balance stage, followed by an abrupt "
                "separate transfer stage"
            ),
            "t61_t62": (
                "separate 0.5 and 1.0 locomotion-weight optimizer stages; "
                "the homotopy family closed at 6/8"
            ),
            "t185": (
                "reference-contact-selected side and phase are held for the "
                "first 27 ticks, then unchanged locomotion phase and reward "
                "resume in the same episode with no optimizer-stage transfer"
            ),
            "mechanically_distinct": True,
            "manual_mass_com_foot_or_geometry_measurement": False,
        },
        "mechanism": {
            "source": "T170_COMPOSED_HALF",
            "source_joint_condition_green_count": "31/32 across Yneg/Zpos",
            "support_side_sampling": "Bernoulli(0.5) at reset",
            "support_phase_anchors": {"left": 2, "right": 15},
            "prefix_ticks": 27,
            "phase_during_prefix": "frozen at selected anchor",
            "reward_during_prefix": "support balance only",
            "post_prefix": (
                "advance from anchor+1 and restore unchanged locomotion "
                "reward in the same episode"
            ),
            "actor_update_scope": "negative_adapter_location_only",
            "critic_update": True,
            "normalizer_frozen": True,
            "policy_abi_change": False,
            "deployment_graph_change": False,
            "runtime_contract_change": False,
        },
        "sources": {
            "builder": file_receipt(BUILDER),
            "module": file_receipt(MODULE),
            "patch": file_receipt(PATCH),
            "composer": file_receipt(COMPOSER),
            "environment_worker": file_receipt(ENV_WORKER),
            "runner": file_receipt(RUNNER),
            "test": file_receipt(TEST),
            "base_joystick": file_receipt(BASE_JOYSTICK),
            "constants": file_receipt(CONSTANTS),
            "poly_module": file_receipt(POLY_MODULE),
            "t55_module": file_receipt(T55_MODULE),
            "t55_result": file_receipt(T55_RESULT),
            "t56_validation": file_receipt(T56_VALIDATION),
            "t60_result": file_receipt(T60_RESULT),
            "t61_result": file_receipt(T61_RESULT),
            "t64_result": file_receipt(T64_RESULT),
            "t65_result": file_receipt(T65_RESULT),
            "t171_validation": file_receipt(T171_VALIDATION),
            "t173_result": file_receipt(T173_RESULT),
            "t179_result": file_receipt(T179_RESULT),
            "t184b_result": file_receipt(T184B_RESULT),
        },
        "assets": {
            "source_checkpoint": directory_receipt(SOURCE),
            "source_raw_onnx": file_receipt(SOURCE_RAW),
            "cpu_topology_template": directory_receipt(TOPOLOGY),
            "reference_features": file_receipt(REFERENCE_FEATURES),
            "hidden_gate_static_asset": file_receipt(GATE),
            "polynomial_reference": file_receipt(POLY),
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "base_path": str(BASE.resolve()),
            "manifest": file_receipt(
                PLAYGROUND / "T185_COMPOSED_SOURCE_MANIFEST.json"
            ),
            "python_inventory": inventory,
            "python_inventory_sha256": canonical_sha256(inventory),
        },
        "cpu_contract": {
            "unit_tests": str(TEST.relative_to(ROOT)),
            "default_off_states": 9,
            "enabled_environment_count": 256,
            "enabled_environment_seed": 185,
            "enabled_environment_steps": 28,
            "required_phase_hold_ticks": 27,
            "required_resume_tick": 28,
            "optimizer_steps": 1024,
            "optimizer_envs": 8,
            "body_configuration_strata": 8,
            "exports": [0, 1024],
            "step_zero_tree_and_raw_onnx_exact": True,
            "both_support_side_metrics_positive": True,
            "formal_behavior_cells": 0,
        },
        "decision_rule": {
            "pass": (
                "EARN_T186_IN_EPISODE_SINGLE_SUPPORT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T185_IN_EPISODE_SINGLE_SUPPORT_PREFIX_AND_RETURN_"
                "TO_MECHANISM_SELECTION"
            ),
            "no_training_retry_from_cpu_result": True,
        },
        "checks": checks,
        "failed_checks": failed,
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
        "# T185 in-episode bilateral single-support CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Source: T170 half (`31/32` across the two decisive conditions)\n"
        "- Reference phases: left `2`, right `15`; prefix `27` ticks\n"
        "- Distinction: reference-contact mapping plus same-episode "
        "stand-to-walk transition\n"
        "- CPU optimizer / behavior / hosted / robot now: `0/0/0/0`\n"
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
