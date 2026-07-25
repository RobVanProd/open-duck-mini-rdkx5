#!/usr/bin/env python3
"""Preregister T3 v2 after excluding the provenance-invalid mock trace."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t3_observation_zscore_v2_preregistration.json"
MARKDOWN = ANALYSIS / "T3_OBSERVATION_ZSCORE_V2_PREREGISTRATION_20260725.md"
POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
GOLDEN = ANALYSIS / "legacy_runtime_golden_vector_20260621.json"
INVALIDATION = ANALYSIS / "T3_OBSERVATION_ZSCORE_V1_INVALIDATION_20260725.md"
GATE3_DIR = "open-duck-gate3-review-hrmv5w64"
CORRECTED_CONTRACT = (
    "open-duck-gate3-source-1792d9c/artifacts/contracts/"
    "legacy-contract-snapshot.json"
)
EXPECTED = {
    "policy": (
        "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067"
    ),
    "golden": (
        "91a95e798b83fccc79452ca3857cda7f08b98f495967de0384a9d570d067ff87"
    ),
    "corrected_contract": (
        "298753fb30c658321161df50f668ad7ab25121a1958c4b7bbdb1c543caf06bff"
    ),
    "v1_invalidation": (
        "cabd1c06674c73cad2a9f2df437988f35c3d7e50ab62f320efb562b9e3d78e08"
    ),
    "gate3_sensor": {
        "both_contacts": (
            "121b0cdea9903e3d5268bdba537e8119a1418af34c72794fa94cf1ebfbee6ff8"
        ),
        "left_contact": (
            "3215514fc67034d70e4508881aebbe3eb92e5aef08206dbc8e24b4fe4d49e15a"
        ),
        "left_tilt": (
            "f10051fddcc1d2fdeed9ad7a1dffc07f1a83d0787d2613ac79508f0f8549b1e1"
        ),
        "no_contacts": (
            "3e184171d1aca748af1051864e7ece88f911c2e06fe595db6cbe87d0ba4543f2"
        ),
        "nose_back": (
            "adf2ce54c17c80c51bd444b34919a376d243a63a998b59ea5658733c5549b498"
        ),
        "nose_forward": (
            "0a4b20e63668413c3c0387d4abef1993e089e60bcbc0668b20b4ba1083010ac3"
        ),
        "right_contact": (
            "3f8b1c6e97434ba1d3c6354946968bee46625bf81efabaa0808390b40cab5968"
        ),
        "right_tilt": (
            "e437b0d7d3bbce26fcd4de929435f2d5bfd528ad09a3d84a01a0e15aba663d95"
        ),
        "upright": (
            "77861e4321f240364aea5c6f5eef83be8d31f6de2b5a8d837fb2dc222c56cd81"
        ),
    },
    "gate3_summary": {
        "both_contacts": (
            "73d86db18c5b4688490ec0e81b6319460ef7ace1bd06007f11e1cdca12b487c5"
        ),
        "left_contact": (
            "da0cc5f12471df71925daf7a89f718c342d78859fd96a61e89d2d58cdce4018a"
        ),
        "left_tilt": (
            "e5b28d712b53812c29af9a69c2ae097e5a13c01dd53d342d3ddec12de72733a6"
        ),
        "no_contacts": (
            "45d7a919ab9d6ca1c8b8bf25fb707b1ac68c6163fe7fcadf622b371b311937f1"
        ),
        "nose_back": (
            "3921b9777a2aa53e1a49ccb79599b9b056d50d9ccc9c7c756168d942fdbc3f3d"
        ),
        "nose_forward": (
            "f25061de044dee1f63bd53aeba55a275a99119923128643f2c421f4ebe6dfd49"
        ),
        "right_contact": (
            "f717f05ade277a70fe9695099bc5b49e6de7439b617296b6783929b4981ba335"
        ),
        "right_tilt": (
            "3f696f9ee411e7767ccae734de38b5651f20958d829cd36fbfdb31dcbb5856a0"
        ),
        "upright": (
            "de9e4df38504e422146db6dfc276dafa51cf213fd04f50d0d37e639adc6174b3"
        ),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--real-data-root",
        type=Path,
        default=Path(r"D:\open-duck-archive-20260725\real-robot-data"),
    )
    args = parser.parse_args()
    real_root = args.real_data_root.resolve()
    labels = sorted(EXPECTED["gate3_sensor"])
    paths = {
        "policy": POLICY,
        "golden": GOLDEN,
        "corrected_contract": real_root / CORRECTED_CONTRACT,
        "v1_invalidation": INVALIDATION,
    }
    for label in labels:
        paths[f"gate3_sensor_{label}"] = (
            real_root / GATE3_DIR / label / "sensor.jsonl"
        )
        paths[f"gate3_summary_{label}"] = (
            real_root / GATE3_DIR / label / "summary.json"
        )
    missing = sorted(name for name, path in paths.items() if not path.is_file())
    actual = {
        name: None if not path.is_file() else sha256(path)
        for name, path in paths.items()
    }
    expected_flat = {
        "policy": EXPECTED["policy"],
        "golden": EXPECTED["golden"],
        "corrected_contract": EXPECTED["corrected_contract"],
        "v1_invalidation": EXPECTED["v1_invalidation"],
    }
    for label in labels:
        expected_flat[f"gate3_sensor_{label}"] = EXPECTED["gate3_sensor"][
            label
        ]
        expected_flat[f"gate3_summary_{label}"] = EXPECTED["gate3_summary"][
            label
        ]
    hash_checks = {
        name: actual[name] == expected for name, expected in expected_flat.items()
    }
    provenance_checks: dict[str, bool] = {}
    for label in labels:
        summary_path = paths[f"gate3_summary_{label}"]
        if not summary_path.is_file():
            provenance_checks[label] = False
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        provenance_checks[label] = (
            summary.get("backend") == "x5"
            and summary.get("samples") == 250
            and summary.get("jsonl_sha256")
            == EXPECTED["gate3_sensor"][label]
            and summary.get("environment", {}).get("policy_loaded") is False
            and summary.get("environment", {}).get("servo_bus_accessed")
            is False
            and summary.get("environment", {}).get("torque_enabled") is False
        )
    failed = sorted(
        [
            *(f"hash:{name}" for name, passed in hash_checks.items() if not passed),
            *(
                f"provenance:{name}"
                for name, passed in provenance_checks.items()
                if not passed
            ),
        ]
    )
    status = (
        "PREREGISTERED_T3_V2_OBSERVATION_ZSCORE_AUDIT"
        if not missing and not failed
        else "HOLD_T3_V2_OBSERVATION_ZSCORE_PREREGISTRATION"
    )
    payload = {
        "schema_version": "open_duck.t3_observation_zscore_preregistration.v2",
        "status": status,
        "failed_checks": failed,
        "missing_inputs": missing,
        "input_paths": {name: str(path) for name, path in paths.items()},
        "input_sha256": actual,
        "expected_sha256": expected_flat,
        "hash_checks": hash_checks,
        "provenance_checks": provenance_checks,
        "supersedes": {
            "schema_version": (
                "open_duck.t3_observation_zscore_preregistration.v1"
            ),
            "reason": "v1 included an auto-config trace whose backend is mock",
            "v1_result_decision_weight": 0,
        },
        "normalizer_contract": {
            "policy_input_name": "obs",
            "observation_dimension": 101,
            "mean_initializer": "mlp_13_1/sub/ReadVariableOp:0",
            "reciprocal_std_initializer": (
                "ConstantFolding/mlp_13_1/truediv_recip:0"
            ),
            "equation": "z=(raw_observation-mean)*reciprocal_std",
            "python_normalization_before_inference": False,
        },
        "source_semantics": {
            "golden": (
                "two complete 101-D observations from the preserved suspended "
                "runtime capture"
            ),
            "corrected_contract": (
                "one complete 101-D corrected-knee observation extracted from "
                "the second suspended replay"
            ),
            "gate3": (
                "x5-provenance direct gyro, acceleration, and contact "
                "components only; no unrecorded policy fields are synthesized"
            ),
            "excluded": (
                "all mock, sim, summary-only, and unhashable raw replay data"
            ),
        },
        "analysis": {
            "report_rows": 101,
            "statistics": [
                "signed_z_p50",
                "absolute_z_p50",
                "absolute_z_p95",
                "absolute_z_max",
                "sample_count",
                "source_count",
            ],
            "sort": "descending absolute_z_max; uncovered rows last",
            "threshold_absolute_z": 0.5,
            "minimum_sustained_samples": 50,
            "sustained_definition": (
                "at least 50 consecutive valid 50-Hz samples with abs(z)>0.5 "
                "within one hash-frozen x5 source"
            ),
            "stale_samples": "reject",
            "missing_channel_values": "report unavailable; never synthesize",
        },
        "decision_rule": {
            "contract_violation_candidate": (
                "flag every channel/source pair satisfying the frozen "
                "sustained definition; deliberate tilt/contact labels remain "
                "labeled and require interpretation rather than erasure"
            ),
            "complete_answer": (
                "requires every channel to have 50 consecutive complete-policy-"
                "observation samples"
            ),
            "incomplete_coverage": (
                "publish measured rows and HOLD the claim that obs[3] is the "
                "only violation"
            ),
            "selection_weight": 0,
        },
        "known_capture_gap": {
            "expected_corrected_replay": (
                "outputs/first_evidence/20260627T221019Z_corrected_dynamic_"
                "replay/suspended_policy_replay_x008_corrected_knee.jsonl"
            ),
            "raw_file_available": False,
            "effect": (
                "T2 cannot execute and T3 cannot claim full replay coverage "
                "without a separately hash-frozen recovery"
            ),
        },
        "authority": {
            "offline_cpu_only": True,
            "robot_or_rdk_access": False,
            "policy_modification": False,
            "training_steps": 0,
            "hosted_compute": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(
        {
            "input_sha256": payload["input_sha256"],
            "provenance_checks": payload["provenance_checks"],
            "normalizer_contract": payload["normalizer_contract"],
            "source_semantics": payload["source_semantics"],
            "analysis": payload["analysis"],
            "decision_rule": payload["decision_rule"],
        }
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T3 observation z-score v2 preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        "- V1 is invalid because it included a mock auto-config trace; its "
        "draft result has zero decision weight.\n"
        "- Every Gate 3 source is hash-frozen and independently verifies "
        "`backend: x5`, 250 samples, no policy, no servo bus, and no torque.\n"
        "- Missing policy fields remain unavailable and are never synthesized.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
