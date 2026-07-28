#!/usr/bin/env python3
"""Run T92's frozen raw-T78 COM endpoint attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t92_raw_t78_com_attribution_preregistration.json"
RESULT = ANALYSIS / "t92_raw_t78_com_attribution_result.json"
MARKDOWN = ANALYSIS / "T92_RAW_T78_COM_ATTRIBUTION_RESULT_20260728.md"
DEFAULT_CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t92_raw_t78_com_attribution_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    matrix_plan,
    receipt,
    run_or_load_block,
)


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


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T92 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status") != "PREREGISTERED_T92_RAW_T78_COM_ATTRIBUTION"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T92 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for policy in value["policies"]:
        verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    plan = matrix_plan(
        [value["condition"]],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != int(value["matrix"]["cells"])
        or canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T92 matrix plan changed")
    return value


def classify(
    green_cells: int,
    rule: Mapping[str, Any],
) -> tuple[str, str]:
    if green_cells == 16:
        item = rule["full"]
    elif green_cells > 6:
        item = rule["partial"]
    else:
        item = rule["none"]
    return str(item["classification"]), str(item["decision"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T92 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T92 formal execution requires a clean worktree")

    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    blocks: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg,
                prereg["condition"],
                policy,
                fit,
                cache_root,
            )
            block_result = extract_block(
                prereg, prereg["condition"], manifest
            )
            block_green_cells = sum(
                int(cell["cell_green"]) for cell in block_result["cells"]
            )
            block = {
                "condition_index": prereg["condition"]["condition_index"],
                "condition_id": prereg["condition"]["id"],
                "checkpoint_id": policy["checkpoint_id"],
                "step": policy["step"],
                "fit_id": fit["fit_id"],
                "cached": cached,
                "manifest": receipt(
                    Path(manifest["evaluation"]["path"]).parent
                    / "manifest.json"
                ),
                "result": block_result,
            }
            blocks.append(block)
            cache_hits += int(cached)
            new_blocks += int(not cached)
            print(
                json.dumps(
                    {
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
                        ),
                        "block_green": block_result["block_green"],
                        "green_cells": block_green_cells,
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )

    summary = condition_summary(prereg["condition"], blocks)
    green_cells = int(summary["green_cells"])
    classification, decision = classify(
        green_cells, prereg["classification_rule"]
    )
    per_checkpoint = []
    for policy in prereg["policies"]:
        selected = [
            block
            for block in blocks
            if block["checkpoint_id"] == policy["checkpoint_id"]
        ]
        per_checkpoint.append(
            {
                "checkpoint_id": policy["checkpoint_id"],
                "step": policy["step"],
                "green_cells": sum(
                    int(cell["cell_green"])
                    for block in selected
                    for cell in block["result"]["cells"]
                ),
                "cells": 8,
            }
        )

    result: dict[str, Any] = {
        "schema_version": "open_duck.t92_raw_t78_com_attribution_result.v1",
        "status": "PASS_T92_RAW_T78_COM_ATTRIBUTION",
        "classification": classification,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "condition": summary,
        "blocks": blocks,
        "per_checkpoint": per_checkpoint,
        "comparison": {
            "raw_t78_green_cells": green_cells,
            "t84_rolling_green_cells": prereg["baselines"][
                "t84_rolling_endpoint_green_cells"
            ],
            "t67_core_green_cells": prereg["baselines"][
                "t67_core_endpoint_green_cells"
            ],
            "gain_over_t84_rolling": green_cells
            - prereg["baselines"]["t84_rolling_endpoint_green_cells"],
            "gain_over_t67_core": green_cells
            - prereg["baselines"]["t67_core_endpoint_green_cells"],
        },
        "summary": {
            "completed_cells": summary["cells"],
            "green_cells": green_cells,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
        },
        "interpretation": {
            "raw_endpoint_fully_learned": green_cells == 16,
            "raw_endpoint_gain_over_core": green_cells > 6,
            "rolling_transform_destroyed_full_endpoint": (
                green_cells == 16
            ),
            "hosted_run_earned": False,
        },
        "cache_root": str(cache_root),
        "authority": {
            "successor_cpu_preregistration": True,
            "additional_training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T92 raw-T78 COM attribution result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{classification}`",
                f"- Decision: `{decision}`",
                f"- Raw T78 green: `{green_cells}/16`",
                "- T67 core baseline: `6/16`",
                "- T84 rolling pair: `4/16`",
                (
                    "- Per checkpoint: "
                    + ", ".join(
                        f"`{item['checkpoint_id']} "
                        f"{item['green_cells']}/8`"
                        for item in per_checkpoint
                    )
                ),
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"classification={classification}")
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
