#!/usr/bin/env python3
"""Validate the recovered RESET_EST_LATCH_U05 hosted artifact on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile
import tempfile

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import numpy as np
import onnx
import onnxruntime as ort


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "outputs/analysis/ground_up_reset_com_estimator_epsilon2_hosted_run_20260715/recovery"
ARCHIVE = ROOT / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz"
MANIFEST = ROOT / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json"
LAUNCH = ROOT / "GROUND_UP_RESET_COM_ESTIMATOR_EPSILON_AWARE_launch.json"
EXPECTED = {
    "archive": "88bf9c799e3a44e7f7817823166ee4365cc574a1a68d662930ae448884563673",
    "manifest": "e7530cfea3f891cb0dbda0970c98394ba4f06544743f5d7dab9a8f8074a1f359",
    "launch": "489a0fa0f68492aa58e2ef8e68daf1bc3710f55be608b5e7069ee8933be87b22",
}
EXPECTED_ONNX = {
    "2026_07_15_221958_0.onnx": "79757d20eb9d47479c7b04999edc43906aaf607b04b728fc6c14221ddf8c3865",
    "2026_07_15_222310_1003520.onnx": "3960e027c1953dff5f10ba58bf857bc1182c734b028354f03f6dae51955bfd5f",
    "2026_07_15_222753_2007040.onnx": "0d3c20544851d2ad7f678d29bdcb55338e1c56b9b59f95d1ad2ce172c439cefe",
}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    hashes = {"archive": sha256(ARCHIVE), "manifest": sha256(MANIFEST),
              "launch": sha256(LAUNCH)}
    manifest = json.loads(MANIFEST.read_text())
    launch = json.loads(LAUNCH.read_text())
    with tempfile.TemporaryDirectory(prefix="reset_estimator_artifact_") as temporary:
        root = Path(temporary)
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            members = archive.getmembers()
            safe = all(not Path(member.name).is_absolute()
                       and ".." not in Path(member.name).parts for member in members)
            if not safe:
                raise RuntimeError("unsafe archive member")
            archive.extractall(root, filter="data")
        output = root / "ground_up_reset_estimator_outputs"
        arm = output / "RESET_EST_LATCH_U05"
        internal_manifest = json.loads((output / MANIFEST.name).read_text())
        original_report = json.loads((output / "hosted_expansion_report_original_1e7.json").read_text())
        corrected_report = json.loads((output / "hosted_expansion_report.json").read_text())
        checkpoint_hashes = {
            path.name: sha256_directory(path) for path in arm.iterdir() if path.is_dir()
        }
        onnx_rows = []
        for path in sorted(arm.glob("*.onnx")):
            model = onnx.load(path)
            onnx.checker.check_model(model)
            session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
            inputs = {item.name: list(item.shape) for item in session.get_inputs()}
            feed = {item.name: np.zeros(tuple(int(value) for value in item.shape), dtype=np.float32)
                    for item in session.get_inputs()}
            values = session.run(None, feed)
            onnx_rows.append({
                "name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size,
                "inputs": inputs,
                "outputs": {item.name: list(item.shape) for item in session.get_outputs()},
                "finite": all(np.isfinite(value).all() for value in values),
                "providers": session.get_providers(),
            })
        checkpoint_expected = {row["name"]: row["directory_sha256"]
                               for row in manifest["arm"]["checkpoints"]}
        event_files = list(arm.glob("events.out.tfevents.*"))
        checks = {
            "recovered_hashes_exact": hashes == EXPECTED,
            "archive_members_safe_and_root_exact": safe and output.is_dir()
            and all(Path(member.name).parts[0] == "ground_up_reset_estimator_outputs"
                    for member in members),
            "internal_external_manifest_exact": internal_manifest == manifest,
            "manifest_status_behavior_and_selection_exact": manifest.get("status")
            == "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY"
            and manifest.get("behavior_status") == "UNEVALUATED"
            and manifest.get("selection")
            == {"behavior_unevaluated": True, "training_reward_used": False},
            "single_arm_steps_exact": manifest.get("arm", {}).get("name")
            == "RESET_EST_LATCH_U05"
            and manifest.get("arm", {}).get("checkpoint_steps") == [0, 1_003_520, 2_007_040]
            and manifest.get("arm", {}).get("expected_steps") == [0, 1_003_520, 2_007_040],
            "checkpoint_directories_hash_exact": checkpoint_hashes == checkpoint_expected
            and len(checkpoint_hashes) == 3,
            "onnx_hash_size_interface_and_cpu_inference_exact": len(onnx_rows) == 3
            and {row["name"]: row["sha256"] for row in onnx_rows} == EXPECTED_ONNX
            and all(row["bytes"] == 906_615 and row["inputs"]
                    == {"obs": [1, 116], "previous_action": [1, 14]}
                    and row["outputs"] == {"continuous_actions": [1, 14],
                                           "previous_action_out": [1, 14]}
                    and row["finite"] and row["providers"] == ["CPUExecutionProvider"]
                    for row in onnx_rows),
            "raw_expansion_failure_preserved_exact": original_report
            == corrected_report.get("raw_original_1e7_report")
            and original_report.get("failed_checks") == ["step_zero_outputs_exact"]
            and original_report.get("status") == "FAIL_HOSTED_CHECKPOINT_EXPANSION",
            "epsilon_aware_expansion_pass_exact": corrected_report.get("status")
            == "PASS_HOSTED_CHECKPOINT_EXPANSION_EPSILON_AWARE"
            and corrected_report.get("failed_checks") == []
            and corrected_report.get("threshold", {}).get("value") == 2.0 ** -23
            and corrected_report.get("maximum_actor_error") == 2.0 ** -23
            and corrected_report.get("maximum_critic_error") == 0.0
            and corrected_report == manifest.get("hosted_expansion"),
            "training_log_and_event_present": (arm / "training.log").stat().st_size > 0
            and len(event_files) == 1 and event_files[0].stat().st_size > 0,
            "command_and_recipe_exact": manifest["arm"]["command"].count("--num_timesteps") == 1
            and manifest["arm"]["command"][manifest["arm"]["command"].index("--num_timesteps") + 1] == "2000000"
            and "--ground_up_reset_com_estimator_input" in manifest["arm"]["command"]
            and "--ground_up_torso_com_randomization" in manifest["arm"]["command"],
            "hosted_limits_and_devices_exact": manifest["execution"]["total_seconds"] <= 2_400
            and manifest["execution"]["maximum_hosted_seconds"] == 2_400
            and manifest["execution"]["session_count"] == 1
            and manifest["execution"]["training_process_count"] == 1
            and manifest["execution"]["resume"] is False
            and manifest["execution"]["versions_and_devices"]
            == ["0.8.2 0.8.2 3.9.0", "[CudaDevice(id=0)]", "HAS_GPU True"],
            "launcher_recovery_cleanup_and_wall_exact": launch.get("status")
            == "PASS_HOSTED_ARTIFACTS_RECOVERED"
            and launch.get("session_stop_passed") is True
            and launch.get("session_wall_within_ceiling") is True
            and launch.get("session_elapsed_seconds", 2401) <= 2400
            and launch.get("compute_units") == "UNMEASURED",
            "local_validation_cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == ""
            and os.environ.get("JAX_PLATFORMS") == "cpu",
        }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "ground_up_reset_com_estimator_hosted_artifact_contract.v1",
        "status": "PASS_RESET_ESTIMATOR_HOSTED_ARTIFACT_CONTRACT" if not failed else "FAIL_RESET_ESTIMATOR_HOSTED_ARTIFACT_CONTRACT",
        "checks": checks, "failed_checks": failed, "source_hashes": hashes,
        "manifest": manifest, "checkpoint_hashes": checkpoint_hashes,
        "onnx": onnx_rows,
        "execution": {"cpu_only": True, "colab_sessions_created": 0,
                      "training_steps": 0, "behavior_cells": 0,
                      "local_gpu_or_igpu": False, "robot_or_rdk": False},
        "authority": {"evaluation_policy_transform_contract_next_if_pass": True,
                      "behavior_evaluation_now": False,
                      "training": False, "colab": False,
                      "robot_or_rdk": False},
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
