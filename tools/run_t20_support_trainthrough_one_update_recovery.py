#!/usr/bin/env python3
"""Run T20's preregistered fresh rate-selector recovery."""

from __future__ import annotations

from pathlib import Path

import run_t20_support_trainthrough_one_update as t20


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"
t20.PREREGISTRATION = (
    ANALYSIS
    / "t20_support_trainthrough_one_update_recovery_preregistration.json"
)
t20.RESULT = (
    ANALYSIS / "t20_support_trainthrough_one_update_recovery_result.json"
)
t20.MARKDOWN = (
    ANALYSIS
    / "T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_RECOVERY_RESULT_20260726.md"
)


if __name__ == "__main__":
    raise SystemExit(t20.main())
