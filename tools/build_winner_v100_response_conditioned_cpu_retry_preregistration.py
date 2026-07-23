#!/usr/bin/env python3
"""Preregister the Winner-v100 checker-contract correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V99_PREREGISTRATION = (
    ANALYSIS / "winner_v99_response_conditioned_cpu_retry_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "winner_v99_preoptimizer_contract_attribution.json"
OUTPUT = ANALYSIS / "winner_v100_response_conditioned_cpu_retry_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V100_RESPONSE_CONDITIONED_CPU_RETRY_PREREGISTRATION_20260722.md"
)
V99_PREREGISTRATION_SHA256 = (
    "f847c533020f0d9b8643bbbadad5dae0ab34f38c1ae206867967e2a4c4ee8ea0"
)
ATTRIBUTION_SHA256 = (
    "d4e64864e38872299b5f721700a8d8090a6483e849b3a66e34654df6a1c038f0"
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
            raise FileExistsError(f"refusing to overwrite Winner-v100 contract: {path}")
    playground = args.playground_root.resolve()
    v99 = json.loads(V99_PREREGISTRATION.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        sha256(V99_PREREGISTRATION) != V99_PREREGISTRATION_SHA256
        or v99.get("status")
        != "PREREGISTERED_WINNER_V99_RESPONSE_CONDITIONED_CPU_RETRY"
        or sha256(ATTRIBUTION) != ATTRIBUTION_SHA256
        or attribution.get("status")
        != "HOLD_WINNER_V99_PREOPTIMIZER_CHECKER_CONTRACT"
        or attribution.get("execution_boundary", {}).get("optimizer_steps") != 0
        or attribution.get("execution_boundary", {}).get("ppo_locomotion_steps")
        != 0
    ):
        raise ValueError("Winner-v100 retry prerequisite changed")
    old_sources = v99["sources"]
    for name, item in old_sources.items():
        if name in {"runner", "network"}:
            continue
        if lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v100 unrelated source changed: {name}")
    runner = ROOT / old_sources["runner"]["path"]
    network = ROOT / old_sources["network"]["path"]
    runner_text = runner.read_text(encoding="utf-8")
    network_text = network.read_text(encoding="utf-8")
    if (
        lf_sha256(runner) == old_sources["runner"]["sha256"]
        or lf_sha256(network) == old_sources["network"]["sha256"]
        or "expanded[1] = initialized" not in runner_text
        or "graph_boundary_contract" not in runner_text
        or "apply_action_with_state" not in runner_text
        or "apply_action_with_state" not in network_text
    ):
        raise ValueError("Winner-v100 exact correction is absent")

    manifest_path = playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != "winner_v98.composed_playground_source.v1"
        or manifest.get("control_commit") != CONTROL_COMMIT
        or manifest.get("stop_before_winner_v98") is not False
    ):
        raise ValueError("Winner-v100 composed source manifest changed")
    composed_relative_paths = tuple(v99["composed_playground_files"])
    composed_files = {
        relative: sha256(playground / relative)
        for relative in composed_relative_paths
    }
    changed_composed = sorted(
        relative
        for relative, digest in composed_files.items()
        if digest != v99["composed_playground_files"][relative]
    )
    if changed_composed != [
        "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "playground/common/winner_v98_response_conditioned_ppo_networks.py",
    ]:
        raise ValueError(f"Winner-v100 composed change scope changed: {changed_composed}")

    value = dict(v99)
    value["schema_version"] = (
        "winner_v100.response_conditioned_cpu_retry_preregistration.v1"
    )
    value["status"] = "PREREGISTERED_WINNER_V100_RESPONSE_CONDITIONED_CPU_RETRY"
    value["decision"] = (
        "AUTHORIZE_ONE_CONTRACT_CORRECTED_1024_STEP_CPU_SMOKE_ONLY"
    )
    sources = {name: dict(item) for name, item in old_sources.items()}
    for name, path in {"runner": runner, "network": network}.items():
        sources[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(path),
        }
    for name, relative in {
        "v100_retry_builder": "tools/build_winner_v100_response_conditioned_cpu_retry_preregistration.py",
        "v99_contract_attribution_builder": "tools/build_winner_v99_preoptimizer_contract_attribution.py",
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
        "v99_preregistration_sha256": V99_PREREGISTRATION_SHA256,
        "v99_failure_attribution_sha256": ATTRIBUTION_SHA256,
        "ppo_subprocess_started": False,
        "ppo_locomotion_steps": 0,
        "optimizer_steps": 0,
    }
    value["correction"] = {
        "checkpoint_container": (
            "store the expanded actor as checkpoint-native dict so Orbax round-trip "
            "structure and numeric leaves can both be exact"
        ),
        "graph_parity": (
            "expose and compare the exact final bounded action before its PPO tanh-location "
            "representation; separately report the <=1.1e-5 exact-saturation mode delta"
        ),
        "boundary_check": (
            "verify protected initializers and ordered rate->actual-centered-guard->deadband "
            "graph producers; apply final-rate telemetry only to coherent golden/behavior traces"
        ),
        "actor_equations_changed": False,
        "calibrator_equations_changed": False,
        "training_hyperparameters_changed": False,
        "behavior_gate_changed": False,
    }
    value["thresholds"] = {
        "zero_update_selected_and_golden_max_abs_at_most": 1.0e-6,
        "exact_pre_location_action_and_hidden_jax_onnx_max_abs_at_most": 1.0e-6,
        "ppo_mode_exact_saturation_representation_max_abs_at_most": 1.1e-5,
        "coherent_golden_final_rate_excess_at_most": 1.0e-6,
        "protected_parameter_update_exactly": 0.0,
        "adapter_state_context_action_update_strictly_above": 0.0,
        "wall_seconds_at_most": 3600.0,
    }
    value["pass_rule"] = [
        "all source, binary, environment, and corrected composed-source hashes match",
        "the selected 512K source checkpoint restores on CPU and expands through a bit-exact numeric and container-structure Orbax round trip",
        "the step-zero graph reproduces all 1,200 frozen x=0/x=.08 golden ticks within 1e-6, retains exact x=0 zero action, and has <=1e-6 coherent-trace final-rate excess",
        "the exported graph retains exact protected initializers and the frozen rate-stage then actual-centered-guard then deadband hierarchy",
        "the exact pre-location bounded action and hidden state agree between JAX and ONNX within 1e-6; any PPO-mode delta above 1e-6 must occur only at exact graph saturation and remain <=1.1e-5",
        "reset runs exactly 250 calibration ticks plus 250 home-return ticks outside PPO transitions, resets phase to [1,0], and produces one finite immutable 64-D context",
        "one 1,024-step CPU PPO smoke keeps every protected leaf exact while adapter state, context, and action families each update",
        "step-zero and step-1,024 ONNX graphs expose the exact stateful ABI and preserve exact x=0 deadband",
    ]
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
        "# Winner-v100 response-conditioned CPU retry preregistration\n\n"
        "Winner-v99 stopped before PPO. Winner-v100 corrects only checkpoint container "
        "identity and two invalid checker interpretations. Policy/calibrator equations, "
        "training settings, golden thresholds, and behavior gates remain frozen. Exactly "
        "one CPU smoke is authorized; no hosted or robot work is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
