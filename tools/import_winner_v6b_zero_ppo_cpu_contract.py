#!/usr/bin/env python3
"""Import one external winner-v6b zero-PPO result into repository evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6B_ZERO_PPO_CPU_CONTRACT_RESULT_20260720.md"


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
        raise FileExistsError("winner-v6b formal result has already been imported")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    preregistration_sha = sha256(PREREGISTRATION)
    if raw["preregistration_sha256"] != preregistration_sha:
        raise ValueError("raw result does not match the frozen v6b preregistration")
    if raw["status"] not in {
        "PASS_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT",
        "HOLD_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT",
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
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(
        "# Winner-v6b Zero-PPO CPU Software Contract Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"Imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- calibrator JAX/ONNX action/hidden error: "
        f"`{payload['calibration_chain']['max_action_error']}` / "
        f"`{payload['calibration_chain']['max_hidden_error']}`\n"
        f"- default-off identity pass: "
        f"`{payload['checks']['default_off_arbitrary_input_identity_bit_exact']}`\n"
        f"- enabled adapter bound-stress pass: "
        f"`{payload['checks']['enabled_adapter_arbitrary_input_bounds_hold']}`\n"
        f"- protected physical-chain pass: "
        f"`{payload['checks']['protected_physical_chains_hold_full_action_contract']}`\n"
        f"- invalid handoffs rejected: "
        f"`{len(payload['fail_closed']['rejected_cases'])}/"
        f"{len(payload['fail_closed']['invalid_cases'])}`\n\n"
        "This result contains no training or behavior outcome. A pass authorizes only "
        "design and review of a separate calibrator-training preregistration; it does "
        "not authorize PPO, Colab, GPU, runtime implementation, robot access, torque, "
        "motion, Gate 5, deployment, or robot clearance.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
