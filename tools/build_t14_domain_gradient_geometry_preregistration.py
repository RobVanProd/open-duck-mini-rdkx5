#!/usr/bin/env python3
"""Freeze T14's CPU-only broad-vs-negative-COM gradient audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t14_domain_gradient_geometry_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T14_DOMAIN_GRADIENT_GEOMETRY_PREREGISTRATION_20260726.md"
)
RUNNER = ROOT / "tools" / "run_t14_domain_gradient_geometry.py"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PLAYGROUND = Path(r"D:\CodexProjects\Open_Duck_Playground-composed-v175")
SOURCE = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v119-extracted-20260724"
    r"\winner_v119_transition_continuation\training"
    r"\2026_07_24_193907_1003520"
)
CPU_TEMPLATE = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v119-transition-cpu-smoke-20260724\smoke"
    r"\2026_07_24_150649_0"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def exact_objective_family_audit() -> dict[str, Any]:
    """Prove that only a CVaR reporting metric, not this objective, exists."""
    roots = (ROOT / "tools", ROOT / "patches", ANALYSIS)
    excluded = {
        Path(__file__).resolve(),
        RUNNER.resolve(),
        OUTPUT.resolve(),
        MARKDOWN.resolve(),
    }
    patterns = {
        "group_dro": re.compile(r"group[-_ ]?dro", re.IGNORECASE),
        "distributionally_robust": re.compile(
            r"distributionally robust",
            re.IGNORECASE,
        ),
        "worst_domain": re.compile(
            r"worst[-_ ]domain",
            re.IGNORECASE,
        ),
        "minimax": re.compile(r"\bminimax\b", re.IGNORECASE),
    }
    hits: dict[str, list[str]] = {name: [] for name in patterns}
    for root in roots:
        for path in root.rglob("*"):
            if (
                not path.is_file()
                or path.resolve() in excluded
                or path.suffix.lower()
                not in {".py", ".patch", ".json", ".md"}
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for name, pattern in patterns.items():
                if pattern.search(text):
                    hits[name].append(
                        path.relative_to(ROOT).as_posix()
                    )
    cvar_reporting = []
    pattern = re.compile(r"worst_joint_cvar95_rad", re.IGNORECASE)
    for root in roots:
        for path in root.rglob("*"):
            if (
                not path.is_file()
                or path.resolve() in excluded
                or path.suffix.lower() not in {".py", ".json", ".md"}
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if pattern.search(text):
                cvar_reporting.append(
                    path.relative_to(ROOT).as_posix()
                )
    return {
        "objective_term_hits": hits,
        "objective_term_hit_count": sum(
            len(rows) for rows in hits.values()
        ),
        "cvar_reporting_metric_paths": sorted(set(cvar_reporting)),
        "interpretation": (
            "The only CVaR usage is a read-only tracking statistic. "
            "No group-DRO, distributionally robust, worst-domain, or "
            "minimax training objective exists in prior work."
        ),
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T14 preregistration")
    t13 = json.loads(
        (ANALYSIS / "t13_shadow_hidden_result.json").read_text(
            encoding="utf-8"
        )
    )
    t13_audit = json.loads(
        (
            ANALYSIS
            / "t13_shadow_hidden_independent_audit_v2.json"
        ).read_text(encoding="utf-8")
    )
    v3 = json.loads(
        (
            ANALYSIS
            / "winner_v3_variable_configuration_result_corrected.json"
        ).read_text(encoding="utf-8")
    )
    t6 = json.loads(
        (
            ANALYSIS / "t6_corrected_robustness_screen_result.json"
        ).read_text(encoding="utf-8")
    )
    family = exact_objective_family_audit()
    checks = {
        "t13_existing_recurrence_handoff_closed": (
            t13["decision"]
            == "CLOSE_EXISTING_RECURRENT_SHADOW_HANDOFF"
        ),
        "t13_independent_audit_green": (
            t13_audit["status"]
            == "PASS_T13_SHADOW_HIDDEN_INDEPENDENT_AUDIT_V2"
            and t13_audit["issues"] == []
        ),
        "v3_full_variable_configuration_route_failed": (
            v3["decision"]
            == "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT"
        ),
        "t6_v121_negative_com_zero_of_sixteen": (
            next(
                row
                for row in t6["candidates"]
                if row["candidate_id"] == "V121"
            )["green_cells"]
            == 0
        ),
        "exact_worst_domain_objective_untried": (
            family["objective_term_hit_count"] == 0
        ),
        "permanent_d_inputs_present": all(
            path.exists()
            for path in (PLAYGROUND, SOURCE, CPU_TEMPLATE)
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    input_hashes = {
        "runner": sha256(RUNNER),
        "reference": sha256(REFERENCE),
        "source_checkpoint_directory": sha256_directory(SOURCE),
        "cpu_template_directory": sha256_directory(CPU_TEMPLATE),
        "playground_manifest": sha256(
            PLAYGROUND / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "recurrent_network": sha256(
            PLAYGROUND
            / "playground/common/"
            "reference_residual_recurrent_adapter_ppo_networks.py"
        ),
        "joystick": sha256(
            PLAYGROUND / "playground/open_duck_mini_v2/joystick.py"
        ),
        "winner_v3_randomizer": sha256(
            PLAYGROUND
            / "playground/common/winner_v3_variable_configuration.py"
        ),
    }
    basis = {
        "schema_version": (
            "open_duck.t14_domain_gradient_geometry_preregistration.v1"
        ),
        "status": "PREREGISTERED_T14_DOMAIN_GRADIENT_GEOMETRY",
        "failed_checks": failed,
        "checks": checks,
        "question": (
            "At the frozen V121-half actor, does the exact winner-v3 "
            "broad-domain PPO descent direction locally increase the PPO "
            "actor loss of the exact -0.05 m torso-COM P30 domain?"
        ),
        "causal_basis": {
            "actual_blocker": (
                "T6 found V121 at 0/16 under the exact -0.05 m torso-COM "
                "condition while timing, transition, and nominal behavior "
                "were already green."
            ),
            "prior_average_route": (
                "Winner-v3 trained one shared actor on the full uniformly "
                "sampled variable-configuration distribution and produced "
                "no robustness survivor."
            ),
            "closed_response_routes": (
                "T10/T11 closed the added context-to-action family; T12 "
                "closed the response-prefix preparation; T13 independently "
                "closed the existing recurrent shadow handoff."
            ),
            "materially_distinct_open_question": (
                "No prior objective optimized the worst domain or used "
                "group-DRO/minimax selection. T14 measures whether average "
                "objective geometry itself points against the clearance "
                "condition before any optimizer is changed."
            ),
        },
        "prior_objective_family_audit": family,
        "matrix": {
            "domains": [
                "winner_v3_full_distribution_scale_1",
                "exact_negative_com_p30",
                "exact_nominal_p30",
            ],
            "environments_per_domain": 256,
            "ticks_per_environment": 80,
            "unroll_length": 20,
            "sequences_per_domain": 1024,
            "observations_per_domain": 20_480,
            "frozen_minibatches": 4,
            "minibatch_sequences": 256,
            "seed": 20260726,
            "torso_com_negative_offset_m": -0.05,
        },
        "pairing": {
            "reset_keys": "bit-identical across all three domains",
            "policy_standard_normal_draws": (
                "bit-identical across all three domains at every tick"
            ),
            "permutation": (
                "one frozen PCG64 permutation shared by all domains"
            ),
            "source_policy": "V121_TRAIN_MATCHED_HALF",
            "source_normalizer": (
                "V121 source for collection; broad-batch-updated source "
                "normalizer is the primary gradient processor"
            ),
            "sensitivity": (
                "the source-frozen normalizer must preserve the primary "
                "interference sign"
            ),
        },
        "pass_rule": {
            "all_rollouts_and_gradients_finite": True,
            "exact_model_and_pairing_readbacks": True,
            "broad_and_negative_gradients_nonzero": True,
            "primary_gradient_cosine_strictly_negative": True,
            "negative_loss_derivative_along_broad_descent": (
                "> 64*eps32*max(1,abs(dot),norm_product)"
            ),
            "harm_sign_minibatches": "at least 3 of 4",
            "source_normalizer_sensitivity": (
                "strictly negative cosine and positive harm derivative "
                "above the same tolerance"
            ),
            "source_checkpoint_bytes_unchanged": True,
        },
        "decision_rule": {
            "pass": (
                "Earn only a separately preregistered CPU implementation "
                "contract for one parameter-free worst-domain/group-DRO "
                "continuation objective. No hosted run is earned by T14."
            ),
            "fail": (
                "Close worst-domain objective continuation from V121-half; "
                "do not narrow the domain, alter the seed, threshold, "
                "normalizer, batch, or gradient definition."
            ),
            "partial_results_selection_weight": 0,
            "no_threshold_changes_after_execution": True,
        },
        "input_hashes": input_hashes,
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_or_colab_compute": False,
            "candidate_selection": False,
            "deployment_or_gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "rollout_observations": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T14 domain-gradient geometry preregistration",
                "",
                (
                    "T14 asks whether the already-tried broad average "
                    "objective points uphill on the exact negative-COM "
                    "clearance condition."
                ),
                "",
                "- Domains: broad V3 / exact COM −0.05 m P30 / nominal P30",
                "- Per domain: 256 environments × 80 ticks = 20,480 observations",
                "- Actor updates / behavior cells / hosted CU / hardware: 0 / 0 / 0 / 0",
                (
                    "- Pass earns only a CPU implementation contract for "
                    "a worst-domain objective."
                ),
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
