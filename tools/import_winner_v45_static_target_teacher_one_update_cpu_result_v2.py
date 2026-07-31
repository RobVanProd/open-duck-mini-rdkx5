#!/usr/bin/env python3
"""Import the V45 artifact with the preregistered reporting-only v2 fix."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V1_PATH = ROOT / "tools/import_winner_v45_static_target_teacher_one_update_cpu_result.py"
CORRECTION = ANALYSIS / "winner_v45_importer_v2_correction_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_RESULT_20260722.md"
EXPECTED_RUN_ID = 29907921832
EXPECTED_ARTIFACT_ID = 8524663581
EXPECTED_HEAD_SHA = "501e3b0f2295e2bf0d45252ed15300958d3883fc"
EXPECTED_ARTIFACT_NAME = "winner-v45-static-target-teacher-one-update-29907921832"
EXPECTED_ARTIFACT_DIGEST = "sha256:5ff180cdd05eb00b77c136b0ac2747896cf77043dafb980a5fd661ce665523aa"
HEX40 = re.compile(r"[0-9a-f]{40}")


def load_v1():
    spec = importlib.util.spec_from_file_location("winner_v45_import_v1_frozen", V1_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen Winner-v45 importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_correction(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v45.importer_v2_correction_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V45_IMPORTER_V2_REPORTING_FIX"
        or value.get("decision") != "AUTHORIZE_ONE_IMPORT_OF_SAME_IMMUTABLE_V45_ARTIFACT_ONLY"
        or value.get("artifact") != {
            "run_id": EXPECTED_RUN_ID,
            "run_attempt": 1,
            "run_head_sha": EXPECTED_HEAD_SHA,
            "artifact_id": EXPECTED_ARTIFACT_ID,
            "artifact_name": EXPECTED_ARTIFACT_NAME,
            "artifact_digest": EXPECTED_ARTIFACT_DIGEST,
            "artifact_zip_bytes": 247738,
        }
        or value.get("allowed_change")
        != "bind teacher_loss_before/after from the already validated raw result before Markdown rendering"
        or any(value.get("execution_now", {}).values())
    ):
        raise ValueError("Winner-v45 importer correction authority changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v45 importer correction sources absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v45 importer correction source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v45 importer correction manifest changed")


def validate_result(value: Mapping[str, Any], **kwargs: Any) -> None:
    v1 = load_v1()
    v1.validate_result(value, **kwargs)
    if "repository_attribution" in value:
        attribution = value["repository_attribution"]
        if (
            attribution.get("importer_correction_contract_lf_sha256") != lf_sha256(CORRECTION)
            or attribution.get("importer_correction_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v45 importer correction attribution changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--run-head-sha", required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--artifact-digest", required=True)
    args = parser.parse_args()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    validate_correction(correction)
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v45 result is already imported")
    v1 = load_v1()
    zip_sha = v1.sha256(args.artifact_zip)
    if (
        args.run_id != EXPECTED_RUN_ID
        or args.run_attempt != 1
        or args.run_head_sha != EXPECTED_HEAD_SHA
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id != EXPECTED_ARTIFACT_ID
        or args.artifact_name != EXPECTED_ARTIFACT_NAME
        or args.artifact_digest != EXPECTED_ARTIFACT_DIGEST
        or args.artifact_digest != f"sha256:{zip_sha}"
        or args.artifact_zip.stat().st_size != correction["artifact"]["artifact_zip_bytes"]
    ):
        raise ValueError("Winner-v45 corrected import artifact attribution changed")
    members = v1.read_artifact(args.artifact_zip)
    raw_bytes = members[v1.RAW_RESULT_NAME]
    receipt_bytes = members[v1.RAW_RECEIPT_NAME]
    raw_sha = v1.sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{v1.RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v45 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=v1.reject_nonfinite)
    v1.validate_result(
        raw, snapshot_bytes=members[v1.SNAPSHOT_MEMBER], graph_bytes=members[v1.GRAPH_MEMBER]
    )
    result = dict(raw)
    result["repository_attribution"] = {
        "repository": v1.EXPECTED_REPOSITORY,
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "github_run_head_sha": args.run_head_sha,
        "github_artifact_id": args.artifact_id,
        "github_artifact_name": args.artifact_name,
        "github_artifact_digest": args.artifact_digest,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": v1.sha256_bytes(receipt_bytes),
        "snapshot_member": v1.SNAPSHOT_MEMBER,
        "snapshot_sha256": v1.sha256_bytes(members[v1.SNAPSHOT_MEMBER]),
        "graph_member": v1.GRAPH_MEMBER,
        "graph_sha256": v1.sha256_bytes(members[v1.GRAPH_MEMBER]),
        "contract_lf_sha256": v1.lf_sha256(v1.PREREGISTRATION),
        "workflow_lf_sha256": v1.lf_sha256(v1.WORKFLOW),
        "runner_lf_sha256": v1.lf_sha256(v1.RUNNER),
        "importer_lf_sha256": v1.lf_sha256(V1_PATH),
        "importer_correction_contract_lf_sha256": lf_sha256(CORRECTION),
        "importer_correction_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(
        result, snapshot_bytes=members[v1.SNAPSHOT_MEMBER], graph_bytes=members[v1.GRAPH_MEMBER]
    )
    before = float(result["optimization"]["teacher_loss_before"])
    after = float(result["optimization"]["teacher_loss_after"])
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text("\n".join([
        "# Winner-v45 static-target teacher one-update CPU result", "",
        f"- Status: `{result['status']}`", f"- Decision: `{result['decision']}`",
        "- Optimizer count: `251 -> 252`", f"- Teacher loss: `{before} -> {after}`",
        f"- Snapshot SHA-256: `{result['snapshot']['sha256']}`",
        f"- ONNX SHA-256: `{result['graph']['sha256']}`",
        f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
        f"- Artifact ZIP SHA-256: `{zip_sha}`",
        "- Importer correction: `reporting-only v2; immutable artifact unchanged`",
        "- Formal support / continuation training / robot: `0 / 0 / 0`", "",
        "A pass authorizes only a separately preregistered bounded continuation.",
        "It does not authorize checkpoint selection, Gate 5, or robot access.", "",
    ]), encoding="utf-8")
    print(result["status"])
    print(f"SNAPSHOT_SHA256={result['snapshot']['sha256']}")
    print(f"ONNX_SHA256={result['graph']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

