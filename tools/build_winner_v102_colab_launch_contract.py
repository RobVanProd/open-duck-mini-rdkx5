#!/usr/bin/env python3
"""Freeze the exact Winner-v102 Colab launcher and notebook."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
CPU_CONTRACT = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v102_response_conditioned_hosted_package_contract.json"
)
LAUNCHER = ROOT / "tools/launch_winner_v102_response_conditioned_colab.py"
NOTEBOOK = ROOT / "notebooks/WINNER_V102_RESPONSE_CONDITIONED_COLAB_LAUNCH.ipynb"
OUTPUT = ANALYSIS / "winner_v102_colab_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V102_COLAB_LAUNCH_CONTRACT_20260722.md"
PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
CPU_CONTRACT_SHA256 = (
    "4f44c2ff9de0ee715b09c1c95048bedb0a43f3334eaa70970dac8c08d6e047d0"
)
PACKAGE_CONTRACT_SHA256 = (
    "d4218997ab5bc75745c32c3e4b29adda82e5e7846adce82db0e52016c3909ea0"
)
PACKAGE_SHA256 = "cbb6dd1ef5c68e013cbc8e0a29bdbb014cff476064f2ac763aedfeeba6b28017"
PACKAGE_BYTES = 59_176_688
LAUNCHER_SHA256 = "24d942f85b2e8bdeb43493f27c78c111ea0e1e4e96c33f21bb30a55674de1818"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v102 launch: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    package_contract = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    launcher_text = LAUNCHER.read_text(encoding="utf-8")
    notebook_source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )
    checks = {
        "preregistration_exact": sha256(PREREGISTRATION)
        == PREREGISTRATION_SHA256
        and prereg.get("status")
        == "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM",
        "cpu_contract_exact": sha256(CPU_CONTRACT) == CPU_CONTRACT_SHA256
        and cpu.get("status") == "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT",
        "package_contract_exact": sha256(PACKAGE_CONTRACT)
        == PACKAGE_CONTRACT_SHA256
        and package_contract.get("status")
        == "PASS_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE",
        "package_exact": package.stat().st_size == PACKAGE_BYTES
        and sha256(package) == PACKAGE_SHA256
        and package_contract.get("archive", {}).get("sha256") == PACKAGE_SHA256,
        "launcher_exact": sha256(LAUNCHER) == LAUNCHER_SHA256,
        "launcher_no_retry_guards": all(
            token in launcher_text
            for token in (
                "Winner-v102 no-retry path exists",
                "--hosted-gpu-authorized",
                '"retry": False',
                '"resume": False',
                '"robot_or_rdk_access": False',
            )
        ),
        "launcher_pins_full_software_contract": all(
            f'"{name}=={version}"' in launcher_text
            for name, version in {
                "numpy": "2.0.2",
                "brax": "0.14.2",
                "flax": "0.11.2",
                "optax": "0.2.5",
                "orbax-checkpoint": "0.11.25",
                "mujoco": "3.9.0",
                "mujoco-mjx": "3.9.0",
                "onnx": "1.22.0",
                "onnxruntime": "1.27.0",
                "playground": "0.0.3",
            }.items()
        )
        and '"jax[cuda12]==0.7.2"' in launcher_text
        and '"jaxlib==0.7.2"' in launcher_text,
        "notebook_l4_gpu_exact": notebook.get("metadata", {}).get("accelerator")
        == "GPU"
        and notebook.get("metadata", {}).get("colab", {}).get("gpuType") == "L4",
        "notebook_package_hash_exact": PACKAGE_SHA256 in notebook_source
        and str(PACKAGE_BYTES) in notebook_source.replace("_", ""),
        "notebook_launcher_hash_exact": LAUNCHER_SHA256 in notebook_source,
        "notebook_gpu_preflight": "nvidia-smi" in notebook_source,
        "notebook_outputs_are_inspection_only": all(
            name in notebook_source
            for name in (
                "winner_v102_result.json",
                "winner_v102_artifacts.tar.gz",
                "winner_v102_launch_receipt.json",
            )
        ),
        "formal_outcomes_zero": not (
            ANALYSIS / "winner_v102_response_conditioned_training_result.json"
        ).exists(),
        "formal_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V102_COLAB_LAUNCH_CONTRACT"
        if not failed
        else "HOLD_WINNER_V102_COLAB_LAUNCH_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v102.colab_launch_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "preregistration": PREREGISTRATION_SHA256,
            "cpu_contract": CPU_CONTRACT_SHA256,
            "package_contract": PACKAGE_CONTRACT_SHA256,
            "package": PACKAGE_SHA256,
            "launcher": LAUNCHER_SHA256,
            "notebook": sha256(NOTEBOOK),
        },
        "execution": {
            "hosted_sessions_started": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_l4_gpu_launch": not failed,
            "retry_or_resume": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v102 Colab launch contract\n\n"
        f"Status: `{status}`\n\n"
        f"- package SHA-256: `{PACKAGE_SHA256}`\n"
        f"- launcher SHA-256: `{LAUNCHER_SHA256}`\n"
        f"- notebook SHA-256: `{sha256(NOTEBOOK)}`\n"
        f"- failed checks: `{failed}`\n\n"
        "A pass authorizes one L4 GPU curriculum without retry or resume. It does "
        "not authorize behavior evaluation, checkpoint selection, RDK-X5 access, "
        "robot access, Gate 5, deployment, torque, motion, or robot clearance.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
