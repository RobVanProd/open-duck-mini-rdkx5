#!/usr/bin/env python3
"""Execute the frozen Winner-v65 isolated persistent-teacher arm."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main() -> int:
    import build_winner_v65_isolated_persistent_teacher_training as builder

    source, _ = builder.transformed_source()
    namespace: dict[str, Any] = {
        "__file__": str(Path(__file__)),
        "__name__": "winner_v65_isolated_persistent_teacher_training",
    }
    exec(compile(source, str(Path(__file__)), "exec"), namespace)
    return namespace["main"]()


if __name__ == "__main__":
    raise SystemExit(main())
