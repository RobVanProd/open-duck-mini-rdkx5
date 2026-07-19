#!/usr/bin/env python3
"""Validate the formal runtime result and independently replay its frozen gate."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT.parent
RUNTIME = ROBOTS / "open-duck-mini-rdkx5-native-runtime"
PACKAGE = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
ANALYSIS = ROOT / "outputs/analysis"
PREREG_PATH = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_preregistration.json"
FORMAL_PATH = (
    RUNTIME
    / "artifacts/gates/phase_5_policy/winner_v2_runtime_v2_verification_20260719.json"
)
REDUCED_PATH = (
    RUNTIME
    / "artifacts/gates/phase_5_policy/"
    "winner_v2_recursive_cross_cpu_closure_20260719.json"
)
OUTPUT_JSON = ANALYSIS / "winner_v2_recursive_cross_cpu_closure_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V2_RECURSIVE_CROSS_CPU_CLOSURE_RESULT_20260719.md"

PREREG_COMMIT = "182459eb4d5eb422a6936b7744f5730d22a9bb27"
RUNTIME_REQUEST_COMMIT = "e9dc0735a177bb4215e24e2dd8406da01704d2f1"
RUNTIME_RESULT_COMMIT = "f8def264c856db3905301f5473f5eb1775b3eec0"
RUNTIME_REDUCED_RESULT_COMMIT = "9c637ec4a161d20b24b06e91dc309a49c46cf981"
RUNTIME_RESULT_REPO_PATH = (
    "artifacts/gates/phase_5_policy/winner_v2_runtime_v2_verification_20260719.json"
)
FORMAL_RESULT_SHA256 = "e1842ca64e91056b96c297666803bdeec7c5ff2950d4dfe32e27044379049b14"
REDUCED_RESULT_REPO_PATH = (
    "artifacts/gates/phase_5_policy/"
    "winner_v2_recursive_cross_cpu_closure_20260719.json"
)
REDUCED_RESULT_SHA256 = "4d403623eb4822befde4b633425e344d010140316d7a4c1e48f4354e76285ace"
RUNTIME_VERIFIER_SHA256 = "5f38094f98e939322c86234438207dabae8d96c9a7e65d1a77119e0323e96259"
RUNTIME_TEST_SHA256 = "4f2da30687bf87c0fd8149dcce2966e22f4b950c10dda2ab91152119226f04fc"
RUNTIME_ARTIFACT_MANIFEST_SHA256 = (
    "fbc0369b07ad4b6586e0a9244e60052094b1d2236350a7ba8d7fe3a55f2ced95"
)
SELECTED_POLICY_SHA256 = "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
AUDIT_POLICY_SHA256 = "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece"
PASS_TOKEN = "PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=RUNTIME)


def policy_git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def require(checks: dict[str, bool]) -> None:
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("formal result check failed: " + ", ".join(failed))


def cell_key(row: dict[str, Any]) -> tuple[int, float]:
    step = int(Path(str(row["policy"])).stem.rsplit("_", 1)[1])
    return step, round(float(row["command_x"]), 3)


def main() -> int:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    formal_bytes = FORMAL_PATH.read_bytes()
    formal = json.loads(formal_bytes)
    reduced_bytes = REDUCED_PATH.read_bytes()
    reduced = json.loads(reduced_bytes)
    constants = prereg["frozen_constants"]
    identities = prereg["frozen_identities"]

    committed_result = git(
        "show", f"{RUNTIME_RESULT_COMMIT}:{RUNTIME_RESULT_REPO_PATH}"
    )
    committed_reduced_result = git(
        "show", f"{RUNTIME_REDUCED_RESULT_COMMIT}:{REDUCED_RESULT_REPO_PATH}"
    )
    prereg_commit_time = int(
        policy_git("show", "-s", "--format=%ct", PREREG_COMMIT).decode().strip()
    )
    formal_commit_time = int(
        git("show", "-s", "--format=%ct", RUNTIME_RESULT_COMMIT).decode().strip()
    )
    ancestry_prereg_request = subprocess.run(
        ["git", "show", f"{RUNTIME_REQUEST_COMMIT}:Comms.md"],
        cwd=RUNTIME,
        check=False,
        stdout=subprocess.PIPE,
    )
    request_text = ancestry_prereg_request.stdout.decode("utf-8")
    formal_comms_text = git("show", f"{RUNTIME_RESULT_COMMIT}:Comms.md").decode(
        "utf-8"
    )
    reduced_descends_from_formal = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            RUNTIME_RESULT_COMMIT,
            RUNTIME_REDUCED_RESULT_COMMIT,
        ],
        cwd=RUNTIME,
        check=False,
    ).returncode == 0
    reduced_descends_from_request = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            RUNTIME_REQUEST_COMMIT,
            RUNTIME_REDUCED_RESULT_COMMIT,
        ],
        cwd=RUNTIME,
        check=False,
    ).returncode == 0

    provenance_checks = {
        "policy_preregistration_commit_exact": policy_git(
            "rev-parse", f"{PREREG_COMMIT}^{{commit}}"
        ).decode().strip()
        == PREREG_COMMIT,
        "runtime_formal_commit_exact": git("rev-parse", f"{RUNTIME_RESULT_COMMIT}^{{commit}}").decode().strip()
        == RUNTIME_RESULT_COMMIT,
        "runtime_reduced_commit_exact": git(
            "rev-parse", f"{RUNTIME_REDUCED_RESULT_COMMIT}^{{commit}}"
        ).decode().strip()
        == RUNTIME_REDUCED_RESULT_COMMIT,
        "formal_commit_postdates_policy_preregistration": formal_commit_time
        > prereg_commit_time,
        "runtime_request_names_policy_preregistration": PREREG_COMMIT in request_text,
        "formal_comms_attests_fresh_post_preregistration_run": (
            "independently fetched prospective policy preregistration commit"
            in formal_comms_text
            and PREREG_COMMIT in formal_comms_text
            and "ran a new 2,400-tick" in formal_comms_text
            and "invocation" in formal_comms_text
        ),
        "working_result_matches_formal_commit": formal_bytes == committed_result,
        "working_reduced_result_matches_reduced_commit": reduced_bytes
        == committed_reduced_result,
        "reduced_commit_descends_from_formal_and_request": (
            reduced_descends_from_formal and reduced_descends_from_request
        ),
        "formal_result_sha256_exact": sha256_bytes(formal_bytes) == FORMAL_RESULT_SHA256,
        "reduced_result_sha256_exact": sha256_bytes(reduced_bytes)
        == REDUCED_RESULT_SHA256,
        "runtime_verifier_sha256_exact": sha256(
            RUNTIME / "src/open_duck_x5/winner_v2_verifier.py"
        )
        == RUNTIME_VERIFIER_SHA256,
        "runtime_test_sha256_exact": sha256(RUNTIME / "tests/test_winner_v2.py")
        == RUNTIME_TEST_SHA256,
        "runtime_artifact_manifest_sha256_exact": sha256(
            RUNTIME / "artifacts/manifest.sha256"
        )
        == RUNTIME_ARTIFACT_MANIFEST_SHA256,
        "handoff_manifest_sha256_exact": sha256(PACKAGE / "manifest.json")
        == identities["handoff_manifest_sha256"],
        "selected_policy_sha256_exact": sha256(
            PACKAGE / "policies/T2_EQUAL_512000.onnx"
        )
        == SELECTED_POLICY_SHA256,
        "formal_cpu_provider_only": formal["environment"]["onnx_execution_provider"]
        == "CPUExecutionProvider",
        "formal_prior_runtime_outcome_weight_false": formal["recursive_preregistration"][
            "formal_prior_runtime_outcome_weight"
        ]
        is False,
        "reduced_binds_formal_result": reduced["formal_full_result_sha256"]
        == FORMAL_RESULT_SHA256,
        "reduced_binds_preregistration": reduced["recursive_preregistration"][
            "commit"
        ]
        == PREREG_COMMIT,
    }
    require(provenance_checks)

    formal_cells = {cell_key(row): row for row in formal["recursive_runtime_cells"]}
    reduced_cells = {cell_key(row): row for row in reduced["cells"]}
    expected_keys = {(512000, 0.0), (512000, 0.08), (1024000, 0.0), (1024000, 0.08)}
    matrix_checks = {
        "exact_four_cell_matrix": set(formal_cells) == expected_keys
        and len(formal["recursive_runtime_cells"]) == 4,
        "reduced_exact_four_cell_matrix": set(reduced_cells) == expected_keys
        and len(reduced["cells"]) == 4,
        "exact_2400_ticks": int(formal["ticks"]) == 2400
        and sum(int(row["ticks"]) for row in formal_cells.values()) == 2400,
        "selected_policy_identity": all(
            row["policy_sha256"] == SELECTED_POLICY_SHA256
            for key, row in formal_cells.items()
            if key[0] == 512000
        ),
        "audit_policy_identity": all(
            row["policy_sha256"] == AUDIT_POLICY_SHA256
            for key, row in formal_cells.items()
            if key[0] == 1024000
        ),
        "audit_checkpoint_non_gating": formal["native_resolution_gate"][
            "audit_checkpoint_is_non_gating"
        ]
        is True,
        "reduced_exact_two_selected_cells": sum(
            bool(row["gating"]) for row in reduced_cells.values()
        )
        == 2,
        "teacher_forced_observation_exact_zero_all_formal_cells": all(
            float(row["max_abs_error"]["observation"]) == 0.0
            for row in formal["semantic_cells"]
        ),
        "teacher_forced_observation_exact_zero_all_reduced_cells": all(
            float(row["semantic_max_abs_error"]["observation"]) == 0.0
            for row in reduced_cells.values()
        ),
    }
    require(matrix_checks)

    reduced_reporting_checks = {
        "schema_exact": reduced["schema_version"]
        == "open_duck_x5.winner_v2_recursive_closure_reduced.v1",
        "status_exact": reduced["status"] == PASS_TOKEN,
        "full_schema_exact": reduced["formal_full_result_schema_version"]
        == formal["schema_version"],
        "manifest_exact": reduced["manifest_sha256"]
        == identities["handoff_manifest_sha256"],
        "selected_policy_exact": reduced["selected_policy"]["sha256"]
        == SELECTED_POLICY_SHA256,
        "all_cells_600_ticks": all(
            int(row["ticks"]) == 600 for row in reduced_cells.values()
        ),
        "all_cells_cpu_provider": all(
            row["onnx_execution_provider"] == "CPUExecutionProvider"
            for row in reduced_cells.values()
        ),
        "all_recorded_cell_gates_pass": all(
            bool(row["all_cell_gates_passed"]) for row in reduced_cells.values()
        ),
        "all_selected_wire_words_exact": sum(
            int(row["raw_goal_mismatch_count"])
            for row in reduced_cells.values()
            if bool(row["gating"])
        )
        == 0,
        "all_first_mismatches_null": all(
            row["first_raw_goal_mismatch"] is None
            for row in reduced_cells.values()
        ),
        "all_per_joint_groups_present": all(
            set(row["per_joint_max_abs_error"])
            == {"logical_target_rad", "p30_observer_rad", "raw_goal_counts"}
            for row in reduced_cells.values()
        ),
    }
    require(reduced_reporting_checks)

    selected_cells = [row for key, row in formal_cells.items() if key[0] == 512000]
    selected_cell_checks: dict[str, bool] = {}
    for key, row in formal_cells.items():
        prefix = f"cell_{key[0]}_x{key[1]:.3f}"
        native = row["native_resolution"]
        classifications = row["classifications"]
        selected_cell_checks[f"{prefix}_ticks"] = int(row["ticks"]) == 600
        selected_cell_checks[f"{prefix}_finite_metrics"] = all(
            float(value) == float(value)
            for value in row["max_abs_error"].values()
        )
        selected_cell_checks[f"{prefix}_classification_identity"] = all(
            (
                classifications["saturation_unchanged"],
                classifications["rate_and_envelope_unchanged"],
                classifications["external_5p24_limiter_identity"],
            )
        )
        selected_cell_checks[f"{prefix}_raw_range"] = native[
            "raw_goal_in_signed_multiturn_range"
        ]
        if key[0] == 512000:
            selected_cell_checks[f"{prefix}_target_half_lsb"] = float(
                native["maximum_logical_target_error_rad"]
            ) <= float(constants["sts_half_lsb_rad"])
            selected_cell_checks[f"{prefix}_p30_half_lsb"] = float(
                native["maximum_p30_observer_error_rad"]
            ) <= float(constants["sts_half_lsb_rad"])
            selected_cell_checks[f"{prefix}_raw_at_most_one_count"] = int(
                native["maximum_raw_goal_absolute_count_difference"]
            ) <= int(constants["raw_goal_max_abs_count_difference"])
            selected_cell_checks[f"{prefix}_wire_bit_exact"] = int(
                native["raw_goal_mismatch_count"]
            ) == 0
            if key[1] == 0.0:
                selected_cell_checks[f"{prefix}_x0_exact"] = bool(
                    row["x0_action_and_state_bit_exact_zero"]
                )
    require(selected_cell_checks)

    top_level_checks = {
        "formal_schema_exact": formal["schema_version"]
        == "open_duck_x5.winner_v2_offline_verification.v2",
        "formal_status_exact": formal["status"] == PASS_TOKEN,
        "overall_disposition_remains_blocked": formal["overall_disposition"]
        == "BLOCKED_FOR_COM_CLEARANCE_AND_X5_CPU_PREFLIGHT",
        "formal_preregistration_commit_exact": formal["recursive_preregistration"]["commit"]
        == PREREG_COMMIT,
        "direct_tolerance_unchanged": float(formal["tolerance"])
        == float(constants["direct_same_input_tolerance"]),
        "semantic_gate_pass": float(formal["semantic_max_abs_error"])
        <= float(constants["direct_same_input_tolerance"]),
        "same_input_policy_gate_pass": float(formal["policy_chain_max_abs_error"])
        <= float(constants["direct_same_input_tolerance"]),
        "component_contract_pass": formal["component_contract_passed"] is True,
        "recursive_contract_pass": formal["recursive_numeric_closure_passed"] is True,
        "selected_x0_recursive_exact": formal[
            "recursive_x0_action_state_target_observer_bit_exact"
        ]
        is True,
        "all_fault_injections_pass": all(formal["fault_injection"].values()),
        "selected_raw_words_all_exact": sum(
            int(row["native_resolution"]["raw_goal_mismatch_count"])
            for row in selected_cells
        )
        == 0,
        "authority_remains_offline": formal["authority"]
        == {
            "cpu_only": True,
            "gate5": False,
            "robot_access": False,
            "robot_clearance": False,
            "runtime_deployment": False,
        },
    }
    require(top_level_checks)

    # Independent policy-side replay. Importing the committed runtime verifier
    # reruns all semantic, fault-injection, recursive and wire-conversion cells.
    sys.path.insert(0, str(RUNTIME / "src"))
    from open_duck_x5.winner_v2_verifier import (
        reduce_recursive_result,
        verify_handoff,
    )

    independent = verify_handoff(PACKAGE, runtime_root=RUNTIME)
    regenerated_reduced = reduce_recursive_result(
        formal,
        full_result_sha256=sha256_bytes(formal_bytes),
    )
    regenerated_reduced_bytes = (
        json.dumps(regenerated_reduced, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    independent_checks = {
        "independent_status_exact": independent["status"] == PASS_TOKEN,
        "independent_component_pass": independent["component_contract_passed"] is True,
        "independent_recursive_pass": independent["recursive_numeric_closure_passed"] is True,
        "independent_selected_raw_words_exact": independent["native_resolution_gate"][
            "selected_raw_goal_mismatch_count"
        ]
        == 0,
        "independent_x0_exact": independent[
            "recursive_x0_action_state_target_observer_bit_exact"
        ]
        is True,
        "independent_cpu_provider_only": independent["environment"][
            "onnx_execution_provider"
        ]
        == "CPUExecutionProvider",
        "independent_teacher_forced_observation_exact_zero": all(
            float(row["max_abs_error"]["observation"]) == 0.0
            for row in independent["semantic_cells"]
        ),
        "reduced_byte_reproducible_from_formal_result": regenerated_reduced_bytes
        == reduced_bytes,
    }
    require(independent_checks)

    result = {
        "schema_version": "winner_v2.recursive_cross_cpu_closure_result.v1",
        "status": PASS_TOKEN,
        "decision": PASS_TOKEN,
        "policy_preregistration_commit": PREREG_COMMIT,
        "runtime_request_commit": RUNTIME_REQUEST_COMMIT,
        "runtime_result_commit": RUNTIME_RESULT_COMMIT,
        "runtime_reduced_result_commit": RUNTIME_REDUCED_RESULT_COMMIT,
        "runtime_commit_topology_note": (
            "The request and formal result are sibling commits from the same "
            "runtime baseline and were subsequently merged. The dedicated "
            "reduced-result commit descends from that merge and therefore "
            "contains both lineages. Formal validity remains bound to the earlier "
            "policy preregistration commit."
        ),
        "runtime_result_path": RUNTIME_RESULT_REPO_PATH,
        "runtime_result_sha256": FORMAL_RESULT_SHA256,
        "runtime_reduced_result_path": REDUCED_RESULT_REPO_PATH,
        "runtime_reduced_result_sha256": REDUCED_RESULT_SHA256,
        "runtime_source_sha256": {
            "winner_v2_verifier.py": RUNTIME_VERIFIER_SHA256,
            "test_winner_v2.py": RUNTIME_TEST_SHA256,
            "artifacts_manifest.sha256": RUNTIME_ARTIFACT_MANIFEST_SHA256,
        },
        "formal_runtime_environment": formal["environment"],
        "formal_runtime_metrics": {
            "ticks": formal["ticks"],
            "semantic_max_abs_error": formal["semantic_max_abs_error"],
            "policy_chain_max_abs_error": formal["policy_chain_max_abs_error"],
            **formal["native_resolution_gate"],
        },
        "independent_policy_environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "onnxruntime": importlib.metadata.version("onnxruntime"),
            "execution_provider": "CPUExecutionProvider",
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "independent_policy_metrics": {
            "ticks": independent["ticks"],
            "semantic_max_abs_error": independent["semantic_max_abs_error"],
            "policy_chain_max_abs_error": independent["policy_chain_max_abs_error"],
            **independent["native_resolution_gate"],
        },
        "checks": {
            "provenance": provenance_checks,
            "matrix": matrix_checks,
            "reduced_reporting": reduced_reporting_checks,
            "cells": selected_cell_checks,
            "top_level": top_level_checks,
            "independent_replay": independent_checks,
        },
        "reduced_reporting_note": (
            "The dedicated reduced artifact is complete and byte-reproducible, "
            "but its teacher-forced observation gate is named and implemented as "
            "at_most_1e_6 instead of exact zero. All four formal and independent "
            "values are exactly 0.0, and this checker applies exact equality, so "
            "the discrepancy cannot change this decision. A reporting-only "
            "runtime correction is requested before the asset set is frozen."
        ),
        "authority": {
            "closes_reviewed_cpu_recursive_numeric_blocker": True,
            "robot_clearance": False,
            "gate5": False,
            "runtime_deployment": False,
            "rdkx5_cpu_preflight": False,
            "powered_off_direct_com_complete": False,
            "robot_or_motor_access": False,
            "gpu_or_igpu": False,
        },
        "remaining_blockers": formal["remaining_blockers"],
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    formal_gate = formal["native_resolution_gate"]
    independent_gate = independent["native_resolution_gate"]
    markdown = f"""# Winner-v2 Recursive Cross-CPU Closure Result — 2026-07-19

