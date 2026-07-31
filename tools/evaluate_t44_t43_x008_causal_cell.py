#!/usr/bin/env python3
"""Evaluate exactly T44's preregistered x=.080 causal cell."""

from __future__ import annotations

import evaluate_t27_t23_robustness_condition as worker


worker.FORMAL_COMMANDS = (0.08,)


if __name__ == "__main__":
    raise SystemExit(worker.main())
