#!/usr/bin/env python3
"""Preregister the cwd-only Winner-v99 CPU smoke correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V98_PREREGISTRATION = (
    ANALYSIS / "winner_v98_response_conditioned_training_preregistration.json"
)
ATTRIBUTION = ANALYSIS / "winner_v98_preoptimizer_failure_attribution.json"
OUTPUT = ANALYSIS / "winner_v99_response_conditioned_cpu_retry_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V99_RESPONSE_CONDITIONED_CPU_RETRY_PREREGISTRATION_20260722.md"
)
V98_PREREGISTRATION_SHA256 = (
    "dc986066f92560d86201e79d6f34ae5b6e18fc5f8f60ea0d2fb394cea09dec95"
)
ATTRIBUTION_SHA256 = (
    "06461c0c2aae30fe51b613447549a38087bae4a6159b1c8dd17906d27d31e270"
)


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
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v99 contract: {path}")
    v98 = json.loads(V98_PREREGISTRATION.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        sha256(V98_PREREGISTRATION) != V98_PREREGISTRATION_SHA256
        or v98.get("status")
        != "PREREGISTERED_WINNER_V98_RESPONSE_CONDITIONED_CPU_SMOKE"
        or sha256(ATTRIBUTION) != ATTRIBUTION_SHA256
        or attribution.get("status")
        != "HOLD_WINNER_V98_PREOPTIMIZER_PATH_BINDING"
        or attribution.get("observed_failure", {}).get("optimizer_steps") != 0
        or attribution.get("observed_failure", {}).get("simulator_locomotion_steps")
        != 0
    ):
        raise ValueError("Winner-v99 retry prerequisite changed")
    old_sources = v98["sources"]
    for name, item in old_sources.items():
        if name == "runner":
            continue
        if lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v99 non-runner source changed: {name}")
    runner = ROOT / old_sources["runner"]["path"]
    runner_text = runner.read_text(encoding="utf-8")
    if (
        lf_sha256(runner) == old_sources["runner"]["sha256"]
        or "with working_directory(playground):" not in runner_text
        or "winner_v99_response_conditioned_cpu_contract.json" not in runner_text
    ):
        raise ValueError("Winner-v99 cwd-only runner correction is absent")

    value = dict(v98)
    value["schema_version"] = (
        "winner_v99.response_conditioned_cpu_retry_preregistration.v1"
    )
    value["status"] = "PREREGISTERED_WINNER_V99_RESPONSE_CONDITIONED_CPU_RETRY"
    value["decision"] = "AUTHORIZE_ONE_CORRECTED_1024_STEP_CPU_SMOKE_ONLY"
    sources = {name: dict(item) for name, item in old_sources.items()}
    sources["runner"] = {
        "path": old_sources["runner"]["path"],
        "hash_mode": "lf",
        "sha256": lf_sha256(runner),
    }
    for name, relative in {
        "retry_builder": "tools/build_winner_v99_response_conditioned_cpu_retry_preregistration.py",
        "failure_attribution_builder": "tools/build_winner_v98_preoptimizer_failure_attribution.py",
    }.items():
        sources[name] = {
            "path": relative,
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / relative),
        }
    value["sources"] = sources
    value["source_manifest_sha256"] = canonical_sha256(sources)
    value["retry_of"] = {
        "v98_preregistration_sha256": V98_PREREGISTRATION_SHA256,
        "v98_failure_attribution_sha256": ATTRIBUTION_SHA256,
        "failed_before_first_reset": True,
        "failed_before_simulator_locomotion": True,
        "failed_before_optimizer": True,
    }
    value["correction"] = {
        "changed_source": old_sources["runner"]["path"],
        "old_runner_lf_sha256": old_sources["runner"]["sha256"],
        "new_runner_lf_sha256": sources["runner"]["sha256"],
        "change": (
            "temporarily bind cwd to the exact composed Playground root around only "
            "the manual environment-construction/reset preflight"
        ),
        "network_sources_changed": False,
        "composed_playground_changed": False,
        "binary_sources_changed": False,
        "training_hyperparameters_changed": False,
        "thresholds_changed": False,
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
        "# Winner-v99 response-conditioned CPU retry preregistration\n\n"
        "The Winner-v98 run stopped before reset, simulation, PPO, or optimization. "
        "Winner-v99 changes only the manual preflight cwd binding. All network sources, "
        "binaries, hyperparameters, populations, and thresholds remain frozen. Exactly "
        "one corrected CPU smoke is authorized; no hosted or robot work is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
