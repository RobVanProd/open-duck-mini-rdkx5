#!/usr/bin/env python3
"""Preregister T95's calibration-FiLM CPU-only falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-t95-film-v1"
)
ASSET_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t95_film_conditioned_assets_v2"
)
ASSET_MANIFEST = ASSET_ROOT / "manifest.json"
OUTPUT = ANALYSIS / "t95_film_conditioned_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T95_FILM_CONDITIONED_CPU_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def context_observability() -> dict[str, Any]:
    t94 = json.loads(
        (ANALYSIS / "t94_r2_calibration_manifold_result.json").read_text(
            encoding="utf-8"
        )
    )
    groups: dict[str, list[str]] = {}
    by_key: dict[tuple[str, str], np.ndarray] = {}
    for cell in t94["cells"]:
        label = f"{cell['configuration_id']}:{cell['fit_id']}"
        groups.setdefault(cell["context_sha256"], []).append(label)
        by_key[(cell["configuration_id"], cell["fit_id"])] = np.asarray(
            cell["context"], dtype=np.float64
        )
    collisions = [
        labels for labels in groups.values() if len(labels) > 1
    ]
    negative_distances = {}
    for fit in ("p30", "p31_34"):
        target = by_key[("TORSO_COM_X_NEG", fit)]
        distances = {
            condition: float(np.linalg.norm(target - context))
            for (condition, candidate_fit), context in by_key.items()
            if candidate_fit == fit and condition != "TORSO_COM_X_NEG"
        }
        negative_distances[fit] = {
            "minimum_distance": min(distances.values()),
            "nearest_condition": min(distances, key=distances.get),
        }
    return {
        "contexts": len(t94["cells"]),
        "unique_contexts": len(groups),
        "exact_collision_groups": collisions,
        "negative_com_contexts_are_unique": all(
            row["minimum_distance"] > 0.0
            for row in negative_distances.values()
        ),
        "negative_com_same_fit_nearest": negative_distances,
        "interpretation": (
            "The prefix cannot identify every R2 axis: floor-friction low, "
            "floor-friction high, and armature low collide exactly within "
            "each actuator fit. It does uniquely expose the current "
            "negative-X COM blocker, so T95 may schedule continuous feedback "
            "gains but may not route discrete experts or claim universal "
            "configuration identification."
        ),
    }


def source_action_head() -> dict[str, Any]:
    assets = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    source = Path(assets["sources"]["source_policy"]["path"])
    if sha256(source) != assets["sources"]["source_policy"]["sha256"]:
        raise ValueError("T95 source policy changed")
    model = onnx.load(source)
    initializers = {
        item.name: numpy_helper.to_array(item)
        for item in model.graph.initializer
    }
    weight = np.asarray(initializers["adapter_weight"], dtype=np.float64)
    return {
        "source_policy": receipt(source),
        "shape": list(weight.shape),
        "rank": int(np.linalg.matrix_rank(weight)),
        "frobenius_norm": float(np.linalg.norm(weight)),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T95: {path}")
    assets = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    t11 = json.loads(
        (ANALYSIS / "t11_context_action_observability_result.json").read_text(
            encoding="utf-8"
        )
    )
    t93 = json.loads(
        (ANALYSIS / "t93_adapter_authority_result.json").read_text(
            encoding="utf-8"
        )
    )
    correction = json.loads(
        (ANALYSIS / "t94_home_offset_reporting_correction.json").read_text(
            encoding="utf-8"
        )
    )
    observability = context_observability()
    action_head = source_action_head()
    sources = {
        "playground_manifest": receipt(
            PLAYGROUND / "T95_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "asset_manifest": receipt(ASSET_MANIFEST),
        "network": receipt(
            ROOT / "patches" / "t95_film_conditioned_v121_networks.py"
        ),
        "update_mask": receipt(
            ROOT / "patches" / "t95_film_only_updates.py"
        ),
        "runner": receipt(
            ROOT / "tools" / "run_t95_film_conditioned_cpu_contract.py"
        ),
        "test": receipt(
            ROOT / "tests" / "test_t95_film_conditioned_cpu.py"
        ),
        "t11_additive_context_closure": receipt(
            ANALYSIS / "t11_context_action_observability_result.json"
        ),
        "t78_validation": receipt(
            ANALYSIS / "t78_recovered_training_validation.json"
        ),
        "t93_adapter_authority": receipt(
            ANALYSIS / "t93_adapter_authority_result.json"
        ),
        "t94_calibration_manifold": receipt(
            ANALYSIS / "t94_r2_calibration_manifold_result.json"
        ),
        "t94_reporting_correction": receipt(
            ANALYSIS / "t94_home_offset_reporting_correction.json"
        ),
    }
    checks = {
        "t95_assets_green": (
            assets["status"] == "PASS_T95_FILM_CONDITIONED_ASSETS"
            and assets["failed_checks"] == []
        ),
        "step_zero_source_bit_exact": assets["checks"][
            "step_zero_source_action_and_state_bit_exact"
        ],
        "film_zero_initialized": assets["checks"][
            "context_parameters_exact_zero"
        ],
        "source_action_head_full_rank": action_head["rank"] == 14,
        "negative_com_contexts_unique": observability[
            "negative_com_contexts_are_unique"
        ],
        "prior_additive_context_closed": (
            t11["status"] == "HOLD_T11_CONTEXT_ACTION_OBSERVABILITY"
            and t11["decision"]
            == "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
        ),
        "adapter_authority_not_hard_limited": (
            t93["classification"]
            == "NO_HARD_ADAPTER_AUTHORITY_LIMIT_FOUND"
        ),
        "discrete_router_closed": (
            correction["decision"]
            == "CLOSE_CALIBRATION_ROUTED_EXPERT_MECHANISM"
        ),
        "cpu_only_no_behavior_or_hardware": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t95_film_cpu_preregistration.v1",
        "status": (
            "PREREGISTERED_T95_FILM_CONDITIONED_CPU_CONTRACT"
            if not failed
            else "HOLD_T95_FILM_CONDITIONED_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can a zero-initialized bilinear calibration/state FiLM path "
            "bind the automatically measured negative-COM response to a "
            "material action change while preserving the protected source, "
            "recurrent state, deployment hierarchy, and x=0 exactly?"
        ),
        "causal_basis": {
            "t91_negative_com": (
                "All 12 moving cells fell under exact TORSO_COM_X_NEG; x=0 "
                "remained 4/4 green."
            ),
            "t93": t93["classification"],
            "t94": correction["classification"],
            "t11_baseline_action_effect_fraction": t11[
                "disjoint_state_coherent_test"
            ]["effective_case_fraction"],
            "selected_distinction": (
                "T10/T11 added context-dependent hidden and action biases. "
                "T95 instead makes the action feedback gain bilinear in the "
                "live recurrent feature and immutable calibration context; "
                "it neither selects an expert nor adds a static pose offset."
            ),
        },
        "sources": sources,
        "assets": {
            "expanded_checkpoint": assets["assets"][
                "expanded_checkpoint"
            ],
            "step_zero_onnx": assets["assets"]["step_zero_onnx"],
            "calibrator": assets["sources"]["calibrator"],
        },
        "software_contract": {
            "timesteps": 1024,
            "backend": "CPU only",
            "source": "T78 joint-adapter half checkpoint",
            "actor_updates": "context_film_scale/kernel only",
            "critic_updates": "allowed",
            "exports": [0, 1024],
            "deployment_abi": "115 observations, 14 actions, 64 hidden, 64 calibration context",
            "x0": "exact deadband zero",
        },
        "architecture_contract": {
            "equation": (
                "h= tanh(Wo*obs + Wh*h_prev + b); "
                "h_film=h + h*(context*Wfilm); "
                "adapter=Waction*h_film+baction"
            ),
            "new_actor_parameters": ["context_film_scale/kernel"],
            "new_parameter_initialization": "exact zero",
            "source_action_head_shape": action_head["shape"],
            "source_action_head_rank": action_head["rank"],
            "source_action_head_frobenius_norm": action_head[
                "frobenius_norm"
            ],
            "recurrent_state_semantics": "h_out remains pre-FiLM and exact",
            "deployment_order": (
                "raw actor -> trained rate -> actual-centered guard -> "
                "x=0 deadband -> final rate -> restored x=0 deadband"
            ),
        },
        "cpu_smoke": {
            "contexts": "all 40 frozen T94 R2 calibration vectors",
            "ticks_per_context": 64,
            "effect_threshold_abs": 1e-8,
            "material_maximum_action_delta": 1e-5,
            "minimum_action_effect_tick_fraction": 0.05,
            "minimum_context_pair_effect_fraction": 0.50,
            "derivation": (
                "The 5% tick threshold is more than ten times T11's "
                "0.439453125% coherent additive-context effect; both exact "
                "negative-COM contexts must independently affect action."
            ),
            "maximum_wall_seconds": 3600,
            "formal_behavior_cells": 0,
        },
        "decision_rule": {
            "pass": (
                "Every contract check passes, only the FiLM actor leaf and "
                "critic update, both negative-COM contexts affect action, "
                "at least 5% of ticks and half of contexts affect action, "
                "and x=0/rate/state/export contracts remain exact."
            ),
            "pass_next_action": (
                "Earn only a separate preregistration for one hosted "
                "FiLM-only continuation; do not launch it from this result."
            ),
            "fail": (
                "Close the FiLM-conditioned continuation without hosted "
                "training and file the observed gradient/action-binding "
                "failure."
            ),
        },
        "authority": {
            "cpu_smoke": not failed,
            "hosted_preregistration_after_pass": not failed,
            "hosted_training": False,
            "behavior_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "context_observability": observability,
    }
    value = {
        **basis,
        "failed_checks": failed,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T95 calibration-FiLM CPU preregistration",
                "",
                f"Status: `{value['status']}`",
                "",
                "T95 tests one distinct mechanism: continuous calibration-"
                "dependent gain scheduling of the live recurrent feedback "
                "features. It does not route experts, add a static pose "
                "offset, or mutate the recurrent state.",
                "",
                f"- Unique calibration contexts: "
                f"**{observability['unique_contexts']}/40**",
                "- Exact collisions are explicitly retained as a limitation.",
                "- Negative-X COM remains uniquely observable in both fits.",
                "- Source adapter action head rank: **14/14**",
                "- New actor leaves: **one zero-initialized kernel**",
                "- Hosted compute, behavior cells, and hardware: **0**",
                "",
                "A green CPU result earns only a separate hosted-run "
                "preregistration. No Colab run is authorized here.",
                "",
                f"Contract SHA-256: "
                f"`{value['preregistered_contract_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
