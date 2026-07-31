#!/usr/bin/env python3
"""Run the frozen one-configuration Winner-v78 teacher extension on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v25_directional_support_control_diagnostic as v25  # noqa: E402
import run_winner_v34_prefix_right_pitch_hard_intervention as v34  # noqa: E402
import run_winner_v41_static_equilibrium_target_feasibility as v41  # noqa: E402
import run_winner_v41_v2_static_equilibrium_target_feasibility as v41_v2  # noqa: E402
import run_winner_v42_static_target_teacher_table as v42  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v78_missing_teacher_extension_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
CONFIGURATION_ID = "COM_CORNER_07"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
TARGETS = 729
TICKS = 250


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v78.missing_teacher_extension_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V78_MISSING_TEACHER_EXTENSION"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_COM_CORNER_07_TEACHER_TABLE"
        or value.get("screen")
        != {
            "configuration_ids": [CONFIGURATION_ID],
            "actuator_plants": list(PLANTS),
            "grid_values": list(v41.GRID_VALUES),
            "targets_per_configuration": TARGETS,
            "maximum_candidate_plant_cells": TARGETS * len(PLANTS),
            "duration_ticks": TICKS,
            "selection": "unchanged Winner-v41 deterministic shared-target key",
            "target_semantics": "one selected time-invariant target for COM_CORNER_07",
        }
        or value.get("execution_now")
        != {
            "configuration_tables": 0,
            "static_target_candidates": 0,
            "candidate_plant_cells": 0,
            "selected_target_replay_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v78 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v78 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v78 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v78 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--missing-teacher-extension-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.missing_teacher_extension_authorized:
        raise PermissionError(
            "Winner-v78 requires --offline-cpu-only "
            "--missing-teacher-extension-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v78 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v78 summary: {markdown}")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v78 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if tuple(smoke.PLANTS) != PLANTS or v41.TICKS != TICKS:
        raise ValueError("Winner-v78 inherited plant or duration changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v78 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v78 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )
    configuration = configurations[CONFIGURATION_ID]
    grid = v41.candidate_coordinates()
    if len(grid) != TARGETS:
        raise ValueError("Winner-v78 inherited target grid changed")
    v41.v38.expand_mirrored_blocks = v41_v2.expand_static_target

    episodes: dict[str, Any] = {}
    initial_snapshots: dict[str, Mapping[str, Any]] = {}
    for plant in PLANTS:
        episode = smoke.Episode(
            mujoco,
            scene,
            configuration,
            plant,
            calibrator_design,
            observer_type,
            args.canonical_fit,
        )
        if episode.initial_contacts != (1, 1):
            raise ValueError("Winner-v78 cell does not start with both feet loaded")
        episodes[plant] = episode
        initial_snapshots[plant] = v25.capture_episode(mujoco, episode)

    candidates: list[dict[str, Any]] = []
    compact_candidates: list[dict[str, Any]] = []
    all_actions_bounded = True
    for candidate_index, coordinates in enumerate(grid):
        plant_results = [
            v41.evaluate_target(
                mujoco=mujoco,
                smoke=smoke,
                reviewed_gate=reviewed_gate,
                episode=episodes[plant],
                initial_snapshot=initial_snapshots[plant],
                coordinates=coordinates,
                include_trace=False,
            )
            for plant in PLANTS
        ]
        all_actions_bounded &= all(item["all_actions_bounded"] for item in plant_results)
        row = {
            "candidate_index": candidate_index,
            "coordinates": coordinates.astype(float).tolist(),
            "coordinates_sha256": smoke.array_sha256(coordinates),
            "plant_results": plant_results,
            "shared_support_pass": all(item["support_pass"] for item in plant_results),
        }
        candidates.append(row)
        compact_candidates.append(
            {
                "candidate_index": candidate_index,
                "coordinates_sha256": row["coordinates_sha256"],
                "shared_support_pass": row["shared_support_pass"],
                "plant_results": [v42.compact_plant_result(item) for item in plant_results],
            }
        )

    passing = [row for row in candidates if row["shared_support_pass"]]
    selected = max(passing if passing else candidates, key=v41.candidate_key)
    selected_coordinates = np.asarray(selected["coordinates"], dtype=np.float32)
    replay_results = [
        v41.evaluate_target(
            mujoco=mujoco,
            smoke=smoke,
            reviewed_gate=reviewed_gate,
            episode=episodes[plant],
            initial_snapshot=initial_snapshots[plant],
            coordinates=selected_coordinates,
            include_trace=True,
        )
        for plant in PLANTS
    ]
    replay_exact = all(
        {name: replay[name] for name in original} == original
        for original, replay in zip(selected["plant_results"], replay_results)
    )
    validity_checks = {
        "exact_1_configuration_table": True,
        "exact_729_targets": len(candidates) == TARGETS,
        "exact_1458_candidate_plant_cells": sum(
            len(row["plant_results"]) for row in candidates
        )
        == TARGETS * len(PLANTS),
        "all_candidate_actions_graph_bounded": bool(all_actions_bounded),
        "selected_target_replay_exact": bool(replay_exact),
    }
    efficacy_checks = {
        "configuration_has_a_shared_two_plant_support_target": bool(passing),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V78_MISSING_TEACHER_EXTENSION"
        decision = "DO_NOT_RUN_RESIDUAL_TEACHER_DIAGNOSTIC"
    elif passed:
        status = "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
        decision = "AUTHORIZE_SEPARATELY_PREREGISTERED_RESIDUAL_TEACHER_DIAGNOSTIC_ONLY"
    else:
        status = "HOLD_WINNER_V78_MISSING_TEACHER_EXTENSION"
        decision = "CLOSE_FULL_NINE_PAIR_STATIC_TEACHER_DIAGNOSTIC"
    result = {
        "schema_version": "winner_v78.missing_teacher_extension_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "screen": preregistration["screen"],
        "configuration_result": {
            "configuration_id": CONFIGURATION_ID,
            "configuration_sha256": smoke.canonical_sha256(configuration),
            "candidate_receipts": compact_candidates,
            "shared_support_pass_count": len(passing),
            "per_plant_support_pass_counts": {
                plant: sum(
                    row["plant_results"][plant_index]["support_pass"] for row in candidates
                )
                for plant_index, plant in enumerate(PLANTS)
            },
            "selected_kind": (
                "shared_support_pass" if passing else "diagnostic_best_not_promoted"
            ),
            "selected_candidate_index": selected["candidate_index"],
            "selected_coordinates": selected["coordinates"],
            "selected_coordinates_sha256": selected["coordinates_sha256"],
            "selected_replay_exact": replay_exact,
            "selected_replay_results": replay_results,
        },
        "teacher_table_extension": {
            CONFIGURATION_ID: {
                "candidate_index": selected["candidate_index"],
                "coordinates": selected["coordinates"],
                "coordinates_sha256": selected["coordinates_sha256"],
                "shared_support_pass": bool(passing),
            }
        },
        "execution": {
            "configuration_tables": 1,
            "static_target_candidates": len(candidates),
            "candidate_plant_cells": sum(
                len(row["plant_results"]) for row in candidates
            ),
            "selected_target_replay_cells": len(PLANTS),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_sha256": sha256(PREREGISTRATION),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered residual-teacher causal diagnostic",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v78 missing-teacher extension result",
                "",
                f"- Status: `{status}`",
                f"- Shared two-plant targets: `{len(passing)}`",
                f"- Selected coordinates: `{selected['coordinates']}`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    print(f"SHARED_TARGETS={len(passing)}")
    print(f"SELECTED_COORDINATES={selected['coordinates']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
