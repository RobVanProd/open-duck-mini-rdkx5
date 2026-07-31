#!/usr/bin/env python3
"""Import the external winner-v7 graph-contract result without policy binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v7_inward_projection_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v7_inward_projection_contract_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_INWARD_PROJECTION_CONTRACT_RESULT_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    args = parser.parse_args()
    raw_path = args.raw_result.resolve()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v7 graph result has already been imported")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    preregistration_sha = sha256(PREREGISTRATION)
    if raw["preregistration_sha256"] != preregistration_sha:
        raise ValueError("raw result does not match the frozen winner-v7 preregistration")
    if raw["status"] not in {
        "PASS_WINNER_V7_INWARD_PROJECTION_TRANSFORM_CONTRACT",
        "HOLD_WINNER_V7_INWARD_PROJECTION_TRANSFORM_CONTRACT",
    }:
        raise ValueError(f"unexpected raw result status: {raw['status']}")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_sha256": preregistration_sha,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "policy_binaries_committed": False,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(
        "# Winner-v7 Inward-Projection Transform Contract Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"Imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- fixed margin: `{payload['margin']['normalized_action']}` normalized action\n"
        f"- arbitrary stress gate: "
        f"`{payload['checks']['all_8192_arbitrary_stress_cases_strictly_bounded']}`\n"
        f"- x=0 exact gate: "
        f"`{payload['checks']['both_256_tick_x0_chains_exact_zero']}`\n"
        f"- moving-chain gate: "
        f"`{payload['checks']['both_32_tick_moving_chains_strictly_bounded']}`\n\n"
        "No transformed ONNX binary is committed by this import. A pass authorizes "
        "only a separate full-behavior revalidation preregistration. No behavior run, "
        "calibrator, training, Colab, GPU, runtime, or robot action is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
