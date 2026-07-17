#!/usr/bin/env python3
"""Verify the cross-fit-selected P30 observer is pinned in native runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime"))

from winner_v2 import FittedBridgeObserver, HOME_TARGET_RAD, P30_FIT_HASH  # noqa: E402


P30 = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
P31 = ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
CROSS_FIT = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_result.json"
RUNTIME = ROOT / "runtime/scripts/v2_rl_walk_mujoco.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rejected(callable_) -> bool:
    try:
        callable_()
    except ValueError:
        return True
    return False


def main() -> int:
    result = json.loads(CROSS_FIT.read_text())
    runtime_source = RUNTIME.read_text()
    p30 = FittedBridgeObserver(P30, HOME_TARGET_RAD)
    checks = {
        "cross_fit_result_passed": result["status"]
        == "PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET"
        and result["p30_observer_pass"] is True,
        "p30_hash_constant_exact": P30_FIT_HASH == sha256(P30),
        "p30_observer_constructs": bool(
            p30.value.shape == (14,)
            and np.max(np.abs(p30.value - HOME_TARGET_RAD)) == 0.0
        ),
        "p31_34_rejected_by_runtime_observer": rejected(
            lambda: FittedBridgeObserver(P31, HOME_TARGET_RAD)
        ),
        "runtime_rejects_gain_overrides_before_hwi": (
            'if kp_overrides:' in runtime_source
            and 'winner-v2 P30 observer contract forbids gain overrides' in runtime_source
            and runtime_source.index('if kp_overrides:')
            < runtime_source.index('self.hwi = HWI')
        ),
        "fit_path_remains_explicit": '--winner-v2-fit-path' in runtime_source
        and 'default=None' in runtime_source,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V2_P30_OBSERVER_PIN"
        if not failed
        else "HOLD_WINNER_V2_P30_OBSERVER_PIN"
    )
    payload = {
        "schema_version": "winner_v2_p30_observer_pin.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "hashes": {
            "p30_fit": sha256(P30),
            "p31_34_fit_rejected": sha256(P31),
            "cross_fit_result": sha256(CROSS_FIT),
            "winner_v2_module": sha256(
                ROOT / "runtime/mini_bdx_runtime/mini_bdx_runtime/winner_v2.py"
            ),
            "runtime_script": sha256(RUNTIME),
        },
        "authority": {
            "offline_v2_configuration_pinned": not failed,
            "gate5_deployment_robot_rdk": False,
        },
    }
    out_json = ROOT / "outputs/analysis/winner_v2_p30_observer_pin.json"
    out_md = ROOT / "outputs/analysis/WINNER_V2_P30_OBSERVER_PIN_20260717.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(
        "# Winner-v2 P30 Observer Pin\n\n"
        f"Status: `{status}`\n\n"
        f"- P30 fit SHA-256: `{sha256(P30)}`\n"
        f"- P31/34 fit rejected by deployment observer: `{checks['p31_34_rejected_by_runtime_observer']}`\n"
        f"- Gain overrides rejected before HWI construction: `{checks['runtime_rejects_gain_overrides_before_hwi']}`\n"
        f"- Failed checks: `{failed}`\n\n"
        "The explicit path remains required, but only the measured P30 artifact is accepted. "
        "This is an offline configuration pin, not Gate 5 or robot clearance.\n"
    )
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
