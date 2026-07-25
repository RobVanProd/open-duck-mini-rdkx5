#!/usr/bin/env python3
"""Compose a default-off continuous reference-feature playground."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(
        item
        for item in path.rglob("*")
        if item.is_file() and "__pycache__" not in item.parts
    ):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            "V166 reference-action lookup marker count changed: "
            f"{text.count(old)}"
        )
    return text.replace(old, new, 1)


def compose_joystick(text: str) -> str:
    old = (
        "            reference_action = self._reference_feature_actions[\n"
        '                command_index, info["imitation_i"]\n'
        "            ]\n"
    )
    new = (
        '            reference_phase = info["imitation_i"]\n'
        "            reference_phase_floor = jp.floor(reference_phase)\n"
        "            reference_phase_index = reference_phase_floor.astype(\n"
        "                jp.int32\n"
        "            ) % self._reference_feature_actions.shape[1]\n"
        "            reference_phase_next = (\n"
        "                reference_phase_index + 1\n"
        "            ) % self._reference_feature_actions.shape[1]\n"
        "            reference_phase_fraction = (\n"
        "                reference_phase - reference_phase_floor\n"
        "            )\n"
        "            reference_action_lower = self._reference_feature_actions[\n"
        "                command_index, reference_phase_index\n"
        "            ]\n"
        "            reference_action_upper = self._reference_feature_actions[\n"
        "                command_index, reference_phase_next\n"
        "            ]\n"
        "            reference_action = jp.where(\n"
        "                reference_phase_fraction == 0,\n"
        "                reference_action_lower,\n"
        "                reference_action_lower\n"
        "                + reference_phase_fraction\n"
        "                * (reference_action_upper - reference_action_lower),\n"
        "            )\n"
    )
    return replace_once(text, old, new)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    source_joystick = (
        source_root / "playground/open_duck_mini_v2/joystick.py"
    )
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite V166: {output_root}")
    source_tree_hash = directory_sha256(source_root)
    source_joystick_hash = sha256(source_joystick)
    shutil.copytree(
        source_root,
        output_root,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    output_joystick = (
        output_root / "playground/open_duck_mini_v2/joystick.py"
    )
    output_joystick.write_text(
        compose_joystick(source_joystick.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    compile(
        output_joystick.read_text(encoding="utf-8"),
        str(output_joystick),
        "exec",
    )
    manifest = {
        "schema_version": (
            "winner_v166.continuous_reference_playground_composition.v1"
        ),
        "status": "PASS_WINNER_V166_CONTINUOUS_REFERENCE_COMPOSITION",
        "input_hashes": {
            "composer": sha256(Path(__file__).resolve()),
            "source_tree": source_tree_hash,
            "source_joystick": source_joystick_hash,
        },
        "source": {
            "root": str(source_root),
            "tree_sha256": source_tree_hash,
            "joystick": str(source_joystick),
            "joystick_sha256": source_joystick_hash,
        },
        "output": {
            "root": str(output_root),
            "tree_sha256": directory_sha256(output_root),
            "joystick": str(output_joystick),
            "joystick_sha256": sha256(output_joystick),
        },
        "change": {
            "scope": "reference_feature_actions phase lookup only",
            "fractional": (
                "linear interpolation between adjacent cyclic phase rows"
            ),
            "integer": "explicit where fast path returns the original row",
            "policy_graph": False,
            "runtime_production": False,
            "training": False,
        },
    }
    manifest_path = output_root / "V166_COMPOSITION_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(manifest["status"])
    print(f"joystick_sha256={manifest['output']['joystick_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
