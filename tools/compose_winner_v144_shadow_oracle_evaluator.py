#!/usr/bin/env python3
"""Compose a two-fit oracle evaluator with a default-on apply switch.

The new switch permits a read-only shadow-oracle diagnostic: the exact
projected action is computed and logged, while the source policy action
continues through the real simulated trajectory unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import compose_winner_v131_two_fit_oracle_evaluator as v131


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
V131_COMPOSER = ROOT / "tools/compose_winner_v131_two_fit_oracle_evaluator.py"
HELPER = ROOT / "tools/exact_torque_oracle_two_fit.py"
EXPECTED = {
    "source": (
        "9ac610245ea835f023c1e933ad1224bf0e4f1cd94ba84a224f29c9cde32fe21b"
    ),
    "v131_composer": (
        "4e37d442b2234525d1d4e0a3d5a162b7f131b1f9b5245e3f2b46104f1f60e25c"
    ),
    "helper": (
        "c9894fa982d0837fbd6281dc778248365c9079e60680c928fd34a50c2e55eb27"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"V144 expected one {name} marker, found {text.count(old)}"
        )
    return text.replace(old, new, 1)


def compose(text: str) -> str:
    text = v131.compose(text)
    text = replace_once(
        text,
        "    exact_torque_oracle_maximum_fit_passes: int = 14\n",
        "    exact_torque_oracle_maximum_fit_passes: int = 14\n"
        "    exact_torque_oracle_apply: bool = True\n",
        "oracle apply config",
    )
    assignment = "                            action, exact_oracle_tick = (\n"
    if text.count(assignment) != 2:
        raise ValueError(
            "V144 expected exactly two two-fit oracle action assignments"
        )
    text = text.replace(
        assignment,
        "                            projected_action, exact_oracle_tick = (\n",
    )
    text = replace_once(
        text,
        '                    exact_oracle_totals["rollout_evaluations"] += int(\n',
        "                    if config.exact_torque_oracle_apply:\n"
        "                        action = projected_action\n"
        '                    exact_oracle_totals["rollout_evaluations"] += int(\n',
        "conditional oracle application",
    )
    text = replace_once(
        text,
        '        "exact_torque_oracle": {\n'
        '            "enabled": bool(config.exact_torque_oracle_enabled),\n',
        '        "exact_torque_oracle": {\n'
        '            "enabled": bool(config.exact_torque_oracle_enabled),\n'
        '            "apply": bool(config.exact_torque_oracle_apply),\n',
        "result apply provenance",
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(
            f"refusing to overwrite V144 evaluator: {output_root}"
        )
    input_hashes = {
        "source": sha256(SOURCE),
        "v131_composer": sha256(V131_COMPOSER),
        "helper": sha256(HELPER),
    }
    if input_hashes != EXPECTED:
        raise ValueError("V144 evaluator inputs changed")
    output_root.mkdir(parents=True)
    output = output_root / "closed_loop_sim_eval_v144_shadow_oracle.py"
    output.write_text(
        compose(SOURCE.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    compile(output.read_text(encoding="utf-8"), str(output), "exec")
    manifest = {
        "schema_version": "winner_v144.shadow_oracle_composition.v1",
        "status": "PASS_WINNER_V144_SHADOW_ORACLE_COMPOSITION",
        "input_hashes": input_hashes,
        "output": {
            "path": str(output),
            "sha256": sha256(output),
            "bytes": output.stat().st_size,
        },
        "default_on": (
            "exact_torque_oracle_apply=True preserves the V131 path"
        ),
        "shadow_mode": (
            "apply=False computes and logs the two-fit projection but "
            "commits the unmodified policy action"
        ),
        "authority": {
            "cpu_diagnostic": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    manifest_path = output_root / "composition_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(manifest["status"])
    print(f"output_sha256={manifest['output']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
