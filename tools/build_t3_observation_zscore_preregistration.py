#!/usr/bin/env python3
"""Preregister the offline T3 real-observation z-score audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t3_observation_zscore_preregistration.json"
MARKDOWN = ANALYSIS / "T3_OBSERVATION_ZSCORE_PREREGISTRATION_20260725.md"
POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
GOLDEN = ANALYSIS / "legacy_runtime_golden_vector_20260621.json"
AUTO_CONFIG_DIR = "duck-auto-config-2529a83096d04812b0d5491303b2e42a"
GATE3_DIR = "open-duck-gate3-review-hrmv5w64"
CORRECTED_CONTRACT = (
    "open-duck-gate3-source-1792d9c/artifacts/contracts/"
    "legacy-contract-snapshot.json"
)

EXPECTED = {
    "policy_sha256": (
        "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067"
    ),
    "golden_sha256": (
        "91a95e798b83fccc79452ca3857cda7f08b98f495967de0384a9d570d067ff87"
    ),
    "corrected_contract_sha256": (
        "298753fb30c658321161df50f668ad7ab25121a1958c4b7bbdb1c543caf06bff"
    ),
    "auto_config_sha256": (
        "b08327a9fd04db8e4971c3ecafd6450ae9416d58fa852890e176951b0250bc38"
    ),
    "gate3_sensor_sha256": {
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

    gate3_files = {
        label: real_root / GATE3_DIR / label / "sensor.jsonl"
        for label in EXPECTED["gate3_sensor_sha256"]
    }
    paths = {
        "policy": POLICY,
        "golden": GOLDEN,
        "corrected_contract": real_root / CORRECTED_CONTRACT,
        "auto_config": real_root / AUTO_CONFIG_DIR / "trace.jsonl",
        **{f"gate3_{key}": value for key, value in gate3_files.items()},
    }
    missing = sorted(name for name, path in paths.items() if not path.is_file())
    actual = {
        name: None if not path.is_file() else sha256(path)
        for name, path in paths.items()
    }
    gate3_actual = {
        label: actual[f"gate3_{label}"] for label in gate3_files
    }
    hash_checks = {
        "policy": actual["policy"] == EXPECTED["policy_sha256"],
        "golden": actual["golden"] == EXPECTED["golden_sha256"],
        "corrected_contract": (
            actual["corrected_contract"]
            == EXPECTED["corrected_contract_sha256"]
        ),
        "auto_config": (
            actual["auto_config"] == EXPECTED["auto_config_sha256"]
        ),
        "gate3": gate3_actual == EXPECTED["gate3_sensor_sha256"],
    }
    failed = sorted(name for name, passed in hash_checks.items() if not passed)
    status = (
        "PREREGISTERED_T3_OBSERVATION_ZSCORE_AUDIT"
        if not missing and not failed
        else "HOLD_T3_OBSERVATION_ZSCORE_PREREGISTRATION"
    )
    payload = {
        "schema_version": "open_duck.t3_observation_zscore_preregistration.v1",
        "status": status,
        "failed_checks": failed,
        "missing_inputs": missing,
        "input_paths": {name: str(path) for name, path in paths.items()},
        "input_sha256": actual,
        "expected_sha256": {
            **{
                key: value
                for key, value in EXPECTED.items()
                if key != "gate3_sensor_sha256"
            },
            "gate3_sensor_sha256": EXPECTED["gate3_sensor_sha256"],
        },
        "hash_checks": hash_checks,
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
                "direct gyro, acceleration, and contact channels only; no "
                "unrecorded policy fields may be synthesized"
            ),
            "auto_config": (
                "direct gyro, acceleration, actual joint position, target, and "
                "contact components plus timestamp-derived joint velocity; "
                "these are component observations, not fabricated complete "
                "policy observations"
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
            "sustained_definition": (
                "at least 50 consecutive valid 50-Hz-equivalent samples "
                "with abs(z)>0.5 within one source"
            ),
            "minimum_sustained_samples": 50,
            "stale_samples": "reject",
            "missing_channel_values": (
                "report as unavailable; never fill with zero, home, or a "
                "simulated value"
            ),
        },
        "decision_rule": {
            "contract_violation": (
                "flag every channel/source pair satisfying the frozen "
                "sustained definition"
            ),
            "complete_answer": (
                "requires every channel to have at least one sustained-window-"
                "sized sequence of direct complete-policy-observation evidence"
            ),
            "incomplete_coverage": (
                "publish the measured rows and HOLD the claim that obs[3] is "
                "the only violation"
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
                "unless the raw file is recovered and separately hash-frozen"
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
            "normalizer_contract": payload["normalizer_contract"],
            "source_semantics": payload["source_semantics"],
            "analysis": payload["analysis"],
            "decision_rule": payload["decision_rule"],
            "input_sha256": payload["input_sha256"],
        }
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T3 observation z-score preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        "- Scope: offline analysis only; no policy, simulator, RDK, or robot "
        "mutation.\n"
        "- Rule: flag a channel/source after 50 consecutive valid samples "
        "with `abs(z) > 0.5`.\n"
        "- Coverage rule: missing real fields remain unavailable; they are "
        "never synthesized.\n"
        "- Known hold: the raw corrected 747-tick replay is absent, so T2 is "
        "not executable from the current archive.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
