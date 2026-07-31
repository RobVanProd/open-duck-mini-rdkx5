#!/usr/bin/env python3
"""Freeze the T74 negative-direction recurrent-core secant extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T68 = ANALYSIS / "t68_t67_postexport_result.json"
T72 = ANALYSIS / "t72_signed_core_mirror_result.json"
T73 = ANALYSIS / "t73_signed_core_mirror_condition7_result.json"
T71_PREREG = ANALYSIS / "t71_t67_com_hidden_causal_preregistration_v2.json"
RUNNER = ROOT / "tools" / "run_t74_signed_core_secant_transform.py"
DEPLOYMENT = ROOT / "tools" / "run_t31_action_margin_trainthrough_cpu_smoke.py"
TEST = ROOT / "tests" / "test_t74_signed_core_secant.py"
OUTPUT = ANALYSIS / "t74_signed_core_secant_preregistration.json"
MARKDOWN = ANALYSIS / "T74_SIGNED_CORE_SECANT_PREREGISTRATION_20260728.md"
CORE = [
    "adapter_obs_weight",
    "adapter_hidden_weight",
    "adapter_hidden_bias",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T74: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T74 preregistration requires a clean worktree")
    t68 = json.loads(T68.read_text(encoding="utf-8"))
    t72 = json.loads(T72.read_text(encoding="utf-8"))
    t73 = json.loads(T73.read_text(encoding="utf-8"))
    t71_prereg = json.loads(T71_PREREG.read_text(encoding="utf-8"))
    raw = {
        "source": t68["deployments"]["0"]["raw"],
        "positive_half": t68["deployments"]["1003520"]["raw"],
        "positive_final": t68["deployments"]["2007040"]["raw"],
    }
    checks = {
        "signed_mirror_contract_green": (
            t72["status"] == "PASS_T72_SIGNED_CORE_MIRROR"
            and not t72["failed_checks"]
        ),
        "mirror_behavior_improves_with_endpoint_distance": (
            t73["status"] == "HOLD_T73_SIGNED_CORE_MIRROR_CONDITION7"
            and t73["decision"] == "CLOSE_SIGNED_CORE_MIRROR"
            and sum(
                cell["cell_green"]
                for block in t73["blocks"]
                if block["checkpoint_id"].endswith("HALF")
                for cell in block["result"]["cells"]
            )
            == 4
            and sum(
                cell["cell_green"]
                for block in t73["blocks"]
                if block["checkpoint_id"].endswith("FINAL")
                for cell in block["result"]["cells"]
            )
            == 7
        ),
        "raw_receipts_exact": all(
            Path(item["path"]).is_file()
            and Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in raw.values()
        ),
        "runner_deployment_test_present": all(
            path.is_file() for path in (RUNNER, DEPLOYMENT, TEST)
        ),
        "no_behavior_training_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t74_signed_core_secant_preregistration.v1",
        "status": (
            "PREREGISTERED_T74_SIGNED_CORE_SECANT"
            if not failed
            else "HOLD_T74_SIGNED_CORE_SECANT_PREREGISTRATION"
        ),
        "question": (
            "Does the unique constant-secant extension implied by the frozen "
            "negative 1M/2M endpoints produce persistent 3M/4M-equivalent "
            "control responses worth one condition-7 behavior matrix?"
        ),
        "mechanism": {
            "source": "S = T52 half / T67 step zero",
            "positive_endpoints": "E1 = T67 half; E2 = T67 final",
            "negative_1m": "M1 = 2*S - E1",
            "negative_2m": "M2 = 2*S - E2",
            "negative_3m": "M3 = M2 + (M2-M1) = 2*S + E1 - 2*E2",
            "negative_4m": "M4 = M3 + (M2-M1) = 2*S + 2*E1 - 3*E2",
            "candidates": [
                {
                    "checkpoint_id": "T74_SIGNED_CORE_SECANT_3M",
                    "pseudo_step": 3_010_560,
                    "coefficients_s_e1_e2": [2, 1, -2],
                },
                {
                    "checkpoint_id": "T74_SIGNED_CORE_SECANT_4M",
                    "pseudo_step": 4_014_080,
                    "coefficients_s_e1_e2": [2, 2, -3],
                },
            ],
            "changed_initializers": CORE,
            "all_other_initializers": "bit-exact S",
            "scalar_sweep": False,
            "fit_or_command_conditioning": False,
            "both_endpoints_required": True,
        },
        "raw_graphs": raw,
        "core_initializers": CORE,
        "direction_contract": {
            "trace_population": t71_prereg["shifted_traces"],
            "sample_ticks": [8, 16, 32, 64, 80],
            "commands": [0.074, 0.077, 0.08],
            "minimum_nonzero_pairs_per_endpoint": 50,
            "minimum_fraction_negative_cosine_vs_positive_final": 0.90,
            "maximum_median_cosine_vs_positive_final": 0.0,
        },
        "decision_rule": {
            "pass": (
                "Both exact secant graphs change only the three core tensors, "
                "pass the unchanged deployment chain, and remain oppositely "
                "directed from the positive final update."
            ),
            "pass_decision": (
                "EARN_T75_SIGNED_CORE_SECANT_CONDITION7_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_SIGNED_CORE_SECANT_WITHOUT_BEHAVIOR",
            "no_hosted_run_earned": True,
        },
        "frozen_inputs": {
            "t68_postexport": receipt(T68),
            "t72_transform": receipt(T72),
            "t73_behavior": receipt(T73),
            "t71_trace_contract": receipt(T71_PREREG),
            "runner": receipt(RUNNER),
            "deployment_helper": receipt(DEPLOYMENT),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_two_secant_transforms": not failed,
            "behavior_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T74 signed recurrent-core secant preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Endpoints: fixed negative 3M/4M secant continuation",
                "- Both endpoints required; no alpha sweep",
                "- Behavior / optimizer / Colab / robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
