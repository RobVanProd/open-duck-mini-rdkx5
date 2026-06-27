#!/usr/bin/env python3
"""Blend two same-architecture ONNX policy exports by initializer value.

This is offline analysis tooling. It does not train, SSH, deploy, or touch robot
runtime behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_alphas(text: str) -> list[float]:
    values = []
    for part in text.split(","):
        part = part.strip()
        if part:
            values.append(float(part))
    if not values:
        raise ValueError("no alphas provided")
    for value in values:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"alpha must be within [0, 1], got {value}")
    return values


def initializer_arrays(model: onnx.ModelProto) -> list[np.ndarray]:
    return [numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer]


def validate_compatible(base: onnx.ModelProto, target: onnx.ModelProto) -> None:
    if len(base.graph.initializer) != len(target.graph.initializer):
        raise ValueError(
            f"initializer count mismatch: {len(base.graph.initializer)} vs {len(target.graph.initializer)}"
        )
    for index, (left, right) in enumerate(
        zip(base.graph.initializer, target.graph.initializer, strict=True)
    ):
        if list(left.dims) != list(right.dims):
            raise ValueError(
                f"initializer shape mismatch at {index}: {left.name} {list(left.dims)} vs {right.name} {list(right.dims)}"
            )


def blend_models(
    base: onnx.ModelProto,
    target: onnx.ModelProto,
    alpha: float,
) -> onnx.ModelProto:
    out = onnx.ModelProto()
    out.CopyFrom(base)
    base_arrays = initializer_arrays(base)
    target_arrays = initializer_arrays(target)
    for index, initializer in enumerate(out.graph.initializer):
        blended = (1.0 - alpha) * base_arrays[index] + alpha * target_arrays[index]
        initializer.CopyFrom(numpy_helper.from_array(blended.astype(np.float32), initializer.name))
    return out


def main() -> int:
    args = parse_args()
    base_path = Path(args.base)
    target_path = Path(args.target)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_model = onnx.load(base_path)
    target_model = onnx.load(target_path)
    validate_compatible(base_model, target_model)

    alphas = parse_alphas(args.alphas)
    outputs: list[dict[str, Any]] = []
    for alpha in alphas:
        out_model = blend_models(base_model, target_model, alpha)
        alpha_label = f"{alpha:.4f}".replace(".", "p")
        out_path = output_dir / f"blend_alpha_{alpha_label}.onnx"
        onnx.save(out_model, out_path)
        outputs.append(
            {
                "alpha": float(alpha),
                "path": str(out_path),
                "sha256": sha256(out_path),
                "size_bytes": out_path.stat().st_size,
            }
        )

    manifest = {
        "status": "PASS_BLEND_ONNX_POLICIES",
        "base": {"path": str(base_path), "sha256": sha256(base_path)},
        "target": {"path": str(target_path), "sha256": sha256(target_path)},
        "outputs": outputs,
        "notes": [
            "alpha=0 is exactly the base policy; alpha=1 is exactly the target policy.",
            "Initializers were blended by order after shape compatibility checks because TensorFlow export prefixes differed.",
            "These ONNX files are offline evaluation artifacts, not robot candidates.",
        ],
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(manifest, indent=2) + "\n")
    print(manifest["status"])
    print(f"wrote {args.output_json}")
    for item in outputs:
        print(f"alpha={item['alpha']:.4f} {item['path']}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--alphas", default="0.1,0.25,0.5,0.75")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/blended_onnx_policy_manifest.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
