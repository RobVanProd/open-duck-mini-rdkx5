#!/usr/bin/env python3
"""Record the pre-environment Winner-v100 TensorFlow import failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v100_response_conditioned_cpu_retry_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v100_preoptimizer_tensorflow_import_attribution.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V100_PREOPTIMIZER_TENSORFLOW_IMPORT_ATTRIBUTION_20260722.md"
)
PREREGISTRATION_SHA256 = (
    "16f52fc87b0e43682477a1d6aa9be7a1d42bfc916b371e20df4d912ba8ad27b8"
)
LOG_SHA256 = "d0fc25b53f1f9dd4b1ecda841a7747db0313198ace9231c57ed88414652a7bab"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failed-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v100 attribution: {path}")
    work = args.failed_work_root.resolve()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V100_RESPONSE_CONDITIONED_CPU_RETRY"
    ):
        raise ValueError("Winner-v100 preregistration changed")
    for name, item in preregistration["sources"].items():
        if lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v100 source changed before attribution: {name}")
    log = work / "winner_v98_response_conditioned_cpu_smoke.log"
    smoke = work / "smoke"
    if (
        sha256(log) != LOG_SHA256
        or any(smoke.iterdir())
        or "ModuleNotFoundError: No module named 'tensorflow'"
        not in log.read_text(encoding="utf-8")
        or (ANALYSIS / "winner_v100_response_conditioned_cpu_contract.json").exists()
    ):
        raise ValueError("Winner-v100 failed-run evidence changed")
    value = {
        "schema_version": "winner_v100.preoptimizer_tensorflow_import_attribution.v1",
        "status": "HOLD_WINNER_V100_PREOPTIMIZER_UNUSED_TENSORFLOW_IMPORT",
        "decision": "AUTHORIZE_LAZY_GENERIC_EXPORT_IMPORT_PREREGISTRATION_ONLY",
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "execution_boundary": {
            "manual_pretraining_contract_passed": True,
            "automatic_calibration_ticks_completed": 250,
            "home_return_ticks_completed": 250,
            "ppo_subprocess_started": True,
            "ppo_environment_constructed": False,
            "ppo_reset_completed": False,
            "ppo_locomotion_steps": 0,
            "optimizer_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "failure": {
            "exception": "ModuleNotFoundError",
            "missing_module": "tensorflow",
            "log_path": str(log),
            "log_sha256": LOG_SHA256,
            "import_chain": [
                "open_duck_mini_v2/runner.py",
                "common/runner.py",
                "common/export_onnx.py",
                "tensorflow",
            ],
        },
        "causal_attribution": {
            "generic_exporter_selected": False,
            "response_conditioned_exporter_requires_tensorflow": False,
            "cause": (
                "common/runner.py imports the TensorFlow-backed generic exporter at module "
                "load even though the selected response-conditioned architecture uses its "
                "dedicated ONNX exporter"
            ),
            "policy_or_calibration_math_implicated": False,
            "simulator_or_optimizer_implicated": False,
        },
        "preserved_preflight_artifacts": {
            "expanded_checkpoint_directory_sha256": directory_sha256(
                work / "expanded_checkpoint"
            ),
            "step_zero_onnx_sha256": sha256(work / "winner_v98_step_zero.onnx"),
        },
        "prospective_correction": {
            "remove_eager_generic_export_import": True,
            "import_generic_exporter_only_in_generic_branch": True,
            "network_source_changed": False,
            "training_hyperparameters_changed": False,
            "threshold_changed": False,
            "new_run_requires_new_preregistration": True,
        },
        "authority": {
            "retry_authorized_now": False,
            "optimizer_authorized_now": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v100 pre-optimizer TensorFlow-import attribution\n\n"
        "Status: `HOLD_WINNER_V100_PREOPTIMIZER_UNUSED_TENSORFLOW_IMPORT`\n\n"
        "All manual preflight checks passed. The PPO subprocess then stopped during "
        "module import, before environment construction, reset, rollout, or optimization. "
        "The response-conditioned exporter does not use TensorFlow; only the unused generic "
        "exporter was imported eagerly. A separately preregistered lazy-import correction "
        "is required.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
