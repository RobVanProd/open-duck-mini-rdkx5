#!/usr/bin/env python3
"""Launch unchanged V165 with the repository package root importable."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.run_winner_v165_coherent_normalizer import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
