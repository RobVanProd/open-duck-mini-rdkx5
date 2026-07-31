#!/usr/bin/env python3
"""Preregister the exact JIT-oracle recovery of T185's CPU contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T185 = ANALYSIS / "t185_in_episode_single_support_cpu_preregistration.json"
RECOVERY = ANALYSIS / "t185_jit_phase_diagnostic_recovery_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t185b_jit_phase_diagnostic_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185B_JIT_PHASE_DIAGNOSTIC_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
ENV_WORKER = ROOT / "tools" / "run_t185_environment_contract_worker.py"
RUNNER = ROOT / "tools" / "run_t185_in_episode_single_support_cpu_contract.py"


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root is not an object: {path}")
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T185B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185B preregistration requires clean worktree")

    t185 = load(T185)
    recovery = load(RECOVERY)
    if (
        canonical_without(t185, "preregistered_contract_sha256")
        != t185["preregistered_contract_sha256"]
        or canonical_without(recovery, "result_sha256")
        != recovery["result_sha256"]
    ):
        raise RuntimeError("T185 or recovery canonical identity changed")
    if (
        t185["status"]
        != "PREREGISTERED_T185_IN_EPISODE_SINGLE_SUPPORT_CPU_CONTRACT"
        or recovery["status"]
        != "INVALIDATE_T185_PHASE_VECTOR_DIAGNOSTIC_BEFORE_OPTIMIZER"
        or recovery["evidence"][
            "source_preregistered_contract_sha256"
        ]
        != t185["preregistered_contract_sha256"]
        or recovery["execution"]["optimizer_steps"] != 0
        or recovery["execution"]["formal_behavior_cells"] != 0
        or recovery["execution"]["hosted_compute_units"] != 0
        or recovery["execution"]["robot_or_rdk_access"] != 0
    ):
        raise RuntimeError("T185 recovery authority or provenance changed")

    basis = {
        key: value
        for key, value in t185.items()
        if key
        not in (
            "schema_version",
            "status",
            "sources",
            "checks",
            "failed_checks",
            "preregistered_contract_sha256",
        )
    }
    basis["schema_version"] = (
        "open_duck.t185b_jit_phase_diagnostic_recovery_"
        "preregistration.v1"
    )
    basis["status"] = (
        "PREREGISTERED_T185B_JIT_PHASE_DIAGNOSTIC_RECOVERY"
    )
    basis["sources"] = {
        **{
            key: value
            for key, value in t185["sources"].items()
            if key
            not in (
                "builder",
                "environment_worker",
                "runner",
            )
        },
        "builder": receipt(BUILDER),
        "environment_worker": receipt(ENV_WORKER),
        "runner": receipt(RUNNER),
        "t185_preregistration": receipt(T185),
        "t185_jit_phase_diagnostic_recovery": receipt(RECOVERY),
    }
    basis["checks"] = {
        **t185["checks"],
        "t185_preoptimizer_stop_recorded": (
            recovery["execution"]["optimizer_steps"] == 0
            and not recovery["execution"]["result_artifact_written"]
        ),
        "diagnostic_oracle_only_change": (
            not recovery["correction"]["mechanism_change"]
            and not recovery["correction"]["scientific_contract_change"]
            and recovery["correction"]["comparison_tolerance"] == 0.0
        ),
        "policy_and_cpu_contract_unchanged": (
            basis["mechanism"] == t185["mechanism"]
            and basis["cpu_contract"] == t185["cpu_contract"]
            and basis["decision_rule"] == t185["decision_rule"]
            and basis["authority"] == t185["authority"]
        ),
    }
    basis["failed_checks"] = sorted(
        name for name, passed in basis["checks"].items() if not passed
    )
    basis["recovery_contract"] = {
        "only_scientific_checker_change": (
            "expected phase vectors are generated with the same "
            "jax.jit(jax.vmap(phase_vector)) execution as the environment"
        ),
        "comparison_tolerance": 0.0,
        "phase_indices_unchanged": {"left": 2, "right": 15},
        "prefix_ticks_unchanged": 27,
        "mechanism_unchanged": basis["mechanism"] == t185["mechanism"],
        "playground_unchanged": basis["playground"] == t185["playground"],
        "cpu_contract_unchanged": (
            basis["cpu_contract"] == t185["cpu_contract"]
        ),
        "decision_rule_unchanged": (
            basis["decision_rule"] == t185["decision_rule"]
        ),
        "authority_unchanged": basis["authority"] == t185["authority"],
        "execution_plumbing": (
            "runner accepts distinct preregistration, result, markdown, "
            "and work-root paths so T185B cannot overwrite T185 evidence"
        ),
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T185B JIT phase diagnostic recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Only checker change: expected phase uses the environment's "
        "JIT/vmap execution path\n"
        "- Exact comparison retained: `tolerance = 0`\n"
        "- Mechanism, CPU contract, decision rule, and authority: unchanged\n"
        "- Optimizer / behavior / hosted / robot now: `0/0/0/0`\n"
        f"- Failed preregistration checks: `{basis['failed_checks']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={basis['failed_checks']}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not basis["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
