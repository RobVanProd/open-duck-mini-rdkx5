#!/usr/bin/env python3
"""Freeze a semantics-preserving removal of one redundant oracle rollout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
SOURCE = ANALYSIS / "winner_v126_exact_oracle_preregistration.json"
CONTRACT = ANALYSIS / "winner_v126_exact_oracle_cpu_contract.json"
OUTPUT = ANALYSIS / "winner_v126_oracle_optimization_amendment.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_ORACLE_OPTIMIZATION_AMENDMENT_20260724.md"
)
PROJECTOR = ROOT / "tools/exact_torque_oracle.py"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
TEST = ROOT / "tests/test_exact_torque_oracle.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V126 optimization amendment")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        source.get("status")
        != "PREREGISTERED_WINNER_V126_EXACT_ORACLE_SCREEN_AND_V115_PRICE_AUDIT"
        or contract.get("status")
        != "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT"
        or contract.get("formal_behavior_cells_executed") != 0
    ):
        raise ValueError("V126 optimization amendment inputs changed")
    payload = dict(source)
    payload["schema_version"] = (
        "winner_v126.exact_oracle_optimization_amendment.v1"
    )
    payload["optimization_amendment"] = {
        "change": (
            "reuse the exact rollout force array that already corresponds to "
            "the final action; execute a final rollout only when the last "
            "coordinate operation changed that action"
        ),
        "semantic_change": False,
        "projection_constants_change": False,
        "action_change": False,
        "gate_change": False,
        "formal_behavior_cells_before_amendment": 0,
        "old_projector_sha256": contract["source_hashes"]["projector"],
        "new_projector_sha256": sha256(PROJECTOR),
        "evaluator_sha256": sha256(EVALUATOR),
        "unit_test_sha256": sha256(TEST),
        "required_revalidation": (
            "repeat the same four-run nonformal CPU contract before any formal "
            "screen cell"
        ),
    }
    payload["authority"] = {
        **payload["authority"],
        "cpu_contract_runs": 4,
        "formal_screen_cells_after_cpu_contract_pass": 16,
        "training": False,
        "hosted_or_colab": False,
        "rdkx5_or_robot": False,
        "gate5": False,
        "torque_or_motion": False,
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v126 oracle optimization amendment\n\n"
        f"Status: `{payload['status']}`\n\n"
        "One redundant exact rollout is removed only when the cached force "
        "array already corresponds to the unchanged final action. Projection "
        "constants, actions, gates, and authority are unchanged.\n\n"
        "The same four-run nonformal CPU contract must pass again before any "
        "formal behavior cell. No training, hosted compute, Gate 5, RDK-X5, "
        "robot, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output_sha256": sha256(OUTPUT),
                "projector_sha256": sha256(PROJECTOR),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
