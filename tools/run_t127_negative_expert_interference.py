#!/usr/bin/env python3
"""Run the frozen negative-expert interference attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t127_negative_expert_interference_preregistration.json"
RESULT = ANALYSIS / "t127_negative_expert_interference_result.json"
MARKDOWN = ANALYSIS / "T127_NEGATIVE_EXPERT_INTERFERENCE_RESULT_20260729.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def verify(item: Mapping[str, Any]) -> Path:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != item["bytes"]
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"changed T127 input: {path}")
    return path


def green_cells(value: dict[str, Any]) -> int:
    return int(value["condition"]["green_cells"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T127 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T127: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T127 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"]
        != "PREREGISTERED_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T127 preregistration changed")
    paths = {name: verify(item) for name, item in prereg["inputs"].items()}
    loaded = {
        name: json.loads(paths[name].read_text(encoding="utf-8"))
        for name in (
            "t67_nominal",
            "t67_negative",
            "t71_hidden_causality",
            "t78_negative",
            "t113_preregistration",
            "t113_negative",
            "t120_preregistration",
            "t124_factorial",
            "t126_negative",
        )
    }
    facts = {
        "t67_nominal_green_cells": green_cells(loaded["t67_nominal"]),
        "t67_negative_green_cells": green_cells(loaded["t67_negative"]),
        "t78_negative_green_cells": int(
            loaded["t78_negative"]["comparison"]["raw_t78_green_cells"]
        ),
        "t113_negative_green_cells": green_cells(loaded["t113_negative"]),
        "t126_negative_green_cells": green_cells(loaded["t126_negative"]),
        "endpoint_strata": int(
            loaded["t120_preregistration"]["training"]["endpoint_strata"]
        ),
        "exact_negative_fraction": 1.0
        / int(loaded["t120_preregistration"]["training"]["endpoint_strata"]),
        "hidden_signal_classification": loaded["t71_hidden_causality"][
            "classification"
        ],
        "t124_nominal_repair": loaded["t124_factorial"]["classification"],
    }
    t113_categories = loaded["t113_preregistration"]["training"][
        "endpoint_strata"
    ]
    t120_categories = loaded["t120_preregistration"]["training"][
        "endpoint_strata"
    ]
    expected = prereg["frozen_facts"]
    checks = {
        "all_frozen_facts_exact": facts == expected,
        "t113_eight_strata": int(t113_categories) == 8,
        "t120_eight_strata": int(t120_categories) == 8,
        "hidden_com_signal_present_and_used": facts[
            "hidden_signal_classification"
        ]
        == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE",
        "expert_dominated_nominal_repair": facts["t124_nominal_repair"]
        == "EXPERT_DOMINANT",
        "negative_performance_never_exceeded_core_baseline": max(
            facts["t78_negative_green_cells"],
            facts["t113_negative_green_cells"],
            facts["t126_negative_green_cells"],
        )
        <= facts["t67_negative_green_cells"],
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t127_negative_expert_interference_result.v1"
        ),
        "status": (
            "PASS_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
            if passed
            else "HOLD_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "MIXED_ENDPOINT_EXPERT_INTERFERENCE_REMAINS_UNFALSIFIED"
            if passed
            else "UNRESOLVED"
        ),
        "causal_conclusion": (
            "The live hidden state already contains and uses COM information, "
            "but every trained correction head received gradients from eight "
            "endpoint strata and none beat the recurrent-core baseline on "
            "negative COM. Exact negative-only training of the existing linear "
            "expert is the smallest untested mechanism; nonlinear capacity is "
            "not yet earned."
        ),
        "facts": facts,
        "checks": checks,
        "failed_checks": failed,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "execution": {
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t128_cpu_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T127 negative-expert interference result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Negative green cells (core/T78/T113/T126): "
        f"`{facts['t67_negative_green_cells']}/"
        f"{facts['t78_negative_green_cells']}/"
        f"{facts['t113_negative_green_cells']}/"
        f"{facts['t126_negative_green_cells']}`\n"
        "- Simulator / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
