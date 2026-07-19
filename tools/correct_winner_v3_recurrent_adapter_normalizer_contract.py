#!/usr/bin/env python3
"""Correct the source-count assertion without rerunning the CPU smoke."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT_JSON = ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json"
RESULT_MD = ANALYSIS / "WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT_20260719.md"
CORRECTION_JSON = ANALYSIS / "winner_v3_recurrent_adapter_normalizer_count_correction.json"
CORRECTION_MD = ANALYSIS / "WINNER_V3_RECURRENT_ADAPTER_NORMALIZER_COUNT_CORRECTION_20260719.md"
INITIAL_RESULT_SHA256 = "73de2fe234c7581e6b06eff5b549ec898d50eec1d5471fb8de8f61f27db821ab"
INITIAL_RESULT_COMMIT = "215a84a1b526510bf7a82128ebff5637c2e216d8"
CPU_TEMPLATE = Path(
    "/home/lsd/robots/open-duck-mini-rdkx5/outputs/"
    "ground_up_torso_com_cpu_smoke/2026_07_14_180720_0"
)
CPU_TEMPLATE_SHA256 = "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a"


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


def uint64_value(value: dict[str, object]) -> int:
    return (int(np.asarray(value["hi"])) << 32) | int(np.asarray(value["lo"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-root", type=Path,
        default=Path("/tmp/winner_v3_recurrent_adapter_cpu_contract_formal_9a6ad2b"),
    )
    args = parser.parse_args()
    work = args.work_root.resolve()
    if sha256(RESULT_JSON) != INITIAL_RESULT_SHA256:
        raise ValueError("initial committed contract-result hash changed")
    initial = json.loads(RESULT_JSON.read_text())
    if initial["status"] != "HOLD_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT":
        raise ValueError("expected the committed initial HOLD")
    if initial["failed_checks"] != ["expanded_hidden_normalizer_exact"]:
        raise ValueError("initial result has an unexpected failure set")
    if not all(
        passed for name, passed in initial["checks"].items()
        if name != "expanded_hidden_normalizer_exact"
    ):
        raise ValueError("a substantive CPU-contract check failed")

    expanded_path = work / "expanded_checkpoint"
    source_path = (
        work / "source/ground_up_tracking_tail_outputs/T2_EQUAL/"
        "2026_07_14_190026_512000"
    )
    trained_onnx = Path(initial["training_artifacts"]["final_onnx_path"])
    trained_checkpoint = Path(initial["training_artifacts"]["final_checkpoint_path"])
    artifact_hashes_exact = bool(
        sha256_directory(expanded_path)
        == initial["expanded_checkpoint_directory_sha256"]
        and sha256_directory(source_path)
        == initial["source_checkpoint_directory_sha256"]
        and sha256(trained_onnx)
        == initial["training_artifacts"]["final_onnx_sha256"]
        and sha256_directory(trained_checkpoint)
        == initial["training_artifacts"]["final_checkpoint_directory_sha256"]
    )
    if sha256_directory(CPU_TEMPLATE) != CPU_TEMPLATE_SHA256:
        raise ValueError("CPU template hash changed")

    checkpointer = ocp.PyTreeCheckpointer()
    expanded = checkpointer.restore(str(expanded_path))
    template = checkpointer.restore(str(CPU_TEMPLATE))
    restore_args = orbax_utils.restore_args_from_target(template)
    source = checkpointer.restore(str(source_path), item=template, restore_args=restore_args)
    source_count = uint64_value(source[0]["count"])
    expanded_count = uint64_value(expanded[0]["count"])
    hidden_mean = np.asarray(expanded[0]["mean"]["policy_hidden"])
    hidden_std = np.asarray(expanded[0]["std"]["policy_hidden"])
    hidden_variance = np.asarray(expanded[0]["summed_variance"]["policy_hidden"])
    neutral_statistics_exact = bool(
        source_count == expanded_count == 7_536_640
        and hidden_mean.shape == hidden_std.shape == hidden_variance.shape == (64,)
        and np.array_equal(hidden_mean, np.zeros(64, dtype=np.float32))
        and np.array_equal(hidden_std, np.ones(64, dtype=np.float32))
        and np.array_equal(
            hidden_variance,
            np.full(64, float(source_count), dtype=np.float32),
        )
    )
    checks = {
        "initial_result_hash_exact": True,
        "initial_only_failure_is_stale_count_assertion": True,
        "all_other_initial_checks_pass": True,
        "formal_artifact_hashes_exact": artifact_hashes_exact,
        "protected_source_and_expanded_count_exact": source_count == expanded_count,
        "neutral_hidden_statistics_use_protected_source_count": neutral_statistics_exact,
        "cpu_only_readback": all(device.platform == "cpu" for device in jax.devices()),
        "no_training_or_inference_rerun": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"normalizer-count correction failed: {failed}")

    corrected = copy.deepcopy(initial)
    corrected["status"] = "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT"
    corrected["checks"]["expanded_hidden_normalizer_exact"] = True
    corrected["failed_checks"] = []
    corrected["normalizer_count_correction"] = {
        "initial_result_commit": INITIAL_RESULT_COMMIT,
        "initial_result_sha256": INITIAL_RESULT_SHA256,
        "incorrect_literal": 8_048_640,
        "protected_source_count": source_count,
        "method": "read-only correction from the same formal expanded/source checkpoints; no smoke rerun",
        "correction_artifact": str(CORRECTION_JSON.relative_to(ROOT)),
    }
    corrected["authority"]["single_cpu_training_curriculum_after_pass"] = True
    RESULT_JSON.write_text(json.dumps(corrected, indent=2, sort_keys=True) + "\n")
    RESULT_MD.write_text(f"""# Winner-v3 Recurrent-Adapter CPU Contract — 2026-07-19

