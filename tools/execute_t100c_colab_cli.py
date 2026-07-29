#!/usr/bin/env python3
"""Execute T100C's exact wrapper bundle in one fresh Colab L4 session."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile


PACKAGE = Path("/content/t100c-original-driver-wrapper-20260728.tar.gz")
PACKAGE_BYTES = 4_323_699
PACKAGE_SHA256 = (
    "38b8e2f1bf520c813ec9725805393e62fa5115a146f73dd3a11b3a24e2659b44"
)
BUNDLE_NAME = "t100c_original_driver_wrapper_bundle"
PREREGISTRATION_SHA256 = (
    "3a79d1406eb9be5c37faaf883628e939d5cad4949c6411ca038378fe1ba042cd"
)
T100_HOLD_SHA256 = (
    "69d2b8289d6c0bedd8b811795072cef4da0a0c94878898cd4515e3281b8e2b6b"
)
T100B_HOLD_SHA256 = (
    "34f0573fc6c659cbf9a51377d963b9b1b783d2b51ccb7ae3a6954573594d9ec2"
)
CPU_RESULT_SHA256 = (
    "a9ddefca6c724960402fdbe635da5618f812b6b8017d360f5c3bf988100d9be2"
)
PACKAGE_MANIFEST_SHA256 = (
    "84ebb9c2b3adc37b0a911d2fb1efa8dacaed2d419c694a21df5d7cd302fc7460"
)
WRAPPER_SHA256 = (
    "b3120a96ef8e2b1be240061403b19b2f9d8e634ff8dc2a1a86f085f2bb5832f8"
)
ORIGINAL_DRIVER_SHA256 = (
    "83ea5ff09b7198c3eafb826c7f1f59da303cc521c4bc441539fe3328070d3397"
)
BASE_DRIVER_SHA256 = (
    "41a39029098ae52cb93bcb26e7fbaea967a4f0d10f70c7ab3db93ae3a8cdc927"
)
T32_DRIVER_SHA256 = (
    "a15ec26c3419d75b2b0417bfd3950947c7d1ae711a050ee33f967f8f1f1f01dd"
)
HELPER_SHA256 = (
    "09bbe4ab7ee42d7f77bb302d7fa8cab15b8734be97f5db80f912ad6619dd808f"
)
WORK = Path("/content/t100c_work")
EXTRACT = Path("/content/t100c_launch")
OUTPUT_JSON = Path("/content/t100c_result.json")
OUTPUT_ARCHIVE = Path("/content/t100c_artifacts.tar.gz")
RECEIPT = Path("/content/t100c_launch_receipt.json")
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
        raise RuntimeError(f"T100C requires L4: {gpu.stdout}{gpu.stderr}")
    for path in (WORK, EXTRACT, OUTPUT_JSON, OUTPUT_ARCHIVE, RECEIPT):
        if path.exists():
            raise FileExistsError(f"T100C no-retry path exists: {path}")
    if (
        PACKAGE.stat().st_size != PACKAGE_BYTES
        or sha256(PACKAGE) != PACKAGE_SHA256
    ):
        raise ValueError("T100C uploaded package changed")

    EXTRACT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "r:gz") as archive:
        if any(
            "/playground/.tmp/" in f"/{member.name}/"
            for member in archive.getmembers()
        ):
            raise ValueError("T100C package contains playground/.tmp")
        archive.extractall(EXTRACT, filter="data")
    bundle = EXTRACT / BUNDLE_NAME
    prereg = bundle / "t100c_original_driver_wrapper_preregistration.json"
    t100_hold = bundle / "t100_preexecution_hold_attribution.json"
    t100b_hold = bundle / "t100b_prelaunch_identity_hold_attribution.json"
    cpu_result = bundle / "t99_deployment_coordinate_audit_result.json"
    manifest = bundle / "t100c_package_manifest.json"
    wrapper = bundle / "colab_t100c_original_driver_wrapper.py"
    driver = bundle / "colab_t100_hidden_expert_continuation.py"
    base_driver = bundle / "colab_t78_endpoint_joint_adapter_continuation.py"
    t32_driver = bundle / "colab_t32_action_margin_trainthrough_continuation.py"
    helper = bundle / "colab_winner_v114_linear_torque_continuation.py"
    observed = (
        sha256(prereg),
        sha256(t100_hold),
        sha256(t100b_hold),
        sha256(cpu_result),
        sha256(manifest),
        sha256(wrapper),
        sha256(driver),
        sha256(base_driver),
        sha256(t32_driver),
        sha256(helper),
    )
    expected = (
        PREREGISTRATION_SHA256,
        T100_HOLD_SHA256,
        T100B_HOLD_SHA256,
        CPU_RESULT_SHA256,
        PACKAGE_MANIFEST_SHA256,
        WRAPPER_SHA256,
        ORIGINAL_DRIVER_SHA256,
        BASE_DRIVER_SHA256,
        T32_DRIVER_SHA256,
        HELPER_SHA256,
    )
    if observed != expected:
        raise ValueError("T100C extracted package identity changed")

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
        raise RuntimeError(f"T100C pinned install failed: {install.returncode}")
    versions = {
        name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS
    }
    if versions != EXPECTED_VERSIONS:
        raise ValueError(f"T100C software versions changed: {versions}")

    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(bundle), str(bundle / "playground"))
    )
    preflight_source = "\n".join(
        (
            "from pathlib import Path",
            "import colab_t100_hidden_expert_continuation as frozen",
            "import colab_t100c_original_driver_wrapper as wrapper",
            "assert wrapper.frozen_t100 is frozen",
            "validation = frozen.validate_inputs(Path('.'))",
            "assert validation['process_count'] == 1",
            "assert validation['devices']",
            "cmd = wrapper.corrected_runner_command(",
            "    Path('playground'), Path('out'),",
            "    Path('assets/source_checkpoint'),",
            "    Path('assets/ground_up_projected_reference_feature_table.npz'),",
            ")",
            "assert cmd.count('--winner_t98_hidden_expert_continuation') == 1",
            "assert cmd.count('--winner_t98_hidden_gate_asset_path') == 1",
            "print('PASS_T100C_HOSTED_FULL_PREFLIGHT')",
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
        or "PASS_T100C_HOSTED_FULL_PREFLIGHT"
        not in preflight.stdout.splitlines()
    ):
        raise RuntimeError(
            f"T100C hosted preflight failed:\n{preflight.stdout}\n"
            f"{preflight.stderr}"
        )

    command = [
        sys.executable,
        str(wrapper),
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
        "schema_version": "open_duck.t100c_colab_launch_receipt.v1",
        "status": "STARTING_T100C_HASH_FROZEN_GPU_CONTINUATION",
        "classification": "pre_optimizer_replacement_not_retry",
        "gpu": gpu.stdout.strip(),
        "package": {"bytes": PACKAGE_BYTES, "sha256": PACKAGE_SHA256},
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "t100_hold_sha256": T100_HOLD_SHA256,
        "t100b_hold_sha256": T100B_HOLD_SHA256,
        "cpu_result_sha256": CPU_RESULT_SHA256,
        "package_manifest_sha256": PACKAGE_MANIFEST_SHA256,
        "wrapper_sha256": WRAPPER_SHA256,
        "original_driver_sha256": ORIGINAL_DRIVER_SHA256,
        "base_driver_sha256": BASE_DRIVER_SHA256,
        "t32_driver_sha256": T32_DRIVER_SHA256,
        "helper_sha256": HELPER_SHA256,
        "software_versions": versions,
        "command": command,
        "retry": False,
        "resume": False,
        "robot_or_rdk_access": False,
    }
    RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    result = subprocess.run(command, env=environment, text=True, check=False)
    receipt["returncode"] = result.returncode
    receipt["status"] = (
        "COMPLETED_T100C_COLAB_LAUNCH"
        if result.returncode == 0
        else "HOLD_T100C_COLAB_LAUNCH"
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
