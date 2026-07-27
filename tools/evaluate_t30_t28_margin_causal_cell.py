#!/usr/bin/env python3
"""Evaluate exactly the preregistered T30 x=.077 causal cell."""

from __future__ import annotations

import evaluate_t27_t23_robustness_condition as worker


worker.FORMAL_COMMANDS = (0.077,)


if __name__ == "__main__":
    raise SystemExit(worker.main())
