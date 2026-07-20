from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"

OUTPUT_JSON = ANALYSIS / "winner_v3_current_gate_application_contract.json"
OUTPUT_MD = ANALYSIS / "WINNER_V3_CURRENT_GATE_APPLICATION_CONTRACT_20260720.md"

SOURCE_AUDIT_COMMIT = "5f329136597f61051852a0fc492c3549c7e8d5a4"
SOURCE_AUDIT_JSON_SHA256 = "aebccef11fa96d374d547a0362f4d6e490d843c9aa059ae86891ee7b7a724934"
SOURCE_AUDIT_MD_SHA256 = "62ea1e318c29de8b70afa738f541d656262c7224fd91ab96809a75881c5264a6"

SPEC_URL = (
    "https://www.feetechrc.com/Data/feetechrc/upload/file/20200611/"
    "6372749961523760249976542.pdf"
)
CATALOG_URL = (
    "https://www.feetechrc.com/Data/feetechrc/upload/file/20240706/"
    "2024%E9%A3%9E%E7%89%B9%E5%AE%A3%E4%BC%A0%E5%86%8C.pdf"
)

KGF_CM_TO_NM = 0.0980665
MOTOR_CONSTANT_KGF_CM_PER_A = 8.0
MOTOR_CONSTANT_NM_PER_A = MOTOR_CONSTANT_KGF_CM_PER_A * KGF_CM_TO_NM
RATED_CURRENT_A = 0.65
STALL_CURRENT_A = 2.5
STALL_TORQUE_KGF_CM = 19.5
STALL_TORQUE_NM = STALL_TORQUE_KGF_CM * KGF_CM_TO_NM
OVERCURRENT_A = 2.0
OVERCURRENT_DURATION_S = 2.0
CONTROL_FREQUENCY_HZ = 50
OVERCURRENT_TICKS = int(OVERCURRENT_DURATION_S * CONTROL_FREQUENCY_HZ)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_contract() -> dict[str, object]:
    assert math.isclose(MOTOR_CONSTANT_NM_PER_A, 0.784532, abs_tol=1e-12)
    assert OVERCURRENT_TICKS == 100
    return {
        "schema_version": "open_duck_mini.winner_v3_current_gate_application_contract.v1",
        "status": "PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT",
        "decision": "AUTHORIZE_AUTOMATIC_RESPONSE_CONDITIONING_INTERFACE_PREREGISTRATION_ONLY",
        "scope": {
            "prospective_only": True,
            "completed_winner_v3_result_reclassified": False,
            "training_authorized": False,
            "hosted_compute_authorized": False,
            "runtime_change_authorized": False,
            "robot_or_rdkx5_authorized": False,
            "torque_or_motion_authorized": False,
        },
        "superseded_interpretation": {
            "statement": (
                "The corrected failure-attribution artifact said no manufacturer source "
                "supported the repository's exact 8 kgf.cm/A conversion. Feetech's "
                "2020-04-10 STS3215 product specification explicitly reports Kt=8 kg.cm/A."
            ),
            "source_result_unchanged": True,
            "source_result_commit": SOURCE_AUDIT_COMMIT,
            "source_audit_json_sha256": SOURCE_AUDIT_JSON_SHA256,
            "source_audit_md_sha256": SOURCE_AUDIT_MD_SHA256,
        },
        "manufacturer_evidence": {
            "detailed_specification": {
                "manufacturer": "Shenzhen FEETECH RC Model Co., Ltd.",
                "model": "STS3215",
                "edition": "A/0",
                "date": "2020-04-10",
                "url": SPEC_URL,
                "electrical_specification": {
                    "operating_voltage_v": [4.0, 7.4],
                    "rated_torque_kgf_cm_at_7p4v": 5.0,
                    "rated_current_a_at_7p4v": RATED_CURRENT_A,
                    "stall_torque_kgf_cm_at_7p4v": STALL_TORQUE_KGF_CM,
                    "stall_current_a_at_7p4v": STALL_CURRENT_A,
                    "motor_constant_kgf_cm_per_a": MOTOR_CONSTANT_KGF_CM_PER_A,
                },
                "electronic_protection": {
                    "overcurrent": "current greater than 2 A for 2 s disables output",
                    "overload": "blocked above 80% of stall for 2 s enters protection",
                    "overtemperature": "temperature greater than 70 C disables torque",
                },
                "reliability_test": (
                    "greater than 100000 cycles at one-fifth stall torque with 0.25 s "
                    "forward, 0.5 s stop, 0.25 s reverse, 0.5 s stop"
                ),
            },
            "catalog_corroboration": {
                "manufacturer": "Shenzhen FEETECH RC Model Co., Ltd.",
                "model": "ST-3215-C001",
                "url": CATALOG_URL,
                "rated_current_a_at_7p4v": RATED_CURRENT_A,
                "stall_current_a_at_7p4v": STALL_CURRENT_A,
                "rated_torque_kgf_cm_at_7p4v": 5.0,
                "stall_torque_kgf_cm_at_7p4v": STALL_TORQUE_KGF_CM,
            },
        },
        "conversion": {
            "kgf_cm_to_nm": KGF_CM_TO_NM,
            "manufacturer_motor_constant_kgf_cm_per_a": MOTOR_CONSTANT_KGF_CM_PER_A,
            "manufacturer_motor_constant_nm_per_a": MOTOR_CONSTANT_NM_PER_A,
            "per_tick_current_estimate_a": (
                "abs(MuJoCo data.actuator_force[joint] N.m) / 0.784532 N.m/A"
            ),
            "runtime_telemetry_scale_a_per_count": 0.0065,
            "conversion_supported_by_primary_source": True,
            "voltage_specific": "7.4 V STS3215 operating point",
        },
        "prospective_offline_candidate_gate": {
            "sample_clock": "exact simulator 50 Hz ticks",
            "per_joint_peak_torque_nm_max": STALL_TORQUE_NM,
            "per_joint_peak_torque_kgf_cm_max": STALL_TORQUE_KGF_CM,
            "per_joint_peak_current_a_max": STALL_CURRENT_A,
            "strict_overcurrent_threshold_a": OVERCURRENT_A,
            "strict_overcurrent_max_consecutive_ticks": OVERCURRENT_TICKS - 1,
            "strict_overcurrent_trip_ticks": OVERCURRENT_TICKS,
            "strict_overcurrent_trip_duration_s": OVERCURRENT_DURATION_S,
            "all_joints_must_pass": True,
            "early_terminated_population": "evaluate every recorded tick before termination",
            "rated_current_p95": {
                "value_a": RATED_CURRENT_A,
                "role": "reported diagnostic only",
                "candidate_pass_fail": False,
                "reason": (
                    "manufacturer evidence defines a rated operating point but does not "
                    "define p95 over a 600-tick rollout as a safety or thermal rule"
                ),
            },
        },
        "prospective_runtime_telemetry_gate": {
            "firmware_protection_remains_authoritative": True,
            "temperature_shutdown_c": 70.0,
            "overcurrent_threshold_a": OVERCURRENT_A,
            "overcurrent_duration_s": OVERCURRENT_DURATION_S,
            "stall_current_a": STALL_CURRENT_A,
            "rated_current_a_reported_not_trip_rule": RATED_CURRENT_A,
            "round_robin_samples_do_not_prove_continuous_sub_tick_current": True,
            "requirements": [
                "record raw current counts and converted amperes with monotonic timestamps",
                "record temperature and device protection status",
                "torque off on device protection, overtemperature, stale telemetry, or watchdog fault",
                "do not infer a thermal duty limit from sparse round-robin current samples",
            ],
        },
        "frozen_follow_up_order": [
            "freeze and obtain runtime review of an automatic-response-conditioned interface",
            "pass a CPU-only response-identifiability and default-off contract",
            "only then preregister at most one training run and the complete behavior matrix",
        ],
    }