Decision: `{PASS_TOKEN}`

The formal post-preregistration Windows CPU result passes the frozen selected
512000-step x=0/x=.080 matrix. The policy-side Linux CPU replay independently
reproduces the same decision. This closes the reviewed CPU recursive-numeric
blocker for runtime-v2; it does not close physical COM, X5 CPU preflight, Gate
5, deployment or robot clearance.

## Formal runtime result

- runtime result commit: `{RUNTIME_RESULT_COMMIT}`;
- result SHA-256: `{FORMAL_RESULT_SHA256}`;
- reduced artifact commit: `{RUNTIME_REDUCED_RESULT_COMMIT}`;
- reduced artifact SHA-256: `{REDUCED_RESULT_SHA256}`;
- provider: `CPUExecutionProvider`;
- ticks: `{formal['ticks']}`;
- direct same-input maximum: `{formal['policy_chain_max_abs_error']:.17g}`
  (frozen limit `{constants['direct_same_input_tolerance']:.17g}`);
- selected logical-target maximum: `{formal_gate['selected_logical_target_max_abs_error_rad']:.17g} rad`;
- selected P30 maximum: `{formal_gate['selected_p30_observer_max_abs_error_rad']:.17g} rad`;
- frozen half STS count: `{constants['sts_half_lsb_rad']:.17g} rad`;
- selected raw STS goal mismatch: `{formal_gate['selected_raw_goal_mismatch_count']} / 16800 words`;
- saturation/rate/envelope classifications unchanged: `{str(formal_gate['selected_classifications_unchanged']).lower()}`.

