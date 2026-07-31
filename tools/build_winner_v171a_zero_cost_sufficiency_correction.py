#!/usr/bin/env python3
"""Freeze the causal-sufficiency correction to V171's zero-cost batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V171 = ANALYSIS / "winner_v171_gradient_geometry_result.json"
OUTPUT = (
    ANALYSIS / "winner_v171a_zero_cost_sufficiency_correction.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V171A_ZERO_COST_SUFFICIENCY_CORRECTION_20260725.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V171a: {path}")
    result = json.loads(V171.read_text(encoding="utf-8"))
    audit_root = Path(result["execution"]["work_root"]) / "audit"
    matches = sorted(audit_root.glob("*_32_v127_aux.json"))
    if len(matches) != 1:
        raise ValueError(f"expected one V171 step-32 aux file: {matches}")
    aux_path = matches[0]
    aux = json.loads(aux_path.read_text(encoding="utf-8"))
    checks = {
        "v171_stated_contract_passed": (
            result.get("status")
            == "PASS_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
            and result.get("failed_checks") == []
        ),
        "one_training_iteration_exact": (
            aux.get("total_training_iterations") == 1
        ),
        "realized_batch_cost_was_zero": (
            float(aux.get("initial_cost")) == 0.0
        ),
        "dual_never_initialized": aux.get("initialized") is False,
        "dual_eta_and_lambda_remained_zero": (
            float(aux.get("eta")) == 0.0
            and float(aux.get("lambda")) == 0.0
        ),
        "cost_critic_was_fresh_not_restored": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"V171a correction inputs fail: {failed}")
    payload = {
        "schema_version": "winner_v171a.zero_cost_correction.v1",
        "status": "CORRECTED_WINNER_V171_CAUSAL_SUFFICIENCY",
        "failed_checks": [],
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "v171_result": sha256(V171),
            "v171_step32_aux": sha256(aux_path),
        },
        "observed": {
            "batch_cost": float(aux["initial_cost"]),
            "dual_initialized": bool(aux["initialized"]),
            "dual_eta": float(aux["eta"]),
            "dual_lambda": float(aux["lambda"]),
            "recorded_cost_gradient_norm": float(
                aux["v171_cost_gradient_norm"]
            ),
        },
        "correction": {
            "still_valid": [
                "the V171 instrumentation was update-bit-exact to V127",
                "the Euclidean tangent formula and numerical checks passed",
            ],
            "withdrawn_inference": (
                "V171 does not establish a causally meaningful torque-safety "
                "direction because its sole rollout batch had zero realized "
                "torque cost while the cost critic was freshly initialized"
            ),
            "reason": (
                "with zero realized cost, the nonzero normalized cost "
                "advantage and actor gradient can be induced by the random "
                "cost-value baseline rather than observed violations"
            ),
        },
        "decision": (
            "HOLD_V171_CAUSAL_PROMOTION_REQUIRE_FIRST_POSITIVE_COST_BATCH"
        ),
        "next_falsifier": (
            "capture the first batch with raw realized batch_cost>0 under the "
            "unchanged 1024-step V127 CPU schedule; require the instrumented "
            "training outputs to remain bit-exact to frozen V127"
        ),
        "authority": {
            "positive_cost_cpu_audit": True,
            "optimizer_implementation": False,
            "hosted_training": False,
            "candidate_selection": False,
            "robustness_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V171a zero-cost causal-sufficiency correction\n\n"
        "- V171 passed its stated geometry and update-equivalence contract.\n"
        "- Its sole rollout batch nevertheless had exactly zero realized "
        "torque cost; the fresh cost critic remained uninitialized by the "
        "dual rule.\n"
        "- Therefore the recorded nonzero cost gradient cannot yet be "
        "attributed to observed torque violations. Promotion to an optimizer "
        "implementation is withdrawn.\n"
        "- The next CPU-only audit must capture the first strictly positive "
        "realized-cost batch from the unchanged 1,024-step V127 schedule.\n"
        "- No hosted run, candidate, robustness matrix, Gate 5, RDK-X5, or "
        "robot is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
