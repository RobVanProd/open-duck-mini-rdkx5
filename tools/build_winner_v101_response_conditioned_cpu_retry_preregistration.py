#!/usr/bin/env python3
"""Preregister the Winner-v101 unused-TensorFlow-import correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V100_PREREGISTRATION = (
    ANALYSIS / "winner_v100_response_conditioned_cpu_retry_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "winner_v100_preoptimizer_tensorflow_import_attribution.json"
OUTPUT = ANALYSIS / "winner_v101_response_conditioned_cpu_retry_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V101_RESPONSE_CONDITIONED_CPU_RETRY_PREREGISTRATION_20260722.md"
)
V100_PREREGISTRATION_SHA256 = (
    "16f52fc87b0e43682477a1d6aa9be7a1d42bfc916b371e20df4d912ba8ad27b8"
)
ATTRIBUTION_SHA256 = (
    "14e251287012684af5a0ff12031ec6e198cf6e1cb8ebb46ef6561d575e16b302"
)
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v101 contract: {path}")

    playground = args.playground_root.resolve()
    v100 = json.loads(V100_PREREGISTRATION.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    boundary = attribution.get("execution_boundary", {})
    if (
        sha256(V100_PREREGISTRATION) != V100_PREREGISTRATION_SHA256
        or v100.get("status")
        != "PREREGISTERED_WINNER_V100_RESPONSE_CONDITIONED_CPU_RETRY"
        or sha256(ATTRIBUTION) != ATTRIBUTION_SHA256
        or attribution.get("status")
        != "HOLD_WINNER_V100_PREOPTIMIZER_UNUSED_TENSORFLOW_IMPORT"
        or boundary.get("optimizer_steps") != 0
        or boundary.get("ppo_locomotion_steps") != 0
        or boundary.get("ppo_environment_constructed") is not False
        or boundary.get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v101 retry prerequisite changed")

    old_sources = v100["sources"]
    for name, item in old_sources.items():
        if name in {"runner", "integration_patch"}:
            continue
        if lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v101 unrelated source changed: {name}")

    runner = ROOT / old_sources["runner"]["path"]
    integration_patch = ROOT / old_sources["integration_patch"]["path"]
    runner_text = runner.read_text(encoding="utf-8")
    patch_text = integration_patch.read_text(encoding="utf-8")
    if (
        lf_sha256(runner) == old_sources["runner"]["sha256"]
        or lf_sha256(integration_patch)
        == old_sources["integration_patch"]["sha256"]
        or "winner_v101_response_conditioned_cpu_retry_preregistration.json"
        not in runner_text
        or "winner_v100_response_conditioned_cpu_retry_preregistration.json"
        in runner_text
        or "-from playground.common.export_onnx import export_onnx" not in patch_text
        or "+            from playground.common.export_onnx import export_onnx"
        not in patch_text
    ):
        raise ValueError("Winner-v101 lazy-import correction is absent")

    manifest_path = playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != "winner_v98.composed_playground_source.v1"
        or manifest.get("control_commit") != CONTROL_COMMIT
        or manifest.get("stop_before_winner_v98") is not False
    ):
        raise ValueError("Winner-v101 composed source manifest changed")
    composed_relative_paths = tuple(v100["composed_playground_files"])
    composed_files = {
        relative: sha256(playground / relative)
        for relative in composed_relative_paths
    }
    changed_composed = sorted(
        relative
        for relative, digest in composed_files.items()
        if digest != v100["composed_playground_files"][relative]
    )
    if changed_composed != [
        "WINNER_V98_COMPOSED_SOURCE.diff",
        "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "playground/common/runner.py",
    ]:
        raise ValueError(f"Winner-v101 composed change scope changed: {changed_composed}")
    composed_runner = (playground / "playground/common/runner.py").read_text(
        encoding="utf-8"
    )
    prefix, response_branch = composed_runner.split(
        'elif self.args.policy_architecture == "response_conditioned_reference_residual":',
        maxsplit=1,
    )
    generic_branch = response_branch.split("else:", maxsplit=1)[1]
    if (
        "from playground.common.export_onnx import export_onnx" in prefix
        or "from playground.common.export_onnx import export_onnx"
        not in generic_branch
    ):
        raise ValueError("Winner-v101 composed runner still eagerly imports TensorFlow")

    value = dict(v100)
    value["schema_version"] = (
        "winner_v101.response_conditioned_cpu_retry_preregistration.v1"
    )
    value["status"] = "PREREGISTERED_WINNER_V101_RESPONSE_CONDITIONED_CPU_RETRY"
    value["decision"] = "AUTHORIZE_ONE_LAZY_IMPORT_CORRECTED_1024_STEP_CPU_SMOKE_ONLY"
    sources = {name: dict(item) for name, item in old_sources.items()}
    for name, path in {
        "runner": runner,
        "integration_patch": integration_patch,
    }.items():
        sources[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(path),
        }
    for name, relative in {
        "v101_retry_builder": "tools/build_winner_v101_response_conditioned_cpu_retry_preregistration.py",
        "v100_import_attribution_builder": "tools/build_winner_v100_preoptimizer_tensorflow_import_attribution.py",
    }.items():
        sources[name] = {
            "path": relative,
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / relative),
        }
    value["sources"] = sources
    value["source_manifest_sha256"] = canonical_sha256(sources)
    value["composed_playground_files"] = composed_files
    value["composed_playground_manifest_sha256"] = sha256(manifest_path)
    value["retry_of"] = {
        "v100_preregistration_sha256": V100_PREREGISTRATION_SHA256,
        "v100_failure_attribution_sha256": ATTRIBUTION_SHA256,
        "ppo_subprocess_started": True,
        "ppo_environment_constructed": False,
        "ppo_locomotion_steps": 0,
        "optimizer_steps": 0,
    }
    value["correction"] = {
        "unused_generic_exporter_import": (
            "remove the eager generic export_onnx import and import it only inside "
            "the generic export branch; the response-conditioned exporter remains "
            "TensorFlow-independent"
        ),
        "policy_equations_changed": False,
        "calibrator_equations_changed": False,
        "training_hyperparameters_changed": False,
        "thresholds_changed": False,
        "behavior_gate_changed": False,
    }
    value["execution_now"] = {
        "optimizer_steps": 0,
        "simulator_locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    value["authority"] = {
        "formal_cpu_retry_authorized": True,
        "result_authorizes": (
            "only preparation of a separate hosted curriculum preregistration if all "
            "checks pass"
        ),
        "additional_retry_authorized": False,
        "hosted_or_colab_training_authorized_now": False,
        "checkpoint_selection_authorized": False,
        "deployment_authorized": False,
        "gate5_authorized": False,
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v101 response-conditioned CPU retry preregistration\n\n"
        "Winner-v100 reached the PPO subprocess but stopped before environment "
        "construction, reset, locomotion, or optimization because an unused generic "
        "exporter eagerly imported TensorFlow. Winner-v101 changes only that import "
        "boundary. Policy/calibrator equations, training settings, thresholds, golden "
        "checks, and behavior gates remain frozen. Exactly one CPU smoke is authorized; "
        "no hosted or robot work is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
