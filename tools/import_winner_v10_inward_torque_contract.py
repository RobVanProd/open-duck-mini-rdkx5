#!/usr/bin/env python3
"""Import the external winner-v10 contract result without ONNX/XML binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v10_inward_torque_contract_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v10_inward_torque_contract_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V10_INWARD_TORQUE_CONTRACT_RESULT_20260720.md"


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
        raise FileExistsError("winner-v10 result already imported")
    raw_path = args.raw_result.resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw["preregistration_sha256"] != sha256(PREREG):
        raise ValueError("raw result does not bind winner-v10 preregistration")
    if raw["status"] not in {
        "PASS_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT",
        "HOLD_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT",
    }:
        raise ValueError("unexpected winner-v10 status")
    for row in raw["policies"]:
        if sha256(Path(row["output_path"])) != row["output_sha256"]:
            raise ValueError("winner-v10 policy output identity mismatch")
    if sha256(Path(raw["xml"]["output_model_path"])) != raw["xml"][
        "output_model_sha256"
    ]:
        raise ValueError("winner-v10 XML output identity mismatch")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "onnx_xml_binaries_committed": False,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(
        "# Winner-v10 Inward-Torque Representation Contract Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- output XML SHA-256: `{payload['xml']['output_model_sha256']}`\n"
        f"- imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n"
        f"- raw result SHA-256: `{sha256(raw_path)}`\n\n"
        "No behavior, training, deployment, runtime, robot access, torque, motion, "
        "Gate 5, or robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
