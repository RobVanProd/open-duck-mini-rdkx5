#!/usr/bin/env python3
"""Compose a default-off recurrent warm-start evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
EXPECTED_SOURCE = (
    "9ac610245ea835f023c1e933ad1224bf0e4f1cd94ba84a224f29c9cde32fe21b"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"V136 expected one {name} marker, found {text.count(old)}"
        )
    return text.replace(old, new, 1)


def compose(text: str) -> str:
    text = replace_once(
        text,
        "    policy_state_output_names: tuple[str, ...] = ()\n",
        "    policy_state_output_names: tuple[str, ...] = ()\n"
        "    policy_initial_h_in: tuple[float, ...] | None = None\n",
        "config field",
    )
    marker = '''        hidden_state = {
            name: value.copy()
            for name, value in policy_io["hidden_state"].items()
        }
'''
    replacement = marker + '''        if config.policy_initial_h_in is not None:
            if "h_in" not in hidden_state:
                raise ValueError(
                    "V136 warm start requires a declared h_in state"
                )
            initial_h_in = np.asarray(
                config.policy_initial_h_in, dtype=np.float32
            )
            if initial_h_in.shape != (64,):
                raise ValueError(
                    f"V136 warm h_in shape {initial_h_in.shape} != (64,)"
                )
            if not np.all(np.isfinite(initial_h_in)):
                raise ValueError("V136 warm h_in contains nonfinite values")
            hidden_state["h_in"] = initial_h_in[None, :].copy()
'''
    return replace_once(
        text,
        marker,
        replacement,
        "hidden initialization",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(
            f"refusing to overwrite V136 evaluator: {output_root}"
        )
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE:
        raise ValueError("V136 evaluator source changed")
    output_root.mkdir(parents=True)
    output = output_root / "closed_loop_sim_eval_v136_warm_start.py"
    output.write_text(
        compose(SOURCE.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    compile(output.read_text(encoding="utf-8"), str(output), "exec")
    manifest = {
        "schema_version": "winner_v136.warm_start_evaluator_composition.v1",
        "status": "PASS_WINNER_V136_WARM_START_EVALUATOR_COMPOSITION",
        "input_hashes": {"source": source_hash},
        "output": {
            "path": str(output),
            "sha256": sha256(output),
            "bytes": output.stat().st_size,
        },
        "default_off": (
            "policy_initial_h_in=None preserves the frozen zero-state path"
        ),
        "warm_start": (
            "when provided, only h_in[1,64] initialization changes; "
            "previous_action remains exact zero"
        ),
        "authority": {
            "cpu_contract": False,
            "formal_behavior": False,
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
