#!/usr/bin/env python3
"""Record the pre-optimizer Winner-v98 path-binding failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v98_response_conditioned_training_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v98_preoptimizer_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V98_PREOPTIMIZER_FAILURE_ATTRIBUTION_20260722.md"
PREREGISTRATION_SHA256 = (
    "dc986066f92560d86201e79d6f34ae5b6e18fc5f8f60ea0d2fb394cea09dec95"
)


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
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--failed-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v98 attribution: {path}")
    playground = args.playground_root.resolve()
    work = args.failed_work_root.resolve()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V98_RESPONSE_CONDITIONED_CPU_SMOKE"
        or preregistration.get("execution_now")
        != {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v98 failed-run preregistration changed")
    runner_item = preregistration["sources"]["runner"]
    if lf_sha256(ROOT / runner_item["path"]) != runner_item["sha256"]:
        raise ValueError("Winner-v98 failed runner source changed before attribution")
    expected_top_level = {"expanded_checkpoint", "winner_v98_step_zero.onnx"}
    actual_top_level = {path.name for path in work.iterdir()}
    if actual_top_level != expected_top_level:
        raise ValueError(f"Winner-v98 failed work population changed: {actual_top_level}")
    relative_asset = Path(
        "playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"
    )
    composed_asset = playground / relative_asset
    wrong_resolution = ROOT / relative_asset
    if not composed_asset.is_file() or wrong_resolution.exists():
        raise ValueError("Winner-v98 path-binding attribution precondition changed")
    if (ANALYSIS / "winner_v98_response_conditioned_cpu_contract.json").exists():
        raise ValueError("Winner-v98 formal result unexpectedly exists")
    value = {
        "schema_version": "winner_v98.preoptimizer_failure_attribution.v1",
        "status": "HOLD_WINNER_V98_PREOPTIMIZER_PATH_BINDING",
        "decision": "AUTHORIZE_PATH_BINDING_CORRECTION_PREREGISTRATION_ONLY",
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "observed_failure": {
            "exception": "FileNotFoundError",
            "missing_relative_path": relative_asset.as_posix(),
            "failure_stage": "manual reset checker environment construction",
            "first_reset_completed": False,
            "simulator_locomotion_steps": 0,
            "optimizer_steps": 0,
            "ppo_subprocess_started": False,
        },
        "causal_attribution": {
            "asset_exists_under_composed_playground": True,
            "asset_exists_under_policy_repository_cwd": False,
            "cause": (
                "the preflight checker instantiated Playground while cwd remained the "
                "policy repository, but PolyReferenceMotion resolves its frozen data path "
                "relative to the composed Playground root"
            ),
            "policy_math_implicated": False,
            "calibration_math_implicated": False,
            "checkpoint_or_onnx_implicated": False,
        },
        "recovered_preflight_artifacts": {
            "expanded_checkpoint_directory_sha256": directory_sha256(
                work / "expanded_checkpoint"
            ),
            "step_zero_onnx_sha256": sha256(work / "winner_v98_step_zero.onnx"),
        },
        "prospective_correction": {
            "change": (
                "bind cwd to the exact composed Playground root only while constructing "
                "and executing the manual reset preflight"
            ),
            "network_source_changed": False,
            "training_hyperparameters_changed": False,
            "threshold_changed": False,
            "new_run_requires_new_preregistration": True,
        },
        "authority": {
            "retry_authorized_now": False,
            "optimizer_or_simulator_authorized_now": False,
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
        "# Winner-v98 pre-optimizer failure attribution\n\n"
        "Status: `HOLD_WINNER_V98_PREOPTIMIZER_PATH_BINDING`\n\n"
        "The formal run stopped before reset, simulation, PPO, or any optimizer step. "
        "The composed simulator asset exists; the checker launched from the wrong cwd. "
        "Only a separately preregistered cwd-binding correction may retry.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
