#!/usr/bin/env python3
"""Run the preregistered reset-COM estimator-input arm on one hosted GPU."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
from typing import Any


CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
SOURCE_ARCHIVE = "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
SOURCE_CHECKPOINT_RELATIVE = Path(
    "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000"
)
PREREG = "GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_TRAINING_PREREGISTRATION_20260715.md"
CPU_PACKAGE = "ground_up_reset_com_estimator_input_package_contract.json"
CPU_EXPANSION = "ground_up_reset_com_estimator_checkpoint_expansion.json"
FEATURE_TABLE = "ground_up_projected_reference_feature_table.npz"
ACTOR_SOURCE = "reference_residual_ppo_networks.py"
PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
    "ground_up_stage1_mechanism_stack.patch",
    "ground_up_nominal_reference_bootstrap.patch",
    "ground_up_signed_progress_objective.patch",
    "ground_up_reference_residual_actor.patch",
    "ground_up_hard_vector_command_support.patch",
    "ground_up_measured_actuator_bridge.patch",
    "ground_up_applied_target_observation.patch",
    "ground_up_tracking_tail_exceedance.patch",
    "ground_up_torso_com_randomization.patch",
    "ground_up_reset_com_estimator_input.patch",
)
EXPECTED_HASHES = {
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
    "ground_up_torso_com_randomization.patch": "524ff95a3d7018925e1ab958dfe067067e09f0cd718176c7cc46bb6b078d8e3a",
    "ground_up_reset_com_estimator_input.patch": "2758898a09ef487d5a6949b9aaafda3db9f00c10976136bd6f5c3e9e7a75a4e8",
    ACTOR_SOURCE: "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
    FEATURE_TABLE: "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    SOURCE_ARCHIVE: "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
    PREREG: "330716283cbe7244cbb47ac678474f040d79cca75296aab5366d7ec83ec86e54",
    CPU_PACKAGE: "00e152e469e8fdeba49d7031c259b688f722ea75764297cb7ea51431d9fc2914",
    CPU_EXPANSION: "e5e7a3e8e34e7cc2ed511828d0e5323aed44d5e2d384082d31718ebb0a42b09c",
}
ARM_NAME = "RESET_EST_LATCH_U05"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
MAX_HOSTED_SECONDS = 2_400
MAX_COMPUTE_UNITS = 2.0
INSERT_INDEX = 101
RESULT_PREFIX = "GROUND_UP_RESET_ESTIMATOR_RESULT="


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def run(
    command: list[str], *, cwd: Path | None = None, timeout: int = 1800,
    capture: bool = False, env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print("COM_COMMAND=" + json.dumps(command), flush=True)
    return subprocess.run(
        command, cwd=cwd, check=True, timeout=timeout, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None, env=env,
    )


def validate_assets(assets: Path) -> dict[str, str]:
    actual: dict[str, str] = {}
    for name, expected in EXPECTED_HASHES.items():
        path = assets / name
        if not path.is_file():
            raise SystemExit(f"missing uploaded asset: {path}")
        actual[name] = sha256(path)
        if actual[name] != expected:
            raise SystemExit(f"hash mismatch for {name}: {actual[name]} != {expected}")
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        suffix = str(SOURCE_CHECKPOINT_RELATIVE / "_METADATA")
        if not any(member.name == suffix for member in archive):
            raise SystemExit(f"protected checkpoint member missing: {suffix}")
    package = json.loads((assets / CPU_PACKAGE).read_text())
    expansion = json.loads((assets / CPU_EXPANSION).read_text())
    if package.get("status") != "PASS_RESET_COM_ESTIMATOR_INPUT_CPU_PACKAGE_CONTRACT":
        raise SystemExit("passing estimator-input CPU package contract required")
    if expansion.get("status") != "PASS_RESET_COM_ESTIMATOR_CHECKPOINT_EXPANSION":
        raise SystemExit("passing CPU checkpoint expansion required")
    return actual


def insert(array: Any, value: Any, *, axis: int = 0) -> Any:
    import jax.numpy as jnp

    source = jnp.asarray(array)
    shape = list(source.shape)
    shape[axis] = 1
    inserted = jnp.broadcast_to(jnp.asarray(value, dtype=source.dtype), shape)
    return jnp.concatenate(
        [
            jnp.take(source, jnp.arange(INSERT_INDEX), axis=axis),
            inserted,
            jnp.take(source, jnp.arange(INSERT_INDEX, source.shape[axis]), axis=axis),
        ],
        axis=axis,
    )


def remove(array: Any, *, axis: int = 0) -> Any:
    import jax.numpy as jnp

    source = jnp.asarray(array)
    return jnp.concatenate(
        [
            jnp.take(source, jnp.arange(INSERT_INDEX), axis=axis),
            jnp.take(source, jnp.arange(INSERT_INDEX + 1, source.shape[axis]), axis=axis),
        ],
        axis=axis,
    )


def expand_checkpoint_tree(source: list[Any]) -> list[Any]:
    import jax.numpy as jnp

    expanded = copy.deepcopy(source)
    for stream in ("state", "privileged_state"):
        expanded[0]["mean"][stream] = insert(expanded[0]["mean"][stream], 0.0)
        expanded[0]["std"][stream] = insert(expanded[0]["std"][stream], 1.0)
        expanded[0]["summed_variance"][stream] = insert(
            expanded[0]["summed_variance"][stream], 8_048_640.0
        )
    actor = expanded[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    expanded[1]["params"]["residual_trunk"]["hidden_0"]["kernel"] = insert(
        actor, jnp.zeros((1, actor.shape[1]), dtype=actor.dtype)
    )
    critic = expanded[2]["params"]["hidden_0"]["kernel"]
    expanded[2]["params"]["hidden_0"]["kernel"] = insert(
        critic, jnp.zeros((1, critic.shape[1]), dtype=critic.dtype)
    )
    return expanded


def collapse_checkpoint_tree(expanded: list[Any]) -> list[Any]:
    collapsed = copy.deepcopy(expanded)
    for stream in ("state", "privileged_state"):
        for family in ("mean", "std", "summed_variance"):
            collapsed[0][family][stream] = remove(collapsed[0][family][stream])
    collapsed[1]["params"]["residual_trunk"]["hidden_0"]["kernel"] = remove(
        collapsed[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    )
    collapsed[2]["params"]["hidden_0"]["kernel"] = remove(
        collapsed[2]["params"]["hidden_0"]["kernel"]
    )
    return collapsed


def tree_max_error(left: Any, right: Any) -> tuple[bool, float]:
    import jax
    import numpy as np

    same = jax.tree_util.tree_structure(left) == jax.tree_util.tree_structure(right)
    if not same:
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left), jax.tree_util.tree_leaves(right), strict=True
        )
    ]
    return True, max(errors, default=0.0)


def normalizer_state(value: dict[str, Any]) -> Any:
    from brax.training import types
    from brax.training.acme import running_statistics

    return running_statistics.RunningStatisticsState(
        mean=value["mean"], std=value["std"],
        count=types.UInt64(hi=value["count"]["hi"], lo=value["count"]["lo"]),
        summed_variance=value["summed_variance"], std_eps=value["std_eps"],
    )


def hosted_expand(source_path: Path, destination: Path, report_path: Path) -> dict[str, Any]:
    import jax
    import jax.numpy as jnp
    import numpy as np
    from orbax import checkpoint as ocp
    from playground.common.reference_residual_ppo_networks import (
        make_reference_residual_ppo_networks,
    )

    if destination.exists():
        raise FileExistsError(f"expanded destination already exists: {destination}")
    checkpointer = ocp.PyTreeCheckpointer()
    source = checkpointer.restore(str(source_path))
    expanded = expand_checkpoint_tree(source)
    checkpointer.save(str(destination), expanded)
    restored = checkpointer.restore(str(destination))
    collapsed = collapse_checkpoint_tree(restored)
    preserved_structure, preserved_error = tree_max_error(source, collapsed)
    save_structure, save_error = tree_max_error(expanded, restored)

    source_shapes = [
        list(np.asarray(source[0]["mean"]["state"]).shape),
        list(np.asarray(source[0]["mean"]["privileged_state"]).shape),
        list(np.asarray(source[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]).shape),
        list(np.asarray(source[2]["params"]["hidden_0"]["kernel"]).shape),
    ]
    expanded_shapes = [
        list(np.asarray(restored[0]["mean"]["state"]).shape),
        list(np.asarray(restored[0]["mean"]["privileged_state"]).shape),
        list(np.asarray(restored[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]).shape),
        list(np.asarray(restored[2]["params"]["hidden_0"]["kernel"]).shape),
    ]
    old_networks = make_reference_residual_ppo_networks(
        {"state": (115,), "privileged_state": (226,)}, 14
    )
    new_networks = make_reference_residual_ppo_networks(
        {"state": (116,), "privileged_state": (227,)}, 14
    )
    old_state = jnp.linspace(-0.25, 0.25, 115, dtype=jnp.float32)[None]
    old_priv = jnp.linspace(-0.5, 0.5, 226, dtype=jnp.float32)[None]
    old_obs = {"state": old_state, "privileged_state": old_priv}
    old_actor = old_networks.policy_network.apply(
        normalizer_state(source[0]), source[1], old_obs
    )
    old_critic = old_networks.value_network.apply(
        normalizer_state(source[0]), source[2], old_obs
    )
    cells = []
    for z in (-1.0, 0.0, 1.0):
        new_obs = {
            "state": insert(old_state, z, axis=1),
            "privileged_state": insert(old_priv, z, axis=1),
        }
        actor = new_networks.policy_network.apply(
            normalizer_state(restored[0]), restored[1], new_obs
        )
        critic = new_networks.value_network.apply(
            normalizer_state(restored[0]), restored[2], new_obs
        )
        cells.append({
            "z": z,
            "actor_max_abs_error": float(np.max(np.abs(np.asarray(actor) - np.asarray(old_actor)))),
            "critic_max_abs_error": float(np.max(np.abs(np.asarray(critic) - np.asarray(old_critic)))),
            "reference_tail_exact": bool(np.array_equal(
                np.asarray(new_obs["state"])[0, -14:], np.asarray(old_state)[0, -14:]
            )),
        })
    inserted = {
        stream: {
            family: float(np.asarray(restored[0][family][stream])[INSERT_INDEX])
            for family in ("mean", "std", "summed_variance")
        }
        for stream in ("state", "privileged_state")
    }
    actor_row = np.asarray(
        restored[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    )[INSERT_INDEX]
    critic_row = np.asarray(restored[2]["params"]["hidden_0"]["kernel"])[INSERT_INDEX]
    checks = {
        "source_shapes_exact": source_shapes == [[115], [226], [115, 512], [226, 512]],
        "source_count_exact": int(np.asarray(source[0]["count"]["hi"])) == 0
        and int(np.asarray(source[0]["count"]["lo"])) == 8_048_640
        and float(np.asarray(source[0]["std_eps"])) == 0.0,
        "expanded_shapes_exact": expanded_shapes == [[116], [227], [116, 512], [227, 512]],
        "inserted_normalizer_exact": all(
            value == {"mean": 0.0, "std": 1.0, "summed_variance": 8_048_640.0}
            for value in inserted.values()
        ),
        "inserted_rows_zero": bool(
            np.count_nonzero(actor_row) == 0 and np.count_nonzero(critic_row) == 0
        ),
        "all_other_values_bit_exact": preserved_structure and preserved_error == 0.0,
        "save_restore_bit_exact": save_structure and save_error == 0.0,
        "step_zero_outputs_exact": max(
            cell[key] for cell in cells
            for key in ("actor_max_abs_error", "critic_max_abs_error")
        ) <= 1e-7,
        "reference_tail_exact": all(cell["reference_tail_exact"] for cell in cells),
        "all_values_finite": all(
            np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree_util.tree_leaves(restored)
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_HOSTED_CHECKPOINT_EXPANSION" if not failed else "FAIL_HOSTED_CHECKPOINT_EXPANSION"
    report = {
        "schema_version": "ground_up_reset_estimator_hosted_expansion.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "source_directory_sha256": sha256_directory(source_path),
        "expanded_directory_sha256": sha256_directory(destination),
        "source_shapes": source_shapes, "expanded_shapes": expanded_shapes,
        "inserted_normalizer": inserted, "output_equivalence": cells,
        "max_other_value_error": preserved_error,
        "max_save_restore_error": save_error,
        "devices": [str(device) for device in jax.devices()],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if failed:
        raise RuntimeError(f"hosted checkpoint expansion failed: {failed}")
    return report


def training_command(root: Path, assets: Path, output: Path, restore: Path) -> list[str]:
    del root
    return [
        sys.executable, "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash", "--env", "joystick",
        "--output_dir", str(output), "--num_timesteps", "2000000",
        "--ppo_seed", "100", "--ppo_num_envs", "256", "--ppo_num_evals", "3",
        "--ppo_episode_length", "600", "--ppo_unroll_length", "20",
        "--ppo_batch_size", "256", "--ppo_num_minibatches", "4",
        "--ppo_num_updates_per_batch", "4", "--ppo_learning_rate", "0.0003",
        "--ppo_discounting", "0.97", "--ppo_entropy_cost", "0.005",
        "--policy_architecture", "reference_residual", "--imitation_scale", "1.0",
        "--reference_feature_table_path", str(assets / FEATURE_TABLE),
        "--nominal_reference_bootstrap", "--ground_up_reset_com_estimator_input",
        "--ground_up_torso_com_randomization",
        "--ground_up_torso_com_x_min_m", "-0.05",
        "--ground_up_torso_com_x_max_m", "0.05",
        "--ground_up_torso_com_distribution", "uniform",
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x", "0.074",
        "--ground_up_command_support_max_x", "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        "5.24,5.24,1.50,1.50,1.50,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25",
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale", "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad", "0.20",
        "--reference_start_phase", "0", "--ground_up_signed_progress_objective",
        "--critic_observation", "privileged_state",
        "--restore_checkpoint_path", str(restore),
    ]


def inspect_exports(output: Path) -> dict[str, Any]:
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    onnx = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints)
    onnx_steps = sorted(int(path.stem.rsplit("_", 1)[1]) for path in onnx)
    if checkpoint_steps != EXPECTED_STEPS or onnx_steps != EXPECTED_STEPS:
        raise RuntimeError(
            f"unexpected exports: checkpoints={checkpoint_steps}, onnx={onnx_steps}"
        )
    return {
        "checkpoint_steps": checkpoint_steps,
        "checkpoints": [
            {"name": path.name, "directory_sha256": sha256_directory(path)}
            for path in checkpoints
        ],
        "onnx": [
            {"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in onnx
        ],
    }


def write_snapshot(output_root: Path, artifact: Path) -> dict[str, Any]:
    temporary = artifact.with_suffix(artifact.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(output_root, arcname=output_root.name)
    temporary.replace(artifact)
    return {"path": str(artifact), "sha256": sha256(artifact), "bytes": artifact.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=Path("/content"))
    parser.add_argument("--validate-assets-only", action="store_true")
    args, _kernel_args = parser.parse_known_args()
    assets = args.asset_root.resolve()
    hashes = validate_assets(assets)
    if args.validate_assets_only:
        print(json.dumps({"status": "PASS_ASSET_VALIDATION", "hashes": hashes}, sort_keys=True))
        return 0

    started = time.monotonic()
    root = assets / "ground_up_reset_estimator_playground"
    source_root = assets / "ground_up_reset_estimator_source"
    output_root = assets / "ground_up_reset_estimator_outputs"
    artifact = assets / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz"
    manifest_path = assets / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json"
    for path in (root, source_root, output_root):
        if path.exists():
            raise FileExistsError(f"no resume/retry: path already exists: {path}")
    if artifact.exists() or manifest_path.exists():
        raise FileExistsError("no resume/retry: output artifact already exists")

    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(root)])
    run(["git", "checkout", "-q", CONTROL_COMMIT], cwd=root)
    for name in PATCHES:
        run(["git", "apply", "--check", str(assets / name)], cwd=root)
        run(["git", "apply", str(assets / name)], cwd=root)
    shutil.copy2(assets / ACTOR_SOURCE, root / "playground/common/reference_residual_ppo_networks.py")
    run(["git", "diff", "--check"], cwd=root)
    run([
        sys.executable, "-m", "py_compile",
        "playground/common/randomize.py", "playground/common/runner.py",
        "playground/common/reference_residual_ppo_networks.py",
        "playground/open_duck_mini_v2/joystick.py",
        "playground/open_duck_mini_v2/runner.py",
    ], cwd=root)

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run([
        sys.executable, "-m", "pip", "install", "-q",
        "jax[cuda12]==0.8.2", "jaxlib==0.8.2", "mujoco==3.9.0",
        "playground==0.0.5", "onnxruntime>=1.20.1", "tensorflow==2.20.0",
        "onnx", "tensorboardX",
    ], timeout=1200)
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(root)])
    device_output = run([
        sys.executable, "-c",
        "import jax,jaxlib,mujoco; print(jax.__version__,jaxlib.__version__,mujoco.__version__); "
        "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))",
    ], capture=True).stdout
    if "HAS_GPU True" not in device_output or "CudaDevice" not in device_output:
        raise RuntimeError("hosted package requires a CUDA JAX GPU")

    source_root.mkdir()
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        members = [
            member for member in archive
            if member.name == str(SOURCE_CHECKPOINT_RELATIVE)
            or member.name.startswith(str(SOURCE_CHECKPOINT_RELATIVE) + "/")
        ]
        archive.extractall(source_root, members=members, filter="data")
    source_checkpoint = source_root / SOURCE_CHECKPOINT_RELATIVE
    output_root.mkdir()
    expanded_checkpoint = output_root / "hosted_expanded_source"
    expansion_report_path = output_root / "hosted_expansion_report.json"
    old_path = list(sys.path)
    sys.path.insert(0, str(root))
    try:
        expansion_report = hosted_expand(
            source_checkpoint, expanded_checkpoint, expansion_report_path
        )
    finally:
        sys.path[:] = old_path
    if time.monotonic() - started >= MAX_HOSTED_SECONDS:
        raise TimeoutError("hosted wall ceiling reached before training")

    arm_output = output_root / ARM_NAME
    arm_output.mkdir()
    command = training_command(root, assets, arm_output, expanded_checkpoint)
    run_env = dict(os.environ)
    run_env["PYTHONPATH"] = str(root)
    completed = run(
        command, cwd=root,
        timeout=max(1, int(MAX_HOSTED_SECONDS - (time.monotonic() - started))),
        capture=True, env=run_env,
    )
    (arm_output / "training.log").write_text(completed.stdout)
    exports = inspect_exports(arm_output)
    elapsed = time.monotonic() - started
    if elapsed > MAX_HOSTED_SECONDS:
        raise TimeoutError(f"hosted wall ceiling exceeded: {elapsed}")
    manifest = {
        "schema_version": "ground_up_reset_com_estimator_hosted_training.v1",
        "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "behavior_status": "UNEVALUATED",
        "control_commit": CONTROL_COMMIT,
        "input_hashes": hashes,
        "arm": {
            "name": ARM_NAME, "command": command, "expected_steps": EXPECTED_STEPS,
            **exports,
        },
        "hosted_expansion": expansion_report,
        "execution": {
            "versions_and_devices": device_output.splitlines(),
            "total_seconds": elapsed,
            "maximum_hosted_seconds": MAX_HOSTED_SECONDS,
            "maximum_compute_units": MAX_COMPUTE_UNITS,
            "session_count": 1, "training_process_count": 1, "resume": False,
        },
        "selection": {"training_reward_used": False, "behavior_unevaluated": True},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    shutil.copy2(manifest_path, output_root / manifest_path.name)
    snapshot = write_snapshot(output_root, artifact)
    result = {
        "status": manifest["status"], "behavior_status": "UNEVALUATED",
        "manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path)},
        "artifact": snapshot, "elapsed_seconds": elapsed,
    }
    print(RESULT_PREFIX + json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