Status: `PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`

The committed initial result at `{INITIAL_RESULT_COMMIT}` held on one stale
normalizer-count assertion. It compared the neutral recurrent variance with
`8,048,640`, copied from the other persistent checkpoint, while the protected
T2_EQUAL 512K source and the formal expanded checkpoint both carry count
`{source_count:,}`. The same formal artifacts prove the 64 recurrent entries
are exactly mean zero, standard deviation one, and summed variance equal to
that source count. No training, export, inference, or behavior cell was rerun.

- JAX devices: `{initial['devices']}`
- step-zero maximum base/adapter logits error: `{initial['step_zero_max_abs_error']}`
- initial ONNX action/hidden error: `{initial['initial_export']['max_action_error']}` / `{initial['initial_export']['max_hidden_error']}`
- CPU smoke exports: `{initial['training']['all_checkpoint_steps']}`
- CPU smoke wall seconds: `{initial['training']['elapsed_seconds']:.3f}`
- base/adapter-state/adapter-head maximum updates: `{initial['update_family_max_delta']['protected_base']}` / `{initial['update_family_max_delta']['adapter_state']}` / `{initial['update_family_max_delta']['adapter_head']}`
- trained ONNX SHA-256: `{initial['training_artifacts']['final_onnx_sha256']}`
- failed checks after read-only correction: `[]`

This is a plumbing and finite-update contract only. Training reward and the
1,024-step behavior have no selection weight and make no gait claim. The pass
authorizes only the single preregistered CPU curriculum and its later frozen
CPU evaluation. It does not authorize hosted/Colab allocation, GPU/iGPU,
RDK-X5, robot, serial, torque, motion, runtime execution, Gate 5, deployment,
or robot clearance.
""")
    correction = {
        "schema_version": "winner_v3.recurrent_adapter_normalizer_count_correction.v1",
        "status": "PASS_READ_ONLY_NORMALIZER_COUNT_CORRECTION",
        "initial_result": {
            "commit": INITIAL_RESULT_COMMIT,
            "sha256": INITIAL_RESULT_SHA256,
            "status": initial["status"],
            "failed_checks": initial["failed_checks"],
        },
        "checks": checks,
        "failed_checks": failed,
        "incorrect_literal": 8_048_640,
        "protected_source_count": source_count,
        "expanded_checkpoint_count": expanded_count,
        "formal_artifacts_reused": {
            "expanded_checkpoint_directory_sha256": sha256_directory(expanded_path),
            "final_checkpoint_directory_sha256": sha256_directory(trained_checkpoint),
            "final_onnx_sha256": sha256(trained_onnx),
        },
        "corrected_result": {
            "path": str(RESULT_JSON.relative_to(ROOT)),
            "status": corrected["status"],
        },
        "authority": {
            "single_cpu_training_curriculum": True,
            "hosted_or_colab": False, "gpu_or_igpu": False,
            "rdkx5_or_robot": False, "runtime_or_deployment": False,
            "robot_clearance": False,
        },
    }
    CORRECTION_JSON.write_text(json.dumps(correction, indent=2, sort_keys=True) + "\n")
    CORRECTION_MD.write_text(f"""# Winner-v3 Recurrent-Adapter Normalizer Count Correction — 2026-07-19

Decision: `PASS_READ_ONLY_NORMALIZER_COUNT_CORRECTION`

The initial contract's only failed check used the wrong persistent-checkpoint
count. The hash-bound T2_EQUAL 512K source count is `{source_count:,}`, not
`8,048,640`. The formal expanded checkpoint contains exactly the source count,
64 zero means, 64 unit standard deviations, and 64 summed-variance values of
`{source_count:,}`. Every formal artifact hash and every other initial contract
check remains exact. The CPU smoke was not rerun.

The corrected contract decision is
`PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`. This corrects bookkeeping
only and grants no behavior, runtime, hardware, deployment, or robot clearance.
""")
    print(corrected["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