def render_markdown(contract: dict[str, object], json_sha256: str) -> str:
    return f"""# Winner-v3 Prospective Current-Gate Application Contract — 2026-07-20

status: `{contract['status']}`

decision: `{contract['decision']}`

JSON SHA-256: `{json_sha256}`

## Correction without reclassification

The completed winner-v3 result remains unchanged. This prospective contract corrects one
source interpretation in the later failure audit: Feetech's detailed 2020-04-10 STS3215
specification explicitly reports `Kt = 8 kg.cm/A`, which converts exactly to
`0.784532 N.m/A`. The simulator's torque-to-current conversion therefore has primary-source
support. The source audit and all 1,024 completed cell classifications remain preserved.

The same specification reports `0.65 A` rated current, `2.5 A` stall current, and electronic
protection that disables output when current is greater than `2 A` for `2 s`. It also reports
`19.5 kg.cm` stall torque and torque shutdown above `70 C`.

Primary specification: {SPEC_URL}

Catalog corroboration: {CATALOG_URL}

## Prospective offline rule

For every joint and every recorded 50 Hz simulator tick:

1. estimate current as `abs(actuator_force_Nm) / 0.784532`;
2. reject demand above the documented `19.5 kg.cm` / `2.5 A` stall envelope;
3. reject any run of `100` consecutive ticks with current strictly greater than `2 A`;
4. evaluate the complete recorded prefix of an early-terminated cell; and
5. require all 14 joints to pass.

The old `p95 <= 0.65 A` quantity remains reported as a rated-duty diagnostic, but it is not a
prospective pass/fail gate. Feetech defines `0.65 A` as a rated operating point; it does not
define p95 over a 600-tick rollout as a protection or thermal rule. No replacement duty-cycle
or thermal threshold is invented.

## Runtime application

Runtime must retain the servo's own over-current/overload protection, record timestamped raw
current, temperature, and device protection status, and torque off on a device protection or
temperature fault. Round-robin current telemetry cannot prove continuous sub-sample current,
so it is evidence and trend monitoring rather than a replacement for servo firmware protection.

## Authority

This contract authorizes only the automatic-response interface preregistration and its CPU-only
contract. It does not authorize training, Colab, GPU/iGPU use, runtime implementation, X5 or
robot access, torque, motion, Gate 5, deployment, or robot clearance.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args(argv)

    contract = build_contract()
    json_bytes = (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode("utf-8")
    json_sha256 = sha256_bytes(json_bytes)
    markdown = render_markdown(contract, json_sha256)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(json_bytes)
    args.output_md.write_text(markdown, encoding="utf-8")
    print(f"status={contract['status']} json_sha256={json_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
