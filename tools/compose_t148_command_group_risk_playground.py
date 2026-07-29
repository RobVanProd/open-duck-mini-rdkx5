#!/usr/bin/env python3
"""Compose T148 from the frozen T128 exact-negative Playground."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = Path(
    "D:/CodexProjects/Open_Duck_Playground-t128-negative-only-expert-v1"
)
DEFAULT_OUTPUT = Path(
    "D:/CodexProjects/Open_Duck_Playground-t148-command-group-risk-v1"
)
LOSS_SOURCE = ROOT / "patches" / "t147_command_group_risk_ppo_losses.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"T148 {label} replacement count changed: {count}")
    return text.replace(old, new)


def patch_common_runner(text: str) -> str:
    old = """        with ExitStack() as stack:
            if getattr(
                self.args, "winner_t37_freeze_observation_normalizer", False
            ):
"""
    new = """        with ExitStack() as stack:
            if getattr(
                self.args, "winner_t147_command_group_risk", False
            ):
                from playground.common.t147_command_group_risk_ppo_losses import (
                    command_group_risk_loss,
                )

                stack.enter_context(command_group_risk_loss())
            if getattr(
                self.args, "winner_t37_freeze_observation_normalizer", False
            ):
"""
    return replace_exact(text, old, new, "loss context")


def patch_task_runner(text: str) -> str:
    old = """    parser.add_argument("--winner_t98_hidden_gate_asset_path", default=None)
    parser.add_argument("--winner_v127_constrained_cost", action="store_true")
"""
    new = """    parser.add_argument("--winner_t98_hidden_gate_asset_path", default=None)
    parser.add_argument(
        "--winner_t147_command_group_risk",
        action="store_true",
    )
    parser.add_argument("--winner_v127_constrained_cost", action="store_true")
"""
    return replace_exact(text, old, new, "CLI flag")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T148 Playground: {output}")
    for path in (BASE, LOSS_SOURCE):
        if not path.exists():
            raise FileNotFoundError(path)

    shutil.copytree(BASE, output)
    loss_path = (
        output
        / "playground/common/t147_command_group_risk_ppo_losses.py"
    )
    shutil.copy2(LOSS_SOURCE, loss_path)
    common_runner = output / "playground/common/runner.py"
    common_runner.write_text(
        patch_common_runner(common_runner.read_text(encoding="utf-8")),
        encoding="utf-8",
        newline="\n",
    )
    task_runner = output / "playground/open_duck_mini_v2/runner.py"
    task_runner.write_text(
        patch_task_runner(task_runner.read_text(encoding="utf-8")),
        encoding="utf-8",
        newline="\n",
    )
    compile_paths = [loss_path, common_runner, task_runner]
    subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, compile_paths)],
        cwd=output,
        check=True,
    )
    inventory = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted(output.rglob("*.py"))
    }
    value = {
        "schema_version": "open_duck.t148_composed_playground.v1",
        "base": str(BASE.resolve()),
        "output": str(output),
        "inputs": {
            "composer": sha256(Path(__file__)),
            "loss_source": sha256(LOSS_SOURCE),
        },
        "generated": {
            "loss": sha256(loss_path),
            "common_runner": sha256(common_runner),
            "task_runner": sha256(task_runner),
        },
        "python_inventory": inventory,
    }
    value["manifest_sha256"] = canonical_sha256(value)
    manifest = output / "T148_COMPOSED_SOURCE_MANIFEST.json"
    manifest.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest": str(manifest),
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
