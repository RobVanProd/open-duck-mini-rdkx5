#!/usr/bin/env python3
"""Import the external winner-v8 zero-behavior contract result without binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v8_physical_envelope_contract_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v8_physical_envelope_contract_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT_RESULT_20260720.md"


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
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v8 result already imported")
    raw = json.loads(args.raw_result.read_text(encoding="utf-8"))
    if raw["preregistration_sha256"] != sha256(PREREG):
        raise ValueError("raw result does not bind the frozen preregistration")
    if raw["status"] not in {"PASS_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT", "HOLD_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT"}:
        raise ValueError("unexpected winner-v8 result status")
    for policy in raw["policies"]:
        path = Path(policy["output_path"])
        if sha256(path) != policy["output_sha256"]:
            raise ValueError(f"transformed policy identity mismatch: {path}")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "raw_result_filename": args.raw_result.name,
        "raw_result_sha256": sha256(args.raw_result),
        "policy_binaries_committed": False,
        "xml_files_committed": False,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "# Winner-v8 Physical-Envelope Contract Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n"
        f"- raw result SHA-256: `{sha256(args.raw_result)}`\n\n"
        "This contract contains no behavior, training, deployment, runtime, robot access, torque, motion, Gate 5, or robot clearance. External ONNX/XML artifacts are hash-bound but not committed.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
