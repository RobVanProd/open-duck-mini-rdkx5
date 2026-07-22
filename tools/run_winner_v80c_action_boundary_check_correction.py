#!/usr/bin/env python3
"""Run Winner-v80 with both frozen Winner-v80b/c corrections."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main() -> int:
    import build_winner_v80c_action_boundary_check_correction as builder

    source, _ = builder.corrected_source()
    namespace: dict[str, Any] = {
        "__file__": str(Path(__file__)),
        "__name__": "winner_v80c_pitch_action_head_step",
    }
    exec(compile(source, str(Path(__file__)), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
