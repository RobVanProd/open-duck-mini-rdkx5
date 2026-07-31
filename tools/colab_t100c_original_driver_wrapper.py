#!/usr/bin/env python3
"""Invoke frozen T100 with only its recursive command dispatch corrected."""

from __future__ import annotations

from pathlib import Path

import colab_t100_hidden_expert_continuation as frozen_t100


_BASE_RUNNER_COMMAND = frozen_t100.base.runner_command


def corrected_runner_command(
    playground: Path,
    output: Path,
    source: Path,
    reference: Path,
) -> list[str]:
    """Construct T100's exact command without recursive self-dispatch."""
    command = _BASE_RUNNER_COMMAND(playground, output, source, reference)
    old = "--winner_t77_endpoint_joint_adapter_continuation"
    command[command.index(old)] = "--winner_t98_hidden_expert_continuation"
    index = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[index:index] = [
        "--winner_t98_hidden_gate_asset_path",
        str(source.parent / frozen_t100.GATE_NAME),
    ]
    return command


def main() -> int:
    frozen_t100.runner_command = corrected_runner_command
    return frozen_t100.main()


if __name__ == "__main__":
    raise SystemExit(main())
