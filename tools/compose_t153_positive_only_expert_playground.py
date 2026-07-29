#!/usr/bin/env python3
"""Compose T153 from the frozen T112 always-on-expert Playground."""

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
BASE = Path("D:/CodexProjects/Open_Duck_Playground-t112-always-on-expert-v1")
DEFAULT_OUTPUT = Path(
    "D:/CodexProjects/Open_Duck_Playground-t153-positive-only-expert-v1"
)
SOURCE_RUNNER = ROOT / "patches" / "t112_open_duck_mini_v2_runner.py"
MECHANISM = ROOT / "patches" / "t153_positive_only_hidden_expert.py"


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
        raise RuntimeError(f"T153 {label} replacement count changed: {count}")
    return text.replace(old, new)


def build_runner_source() -> str:
    text = SOURCE_RUNNER.read_text(encoding="utf-8")
    old = """                from playground.common.t66_endpoint_core_continuation import (
                    make_endpoint_bank_randomizer,
                )

                self.randomizer = make_endpoint_bank_randomizer(
                    self.randomizer,
                    torso_body_id=torso_body_id,
                )
                if args.winner_t98_hidden_expert_continuation:
                    print(
                        "T98_HIDDEN_EXPERT_CONTINUATION="
                        "strata=8,broad=1,isolated=7,"
                        "gate=always_on,"
                        "actor_updates=negative_adapter_location_only"
                    )
                elif args.winner_t77_endpoint_joint_adapter_continuation:
"""
    new = """                if args.winner_t98_hidden_expert_continuation:
                    from playground.common.t98_hidden_expert_continuation import (
                        make_positive_only_randomizer,
                    )

                    self.randomizer = make_positive_only_randomizer(
                        self.randomizer,
                        torso_body_id=torso_body_id,
                    )
                    print(
                        "T98_HIDDEN_EXPERT_CONTINUATION="
                        "strata=1,exact=torso_com_x_pos,offset_m=+0.05,"
                        "gate=always_on,"
                        "actor_updates=isolated_positive_expert_slot_only"
                    )
                else:
                    from playground.common.t66_endpoint_core_continuation import (
                        make_endpoint_bank_randomizer,
                    )

                    self.randomizer = make_endpoint_bank_randomizer(
                        self.randomizer,
                        torso_body_id=torso_body_id,
                    )
                if args.winner_t77_endpoint_joint_adapter_continuation:
"""
    return replace_exact(text, old, new, "positive-only randomizer")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T153 Playground: {output}")
    for path in (BASE, SOURCE_RUNNER, MECHANISM):
        if not path.exists():
            raise FileNotFoundError(path)

    shutil.copytree(BASE, output)
    mechanism_path = (
        output / "playground/common/t98_hidden_expert_continuation.py"
    )
    shutil.copy2(MECHANISM, mechanism_path)
    runner_path = output / "playground/open_duck_mini_v2/runner.py"
    runner_path.write_text(
        build_runner_source(), encoding="utf-8", newline="\n"
    )
    compile_paths = [
        mechanism_path,
        runner_path,
        output / "playground/common/runner.py",
        output / "playground/common/t98_hidden_expert_ppo_networks.py",
    ]
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
        "schema_version": "open_duck.t153_composed_playground.v1",
        "base": str(BASE.resolve()),
        "output": str(output),
        "inputs": {
            "composer": sha256(Path(__file__)),
            "source_runner": sha256(SOURCE_RUNNER),
            "mechanism": sha256(MECHANISM),
        },
        "generated": {
            "runner": sha256(runner_path),
            "mechanism": sha256(mechanism_path),
        },
        "python_inventory": inventory,
    }
    value["manifest_sha256"] = canonical_sha256(value)
    manifest = output / "T153_COMPOSED_SOURCE_MANIFEST.json"
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
