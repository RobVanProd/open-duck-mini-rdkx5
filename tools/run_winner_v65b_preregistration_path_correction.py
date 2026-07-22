#!/usr/bin/env python3
"""Execute the frozen Winner-v65b path correction."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main() -> int:
    import build_winner_v65b_preregistration_path_correction as builder

    source, _ = builder.corrected_source()
    namespace: dict[str, Any] = {
        "__file__": str(Path(__file__)),
        "__name__": "winner_v65b_isolated_persistent_teacher_training",
    }
    exec(compile(source, str(Path(__file__)), "exec"), namespace)
    return_code = namespace["main"]()
    output_index = sys.argv.index("--output") + 1
    output = Path(sys.argv[output_index])
    result = json.loads(output.read_text(encoding="utf-8"))
    contract = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
    result["schema_version"] = (
        "winner_v65b.isolated_persistent_teacher_training_result.v1"
    )
    result["status"] = result["status"].replace("WINNER_V65_", "WINNER_V65B_")
    result["v65b"] = contract["v65b"]
    result["sources"] = contract["sources"]
    result["source_manifest_sha256"] = contract["source_manifest_sha256"]
    output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
