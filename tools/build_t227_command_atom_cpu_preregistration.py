#!/usr/bin/env python3
"""Freeze T227's deterministic command-atom CPU training contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t227_command_atom_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T227_COMMAND_ATOM_CPU_PREREGISTRATION_20260730.md"
)
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t215b_axis_complete_tilt_cpu_source_v1"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227_command_atom_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t216_colab_recovery_20260730/extracted/"
    "t216_axis_complete_tilt_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_165259_2007040"
SOURCE_RAW = TRAINING / "2026_07_30_165259_2007040.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/t100c_half_cpu_remap"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
MANIFEST = PLAYGROUND / "T227_COMPOSED_SOURCE_MANIFEST.json"
T226B = ANALYSIS / "t226b_t216_support_correction_result.json"
T217 = ANALYSIS / "t217_t216_recovered_training_validation.json"
T225 = ANALYSIS / "t225_global_plateau_full_r2_result.json"
BUILDER = Path(__file__).resolve()
MODULE = ROOT / "training/t227_command_atom_bank.py"
COMPOSER = ROOT / "tools/compose_t227_command_atom_playground.py"
ENV_WORKER = ROOT / "tools/run_t227_command_atom_environment_worker.py"
RUNNER = ROOT / "tools/run_t227_command_atom_cpu_contract.py"
TEST = ROOT / "tests/test_t227_command_atom_bank.py"


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


def receipt(path: Path) -> dict[str, Any]:
    if path.is_dir():
        return {
            "kind": "directory",
            "path": str(path.resolve()),
            "sha256": directory_sha256(path),
        }
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T227 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T227 preregistration requires clean worktree")
    required_dirs = (BASE, PLAYGROUND, SOURCE, TOPOLOGY)
    required_files = (
        SOURCE_RAW,
        REFERENCE,
        GATE,
        MANIFEST,
        T226B,
        T217,
        T225,
        BUILDER,
        MODULE,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
    )
    if not all(path.is_dir() for path in required_dirs):
        raise FileNotFoundError("T227 required directory missing")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("T227 required file missing")

    t226b = load(T226B)
    t217 = load(T217)
    t225 = load(T225)
    manifest = load(MANIFEST)
    module_text = MODULE.read_text(encoding="utf-8")
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    final_policy = next(
        item
        for item in t217["exports"]["policy_checkpoints"]
        if int(item["step"]) == 2_007_040
    )
    final_onnx = next(
        item
        for item in t217["exports"]["onnx"]
        if int(item["step"]) == 2_007_040
    )
    checks = {
        "t226b_earns_only_this_cpu_contract": (
            t226b["status"] == "PASS_T226B_T216_SUPPORT_CORRECTION"
            and t226b["failed_checks"] == []
            and t226b["decision"]
            == (
                "EARN_T227_COMMAND_ATOM_X_EXISTING_COM_BANK_CPU_"
                "CONTRACT_PREREGISTRATION_ONLY"
            )
        ),
        "t216_final_source_identity_exact": (
            Path(final_policy["path"]).resolve() == SOURCE.resolve()
            and final_policy["directory_sha256"]
            == directory_sha256(SOURCE)
            and final_onnx["sha256"] == sha256(SOURCE_RAW)
        ),
        "source_choice_is_mechanistic_not_checkpoint_selection": (
            t225["summary"]["first_failed_condition"]
            == "TORSO_COM_Z_POS"
            and all(
                block["result"]["green_cells"] == 8
                for block in t225["blocks"]
                if block["condition_id"] == "TORSO_COM_Z_POS"
                and block["checkpoint_id"]
                == "T222_GLOBAL_PLATEAU_FINAL"
            )
        ),
        "lattice_is_exact_and_parameter_free": (
            "CONFIGURATION_STRATA = 8" in module_text
            and "COMMAND_STRATA = 4" in module_text
            and "COMMAND_ATOMS_M_S = jnp.asarray(" in module_text
            and "[0.074, 0.077, 0.080]" in module_text
            and "population % CARTESIAN_STRATA != 0" in module_text
        ),
        "composed_scope_is_training_only": (
            manifest["schema_version"]
            == "open_duck.t227_composed_source.v1"
            and manifest["mechanism"]["configuration_randomizer_change"]
            is False
            and manifest["mechanism"]["reward_change"] is False
            and manifest["mechanism"]["cost_change"] is False
            and manifest["mechanism"]["policy_abi_change"] is False
            and manifest["mechanism"]["deployment_graph_change"] is False
        ),
        "composed_inventory_contains_exact_module": (
            python_inventory[
                "playground/common/t227_command_atom_bank.py"
            ]
            == sha256(MODULE)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T227 preregistration checks failed: {failed}")

    sources = {
        "builder": receipt(BUILDER),
        "command_atom_module": receipt(MODULE),
        "composer": receipt(COMPOSER),
        "environment_worker": receipt(ENV_WORKER),
        "runner": receipt(RUNNER),
        "unit_test": receipt(TEST),
    }
    assets = {
        "source_checkpoint": receipt(SOURCE),
        "source_raw_onnx": receipt(SOURCE_RAW),
        "cpu_topology_template": receipt(TOPOLOGY),
        "reference_features": receipt(REFERENCE),
        "hidden_gate_static_asset": receipt(GATE),
        "t226b_selection": receipt(T226B),
        "t217_source_validation": receipt(T217),
        "t225_full_r2_result": receipt(T225),
        "composed_source_manifest": receipt(MANIFEST),
    }
    mechanism = {
        "source": "T216_FINAL",
        "source_reason": (
            "the final checkpoint is the member that already passes all "
            "eight upper-Z cells; the new run is still judged at both "
            "preregistered exports"
        ),
        "configuration_strata": 8,
        "configuration_semantics": (
            "unchanged T216 one-broad plus seven isolated exact strata"
        ),
        "command_strata": [
            "broad_continuous_[.074,.080)",
            "exact_.074",
            "exact_.077",
            "exact_.080",
        ],
        "cartesian_strata": 32,
        "hosted_population_if_earned": 256,
        "hosted_repetitions_per_cartesian_stratum": 8,
        "cpu_population": 32,
        "cpu_repetitions_per_cartesian_stratum": 1,
        "reward_change": False,
        "cost_change": False,
        "axis_complete_tilt_dual_change": False,
        "actor_update_mask_change": False,
        "observation_change": False,
        "action_change": False,
        "policy_abi_change": False,
        "deployment_graph_change": False,
        "x_zero_handling_change": False,
        "global_command_transform_retry": False,
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t227_command_atom_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T227_COMMAND_ATOM_CPU_CONTRACT",
        "mechanism": mechanism,
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
        "expected_runner_readback": (
            "T227_COMMAND_ATOM_BANK="
            "configuration_strata=8,"
            "command_strata=4,"
            "command_groups=broad|0.074|0.077|0.080,"
            "cartesian_repetitions=1,"
            "reward=unchanged,cost=unchanged,"
            "policy_abi=unchanged,deployment_graph=unchanged"
        ),
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_if": [
                "default-off trajectory remains bit-exact",
                "the actual T19/vectorized reset contains all 32 configuration-command pairs exactly once on CPU",
                "the exact command atoms survive reset and resampling",
                "the T216-final policy restores bit-exactly",
                "only the already-authorized negative adapter head changes over 1024 steps",
                "reward and cost channels remain the T215B contract",
                "step-0 and step-1024 ONNX graphs retain the exact 115/14/64 stateful ABI",
            ],
            "pass": (
                "EARN_T228_COMMAND_ATOM_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_T227_COMMAND_ATOM_TRAINING_DISTRIBUTION",
            "hosted_runs_now": 0,
            "selection_weight": 0,
        },
        "execution_now": {
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_contract": True,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "gate5": False,
            "robot_or_rdk": False,
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
        "# T227 command-atom CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T216 final policy\n"
        "- Change: broad/.074/.077/.080 command strata crossed with the existing 8 configuration strata\n"
        "- Reward / cost / actor mask / ABI / deployment graph: unchanged\n"
        "- Hosted / behavior / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
