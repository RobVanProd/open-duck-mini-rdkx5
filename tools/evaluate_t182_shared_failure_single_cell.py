#!/usr/bin/env python3
"""Formal T182 worker: exact T27 logic with the one frozen command."""

from __future__ import annotations

from pathlib import Path
import sys


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import evaluate_t27_t23_robustness_condition as base  # noqa: E402


FORMAL_COMMANDS = (0.077,)


def main() -> int:
    base.FORMAL_COMMANDS = FORMAL_COMMANDS
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
