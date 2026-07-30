#!/usr/bin/env python3
"""Execute T186's exact package in one fresh Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE = Path(
    "/content/t186-in-episode-single-support-20260730.tar.gz"
)
PACKAGE_BYTES = 4_342_052
PACKAGE_SHA256 = (
    "adcd374145974a965d280d8129787f38fbc28a2e02c1b5147e36c0822a553eb8"
)
BUNDLE_NAME = "t186_in_episode_single_support_bundle"
MEMBER_PATHS_AND_HASHES = (
    (
        "t186_in_episode_single_support_hosted_preregistration.json",
        "7f872383bed3e6ac50e505db42e3be182170b077b929cc91f72194855bdf571d",
    ),
    (
        "t185c_in_episode_single_support_cpu_result.json",
        "d39f25a0b8fa4ad4883ccd4bc3f324eac35c3ca9caad7c32805268fde9e5f994",
    ),
    (
        "t185f_metric_runner_path_recovery_result.json",
        "d30b977d067f64b25f889570f9723c255248b85e0a8bf939649b83d20b70afbb",
    ),
    (
        "t171_t170_recovered_training_validation.json",
        "cad263608fad0fb0f220727db755a2c280314bc250925c4bdf5e3c1ae44a9573",
    ),
    (
        "t186_package_manifest.json",
        "8c2e74442052891cc4007a9c50a0c8031bf2e700fd8df17727b0ea0161001b29",
    ),
    (
        "colab_t186_in_episode_single_support_continuation.py",
        "268d5128c4140c3ac93a4c92735659ffb3002eb8323c14ca325b4587052bd0a5",
    ),
    (
        "colab_t170_eight_stratum_head_continuation.py",
        "3b81a0db4ba3374a2341256860b78c42f4207a6d8ced8d606c4bd9395f1fa744",
    ),
    (
        "colab_t78_endpoint_joint_adapter_continuation.py",
        "41a39029098ae52cb93bcb26e7fbaea967a4f0d10f70c7ab3db93ae3a8cdc927",
    ),
    (
        "colab_t32_action_margin_trainthrough_continuation.py",
        "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd",
    ),
    (
        "colab_winner_v114_linear_torque_continuation.py",
        "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f",
    ),
)
WORK = Path("/content/t186_work")
EXTRACT = Path("/content/t186_launch")
OUTPUT_JSON = Path("/content/t186_result.json")
OUTPUT_ARCHIVE = Path("/content/t186_artifacts.tar.gz")
RECEIPT = Path("/content/t186_launch_receipt.json")
EXPECTED_VERSIONS = {
    "brax": "0.14.2",
    "flax": "0.11.2",
    "jax": "0.7.2",
    "jaxlib": "0.7.2",
    "mujoco": "3.9.0",
    "mujoco-mjx": "3.9.0",
    "numpy": "2.0.2",
    "onnx": "1.22.0",
    "onnxruntime": "1.27.0",
    "optax": "0.2.5",
    "orbax-checkpoint": "0.11.25",
    "playground": "0.0.3",
}
INSTALL_REQUIREMENTS = (
    "numpy==2.0.2",
    "jax[cuda12]==0.7.2",
    "jaxlib==0.7.2",
    "brax==0.14.2",
    "flax==0.11.2",
    "optax==0.2.5",
    "orbax-checkpoint==0.11.25",
    "mujoco==3.9.0",
    "mujoco-mjx==3.9.0",
    "onnx==1.22.0",
    "onnxruntime==1.27.0",
    "playground==0.0.3",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    gpu = subprocess.run(
        ["nvidia-smi", "-L"], capture_output=True, text=True, check=False
    )
    if gpu.returncode != 0 or "L4" not in gpu.stdout:
        raise RuntimeError(f"T186 requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T186 no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T186 uploaded package changed")
    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T186 package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    observed = tuple(
        sha256(bundle / relative) for relative, _ in MEMBER_PATHS_AND_HASHES
    )
    expected = tuple(
        expected_hash for _, expected_hash in MEMBER_PATHS_AND_HASHES
    )
    if observed != expected:
        raise ValueError("T186 extracted package identity changed")
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--quiet",
            "--upgrade",
            *INSTALL_REQUIREMENTS,
        ],
        text=True,
        check=False,
    )
    if install.returncode != 0:
        raise RuntimeError(f"T186 pinned install failed: {install.returncode}")
    versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if versions != EXPECTED_VERSIONS:
        raise ValueError(f"T186 software versions changed: {versions}")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight_source = "\n".join(
        (
            "from pathlib import Path",
            "import colab_t186_in_episode_single_support_continuation as driver",
            "validation = driver.validate_inputs(Path('.'))",
            "assert validation['process_count'] == 1",
            "assert validation['devices']",
            "cmd = driver.runner_command(",
            "    Path('playground'), Path('out'),",
            "    Path('assets/source_checkpoint'),",
            "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
            ")",
            "assert cmd.count('--winner_t185_in_episode_single_support_prefix') == 1",
            "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
            "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
            "assert cmd[cmd.index('--ppo_num_envs') + 1] == '256'",
            "assert cmd[cmd.index('--num_timesteps') + 1] == '2007040'",
            "runner = Path('playground/playground/open_duck_mini_v2/runner.py').read_text()",
            "assert 'T185_IN_EPISODE_SINGLE_SUPPORT_PREFIX=' in runner",
            "assert 'T98_HIDDEN_EXPERT_CONTINUATION=' in runner",
            "print('PASS_T186_HOSTED_FULL_PREFLIGHT')",
        )
    )
    preflight = subprocess.run(
        [sys.executable, "-c", preflight_source],
        cwd=bundle,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if (
        preflight.returncode != 0
        or "PASS_T186_HOSTED_FULL_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T186 hosted preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )
    driver = (
        bundle / "colab_t186_in_episode_single_support_continuation.py"
    )
    command = [
        sys.executable,
        str(driver),
        "--bundle-root",
        str(bundle),
        "--work-root",
        str(WORK),
        "--output-json",
        str(OUTPUT_JSON),
        "--output-archive",
        str(OUTPUT_ARCHIVE),
        "--hosted-gpu-authorized",
    ]
    receipt = {
        "schema_version": "open_duck.t186_colab_launch_receipt.v1",
        "status": "STARTING_T186_HASH_FROZEN_GPU_CONTINUATION",
        "gpu": gpu.stdout.strip(),
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "member_hashes": dict(MEMBER_PATHS_AND_HASHES),
        "software_versions": versions,
        "command": command,
        "retry": False,
        "same_run_resume": False,
        "robot_or_rdk_access": False,
    }
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    result = subprocess.run(command, env=environment, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_T186_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T186_COLAB_LAUNCH"
    )
    for name, path in (
        ("output_json", OUTPUT_JSON),
        ("output_archive", OUTPUT_ARCHIVE),
    ):
        receipt[f"{name}_exists"] = path.is_file()
        if path.is_file():
            receipt[f"{name}_sha256"] = sha256(path)
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
