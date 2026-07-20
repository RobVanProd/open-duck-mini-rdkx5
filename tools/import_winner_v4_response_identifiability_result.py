from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT_JSON = ANALYSIS / "winner_v4_response_identifiability_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V4_RESPONSE_IDENTIFIABILITY_RESULT_20260720.md"
EXPECTED_SOURCE_SHA256 = "b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730"
EXPECTED_CONTRACT_SHA256 = "948e1323a2c0b0a2078602f3151b745d174f6355ab0cd4ff3eb3b65c55be7a7c"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render(result: dict[str, object]) -> str:
    signed = result["signed_endpoint_checks"]
    runs = result["runs"]
    settle_by_offset: dict[float, int] = {}
    excitation_by_offset: dict[float, int] = {}
    for row in runs:
        offset = float(row["torso_x_offset_m"])
        settle_by_offset[offset] = max(
            settle_by_offset.get(offset, 0),
            int(row["simulation"]["settle_contact_failure_ticks"]),
        )
        excitation_by_offset[offset] = max(
            excitation_by_offset.get(offset, 0),
            int(row["simulation"]["excitation_contact_failure_ticks"]),
        )
    lines = [
        "# Winner-v4 Response Identifiability Result — 2026-07-20",
        "",
        f"status: `{result['status']}`",
        "",
        f"decision: `{result['decision']}`",
        "",
        f"result JSON SHA-256: `{EXPECTED_SOURCE_SHA256}`",
        "",
        "## Result",
        "",
        "The response73 values are not the blocker in this run: both measured actuator-fit",
        "pairs distinguish torso X = -0.05 m from +0.05 m after physical sensor quantization,",
        "and all four endpoint/fit repeats are bit-exact. The differing field counts are",
        f"`{signed['p30_all_joint']['different_field_count']}/73` for P30 and",
        f"`{signed['p31_34_pitch_with_p30_nonpitch']['different_field_count']}/73` for P31/34.",
        "",
        "The run still fails its preregistered support boundary. Double-foot contact was absent",
        f"for `{settle_by_offset[-0.05]}` settle ticks at -0.05 m and",
        f"`{settle_by_offset[0.05]}` settle ticks at +0.05 m. The recorded 2,814-tick",
        "excitation populations later had zero double-contact failures, but the contract required",
        "the complete settle plus excitation population, so that later recovery cannot convert",
        "this run into a pass.",
        "",
        "## Decision",
        "",
        "Do not implement or train response73 from this evidence. The exact support procedure",
        "must be redesigned and reviewed prospectively; the completed run is not retried or",
        "reclassified. No policy, runtime, robot, or hardware action is authorized.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = args.source.read_bytes()
    actual = sha256_bytes(payload)
    if actual != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"result hash mismatch: expected {EXPECTED_SOURCE_SHA256}, got {actual}")
    result = json.loads(payload)
    if result["status"] != "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED":
        raise ValueError("source is not the frozen negative response73 result")
    if result["contract"]["sha256"] != EXPECTED_CONTRACT_SHA256:
        raise ValueError("result references the wrong pretraining contract")
    if args.output_json.exists() or args.output_md.exists():
        raise FileExistsError("refusing to replace an imported response73 result")
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(payload)
    args.output_md.write_text(render(result), encoding="utf-8")
    print(f"status={result['status']} sha256={actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
