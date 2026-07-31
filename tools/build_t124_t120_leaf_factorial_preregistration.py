#!/usr/bin/env python3
"""Freeze read-only T120 half-to-final router/expert attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T121 = ANALYSIS / "t121_t120_recovered_training_validation.json"
T122 = ANALYSIS / "t122_t120_postexport_result.json"
T123 = ANALYSIS / "t123_t120_nominal_result.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t124_t120_leaf_factorial.py"
TEST = ROOT / "tests" / "test_t124_t120_leaf_factorial.py"
OUTPUT = ANALYSIS / "t124_t120_leaf_factorial_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T124_T120_LEAF_FACTORIAL_PREREGISTRATION_20260729.md"
)
CACHE = Path("D:/CodexArtifacts/open-duck-policy/t123_t120_nominal_v1")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def block(result: dict[str, Any], checkpoint: str) -> dict[str, Any]:
    matches = [
        item
        for item in result["blocks"]
        if item["checkpoint_id"] == checkpoint
        and item["fit_id"] == "p31_34"
    ]
    if len(matches) != 1:
        raise RuntimeError(f"changed T123 P31/34 block: {checkpoint}")
    return matches[0]


def trace_path(checkpoint: str) -> Path:
    return (
        CACHE
        / "02_FLOOR_FRICTION_HI"
        / checkpoint
        / "p31_34"
        / "traces"
        / "x0.080_seed167931544_action_margin.jsonl"
    )


def green_cells(item: dict[str, Any]) -> int:
    return sum(bool(cell["cell_green"]) for cell in item["result"]["cells"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T124 requires --read-only-authorized")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T124: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T124 preregistration requires clean worktree")

    t121 = json.loads(T121.read_text(encoding="utf-8"))
    t122 = json.loads(T122.read_text(encoding="utf-8"))
    t123 = json.loads(T123.read_text(encoding="utf-8"))
    half_id = "T120_JOINT_SOFT_ROUTER_HALF"
    final_id = "T120_JOINT_SOFT_ROUTER_FINAL"
    half_block = block(t123, half_id)
    final_block = block(t123, final_id)
    graphs = {
        "half": t122["deployments"]["1003520"]["context_abi"],
        "final": t122["deployments"]["2007040"]["context_abi"],
    }
    traces = {
        "half_failed": receipt(trace_path(half_id)),
        "final_passed": receipt(trace_path(final_id)),
    }
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t121_result": T121,
        "t122_result": T122,
        "t123_result": T123,
    }
    checks = {
        "t121_exact_actor_scope": (
            t121["status"]
            == "PASS_T121_T120_RECOVERED_TRAINING_VALIDATION"
            and t121["failed_checks"] == []
        ),
        "t122_transform_green": (
            t122["status"] == "PASS_T122_T120_POSTEXPORT_TRANSFORM"
            and t122["failed_checks"] == []
        ),
        "t123_exact_15_of_16_hold": (
            t123["status"] == "HOLD_T123_T120_NOMINAL_MATRIX"
            and t123["condition"]["green_cells"] == 15
        ),
        "half_p31_has_one_failure": (
            green_cells(half_block) == 3
        ),
        "final_p31_all_green": green_cells(final_block) == 4,
        "graphs_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in graphs.values()
        ),
        "traces_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in traces.values()
        ),
        "inputs_present": all(path.is_file() for path in inputs.values()),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t124_t120_leaf_factorial_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T124_T120_LEAF_FACTORIAL"
            if not failed
            else "HOLD_T124_T120_LEAF_FACTORIAL_PREREGISTRATION"
        ),
        "question": (
            "Did the router, the negative-COM expert, or their multiplicative "
            "interaction dominate T120's half-to-final repair of the sole "
            "nominal failure?"
        ),
        "graphs": graphs,
        "traces": traces,
        "factorial": {
            "variants": {
                "HH": "half router + half expert",
                "HF": "half router + final expert",
                "FH": "final router + half expert",
                "FF": "final router + final expert",
            },
            "swapped_initializers": {
                "router": [
                    "hidden_gate_coefficient",
                    "hidden_gate_intercept",
                ],
                "expert": [
                    "negative_adapter_weight",
                    "negative_adapter_bias",
                ],
            },
            "observed_outputs": [
                "continuous_actions",
                "soft_negative_com_weight",
                "negative_adapter_location",
                "conditional_adapter_location",
            ],
            "critical_window": {
                "trace": "half_failed",
                "last_ticks": 40,
                "defined_before_execution": True,
            },
            "decomposition": (
                "router=FH-HH; expert=HF-HH; "
                "interaction=FF-FH-HF+HH"
            ),
            "classification": (
                "largest RMS continuous-action component over the frozen "
                "critical window"
            ),
        },
        "decision_rule": {
            "router_dominant": "EARN_ROUTER_FIRST_CPU_SCREEN_ONLY",
            "expert_dominant": "EARN_EXPERT_FIRST_CPU_SCREEN_ONLY",
            "interaction_dominant": (
                "EARN_NOMINAL_CONTINUITY_CONSTRAINED_CPU_SCREEN_ONLY"
            ),
            "no_hosted_training": True,
            "no_behavior_selection": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_read_only_leaf_factorial": not failed,
            "simulator": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T124 T120 leaf-factorial preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: the frozen failed half and passing final x=.08 P31/34 traces\n"
        "- Factorial: half/final router x half/final negative-COM expert\n"
        "- Simulator / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
