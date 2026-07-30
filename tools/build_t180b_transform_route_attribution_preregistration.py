#!/usr/bin/env python3
"""Correct T180's comparator binding without changing its analysis."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t180b_transform_route_attribution_recovery.py"
TEST = ROOT / "tests" / "test_t180b_transform_route_attribution_recovery.py"
T180_PREREG = ANALYSIS / "t180_transform_route_attribution_preregistration.json"
RECOVERY = ANALYSIS / "t180_input_mapping_recovery_20260730.json"
T177 = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"
OUTPUT = ANALYSIS / "t180b_transform_route_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T180B_TRANSFORM_ROUTE_ATTRIBUTION_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
    verify_receipt,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def select_block(
    blocks: list[Mapping[str, Any]],
    *,
    condition_id: str,
    checkpoint_id: str,
    fit_id: str,
) -> Mapping[str, Any]:
    matches = [
        block
        for block in blocks
        if block["condition_id"] == condition_id
        and block["checkpoint_id"] == checkpoint_id
        and block["fit_id"] == fit_id
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "condition/checkpoint/fit block binding is not unique: "
            f"{condition_id}:{checkpoint_id}:{fit_id}"
        )
    return matches[0]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T180B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T180B preregistration requires a clean worktree")
    prior = _load_json(T180_PREREG)
    recovery = _load_json(RECOVERY)
    t177 = _load_json(T177)
    if (
        prior.get("preregistered_contract_sha256")
        != "900683b939d287e47b3db42b5893127991e128442af73d3b9aefd7ed2a19978a"
        or recovery.get("result_sha256")
        != "1e53786cf370ef0a353bdd261af1c353c121cfa18685201715e3658580f369d0"
        or recovery.get("status") != "INVALID_T180_INPUT_MAPPING_NO_RESULT"
    ):
        raise RuntimeError("T180B recovery identity differs")
    cases = []
    commands = [0.0, 0.074, 0.077, 0.08]
    for source_case in prior["cases"]:
        case = dict(source_case)
        if case["condition_id"] == "TORSO_COM_Z_POS":
            checkpoint_id = (
                "T175_HEAD_MEAN_HALF"
                if case["checkpoint_pair"] == "half"
                else "T175_HEAD_MEAN_FINAL"
            )
            block = select_block(
                t177["blocks"],
                condition_id=case["condition_id"],
                checkpoint_id=checkpoint_id,
                fit_id=case["fit_id"],
            )
            verify_receipt(block["manifest"], f"corrected:{case['case_id']}")
            manifest = _load_json(Path(block["manifest"]["path"]))
            if (
                manifest["block_contract"]["condition"]["id"]
                != case["condition_id"]
            ):
                raise RuntimeError("corrected manifest condition differs")
            index = commands.index(float(case["command_x_m_s"]))
            trace = manifest["traces"][index]
            verify_receipt(trace, f"corrected_trace:{case['case_id']}")
            case["transformed_trace"] = trace
        cases.append(case)
    for case in cases:
        for role in ("source_trace", "transformed_trace"):
            verify_receipt(case[role], f"{case['case_id']}:{role}")
    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "invalid_t180_preregistration": T180_PREREG,
        "input_mapping_recovery": RECOVERY,
        "t177_terminal_result": T177,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t180b_transform_route_attribution_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T180B_TRANSFORM_ROUTE_ATTRIBUTION_RECOVERY"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "recovery_sha256": recovery["result_sha256"],
        "superseded_contract_sha256": prior["preregistered_contract_sha256"],
        "cases": cases,
        "analysis_contract": prior["analysis_contract"],
        "decision_rule": prior["decision_rule"],
        "correction": {
            "changed_field": "positive-Z transformed trace receipts only",
            "binding_key": ["condition_id", "checkpoint_id", "fit_id"],
            "all_case_definitions_unchanged": True,
            "all_thresholds_and_decisions_unchanged": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": prior["execution_now"],
        "authority_after_result": prior["authority_after_result"],
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T180B corrected transform-route attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Correction: bind every trace by condition, checkpoint, and fit\n"
        "- Unchanged: six cases, 162 ticks, replay/cosine thresholds, decisions\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
