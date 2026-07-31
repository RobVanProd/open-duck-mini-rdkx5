#!/usr/bin/env python3
"""Execute the frozen Winner-v71b full-loss binding correction."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main() -> int:
    import build_winner_v71b_full_loss_binding_correction as builder

    source, _ = builder.corrected_source()
    namespace: dict[str, Any] = {
        "__file__": str(Path(__file__)),
        "__name__": "winner_v71b_fresh_moment_safeguarded_continuation",
    }
    exec(compile(source, str(Path(__file__)), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