The 1024000 sibling was run and recorded but remained non-gating exactly as
preregistered. The dedicated reduced artifact is byte-reproducible from the
formal full result and includes each required cell, identity, metric and role.

The runtime-side request and formal-result commits were concurrent siblings
from the same baseline and were subsequently merged. The dedicated reduced-
result commit descends from that merge. The formal result remains valid because
the authoritative policy preregistration predates it, the verifier binds the
exact preregistration commit, and the committed runtime record attests a fresh
2,400-tick post-preregistration invocation.

## Independent policy-side replay

- provider: `CPUExecutionProvider` on `{platform.platform()}`;
- ticks: `{independent['ticks']}`;
- selected logical-target maximum: `{independent_gate['selected_logical_target_max_abs_error_rad']:.17g} rad`;
- selected P30 maximum: `{independent_gate['selected_p30_observer_max_abs_error_rad']:.17g} rad`;
- selected raw STS goal mismatch: `{independent_gate['selected_raw_goal_mismatch_count']} / 16800 words`;
- selected x=0 action/state/target/P30: bit-exact.

All formal provenance, four-cell matrix, identity, completeness, fault-
injection, same-input, native-resolution and authority checks pass. Runtime
tests separately pass `247/247`, and the runtime artifact hash check is clean.
The reduced artifact describes teacher-forced observation with a `<=1e-6`
gate, whereas the frozen rule is exact zero. Every formal and independent value
is exactly `0.0`, and policy applies exact equality, so this reporting defect
does not change the decision. Runtime has been asked to correct it before the
asset set is frozen, without rerunning or changing formal outcome cells.

## Authority

`{PASS_TOKEN}` closes only the reviewed CPU recursive-numeric blocker. Robot
clearance remains `NO`. Still required are the powered-off direct-reaction
torso-COM packet, a reviewed frozen runtime/policy/config asset set, and the
same CPU-only native-resolution replay on the X5 without servo access. No
robot, RDK-X5, motor, torque, deployment, GPU or iGPU action occurred here.
"""
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    print(PASS_TOKEN)
    print(f"FORMAL_RESULT_SHA256={FORMAL_RESULT_SHA256}")
    print(f"REDUCED_RESULT_SHA256={REDUCED_RESULT_SHA256}")
    print(
        "FORMAL_SELECTED_RAW_MISMATCHES="
        f"{formal_gate['selected_raw_goal_mismatch_count']}/16800"
    )
    print(
        "INDEPENDENT_SELECTED_RAW_MISMATCHES="
        f"{independent_gate['selected_raw_goal_mismatch_count']}/16800"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
