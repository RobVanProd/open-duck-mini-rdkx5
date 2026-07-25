#!/usr/bin/env python3
"""Compose a default-off fractional-cadence CPU evaluator for V159."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"V159 expected one {name} marker, found {text.count(old)}"
        )
    return text.replace(old, new, 1)


def compose(text: str) -> str:
    text = replace_once(
        text,
        "    policy_phase_advance_before_observation: bool = False\n",
        "    policy_phase_advance_before_observation: bool = False\n"
        "    phase_frequency_factor: float = 1.0\n",
        "cadence config",
    )
    text = replace_once(
        text,
        '            state.info["imitation_i"] += 1\n',
        '            state.info["imitation_i"] += config.phase_frequency_factor\n',
        "reference increment",
    )
    marker = (
        '        "policy_phase_advance_before_observation": bool(\n'
        "            config.policy_phase_advance_before_observation\n"
        "        ),\n"
    )
    if text.count(marker) != 2:
        raise ValueError(
            "V159 expected two result cadence provenance markers, found "
            f"{text.count(marker)}"
        )
    text = text.replace(
        marker,
        marker
        + '        "phase_frequency_factor": float(\n'
        + "            config.phase_frequency_factor\n"
        + "        ),\n",
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-evaluator-root", type=Path, required=True
    )
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_evaluator_root.resolve()
    source_manifest_path = source_root / "composition_manifest.json"
    source_manifest = json.loads(
        source_manifest_path.read_text(encoding="utf-8")
    )
    source = Path(source_manifest["output"]["path"])
    if sha256(source) != source_manifest["output"]["sha256"]:
        raise ValueError("V159 source evaluator hash changed")
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(
            f"refusing to overwrite V159 evaluator: {output_root}"
        )
    output_root.mkdir(parents=True)
    output = output_root / "closed_loop_sim_eval_v159_cadence.py"
    output.write_text(
        compose(source.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    compile(output.read_text(encoding="utf-8"), str(output), "exec")
    manifest = {
        "schema_version": "winner_v159.cadence_evaluator_composition.v1",
        "status": "PASS_WINNER_V159_CADENCE_EVALUATOR_COMPOSITION",
        "input_hashes": {
            "composer": sha256(Path(__file__).resolve()),
            "source_manifest": sha256(source_manifest_path),
            "source": sha256(source),
        },
        "source": {
            "manifest_path": str(source_manifest_path),
            "path": str(source),
        },
        "output": {
            "path": str(output),
            "sha256": sha256(output),
            "bytes": output.stat().st_size,
        },
        "default_off": (
            "phase_frequency_factor=1.0 reproduces the source reference "
            "increment exactly"
        ),
        "scope": (
            "CPU evaluator only; no runtime, policy graph, training, "
            "deployment, Gate 5, or robot change"
        ),
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
