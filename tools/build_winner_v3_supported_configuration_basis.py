#!/usr/bin/env python3
"""Build the evidence-derived variable-configuration policy-domain basis."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
R2_PATH = ROOT / "outputs/analysis/ground_up_robustness_r2_matrix_preregistration.json"
BREAK_PATH = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
DEFAULT_JSON = ROOT / "outputs/analysis/winner_v3_supported_configuration_basis.json"
DEFAULT_MD = ROOT / "outputs/analysis/WINNER_V3_SUPPORTED_CONFIGURATION_BASIS_20260719.md"
SELECTED_ONNX_SHA256 = (
    "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def condition(r2: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [row for row in r2["conditions_in_strict_order"] if row["id"] == name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one R2 condition named {name}")
    return matches[0]["override"]


def geom_points(model: mujoco.MjModel, body_id: int) -> np.ndarray:
    points: list[np.ndarray] = []
    first = int(model.body_geomadr[body_id])
    count = int(model.body_geomnum[body_id])
    for geom_id in range(first, first + count):
        geom_type = int(model.geom_type[geom_id])
        position = np.asarray(model.geom_pos[geom_id], dtype=np.float64)
        rotation_flat = np.empty(9, dtype=np.float64)
        mujoco.mju_quat2Mat(rotation_flat, model.geom_quat[geom_id])
        rotation = rotation_flat.reshape(3, 3)
        if geom_type == int(mujoco.mjtGeom.mjGEOM_MESH):
            mesh_id = int(model.geom_dataid[geom_id])
            start = int(model.mesh_vertadr[mesh_id])
            length = int(model.mesh_vertnum[mesh_id])
            vertices = np.asarray(
                model.mesh_vert[start : start + length], dtype=np.float64
            )
            vertices = vertices * np.asarray(model.mesh_scale[mesh_id])
        elif geom_type == int(mujoco.mjtGeom.mjGEOM_BOX):
            size = np.asarray(model.geom_size[geom_id], dtype=np.float64)
            vertices = np.asarray(
                [
                    [x, y, z]
                    for x in (-size[0], size[0])
                    for y in (-size[1], size[1])
                    for z in (-size[2], size[2])
                ]
            )
        else:
            raise ValueError(
                f"unsupported torso geometry type {geom_type} at geom {geom_id}"
            )
        points.append(vertices @ rotation.T + position)
    if not points:
        raise ValueError("torso has no geometry")
    return np.concatenate(points, axis=0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--playground-root",
        type=Path,
        default=ROOT.parent / ".ground_up_playground_control",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()

    playground = args.playground_root.resolve()
    status = git(playground, "status", "--porcelain")
    if status:
        raise ValueError("playground source must be clean")
    playground_commit = git(playground, "rev-parse", "HEAD")
    origin = git(playground, "remote", "get-url", "origin")
    if origin != "https://github.com/apirrone/Open_Duck_Playground.git":
        raise ValueError(f"unexpected playground origin: {origin}")

    xml_path = (
        playground
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    randomizer_path = playground / "playground/common/randomize.py"
    model = mujoco.MjModel.from_xml_path(str(xml_path))
    torso_id = int(model.body("trunk_assembly").id)
    if torso_id != 2:
        raise ValueError(f"trunk_assembly body changed: {torso_id}")
    torso_mass = float(model.body_mass[torso_id])
    torso_ipos = np.asarray(model.body_ipos[torso_id], dtype=np.float64)
    torso_inertia = np.asarray(model.body_inertia[torso_id], dtype=np.float64)
    points = geom_points(model, torso_id)
    aabb_min = points.min(axis=0)
    aabb_max = points.max(axis=0)

    r2 = json.loads(R2_PATH.read_text(encoding="utf-8"))
    break_result = json.loads(BREAK_PATH.read_text(encoding="utf-8"))
    com_offsets = {
        "x": [
            float(condition(r2, "TORSO_COM_X_NEG")["torso_com_offset_m"][0]),
            float(condition(r2, "TORSO_COM_X_POS")["torso_com_offset_m"][0]),
        ],
        "y": [
            float(condition(r2, "TORSO_COM_Y_NEG")["torso_com_offset_m"][1]),
            float(condition(r2, "TORSO_COM_Y_POS")["torso_com_offset_m"][1]),
        ],
        "z": [
            float(condition(r2, "TORSO_COM_Z_NEG")["torso_com_offset_m"][2]),
            float(condition(r2, "TORSO_COM_Z_POS")["torso_com_offset_m"][2]),
        ],
    }
    all_mass_scale = [
        float(condition(r2, "ALL_LINK_MASS_LO")["all_link_mass_scale"]),
        float(condition(r2, "ALL_LINK_MASS_HI")["all_link_mass_scale"]),
    ]
    torso_mass_add = [
        float(condition(r2, "TORSO_MASS_NEG")["torso_mass_add_kg"]),
        float(condition(r2, "TORSO_MASS_POS")["torso_mass_add_kg"]),
    ]
    if com_offsets != {
        "x": [-0.05, 0.05],
        "y": [-0.05, 0.05],
        "z": [-0.05, 0.05],
    }:
        raise ValueError(f"unexpected frozen COM endpoints: {com_offsets}")
    if all_mass_scale != [0.9, 1.1] or torso_mass_add != [-0.1, 0.1]:
        raise ValueError("unexpected frozen mass endpoints")

    shifted_ipos = np.stack(
        [
            torso_ipos + np.asarray([x, y, z])
            for x in com_offsets["x"]
            for y in com_offsets["y"]
            for z in com_offsets["z"]
        ]
    )
    com_corners_inside_torso_aabb = bool(
        np.all(shifted_ipos >= aabb_min) and np.all(shifted_ipos <= aabb_max)
    )

    mass_range = [
        torso_mass * all_mass_scale[0] + torso_mass_add[0],
        torso_mass * all_mass_scale[1] + torso_mass_add[1],
    ]
    torso_mass_scale_range = [value / torso_mass for value in mass_range]
    radius = max(abs(com_offsets["x"][0]), abs(com_offsets["x"][1]))
    added_mass_abs = max(abs(torso_mass_add[0]), abs(torso_mass_add[1]))
    principal_allowance = added_mass_abs * (radius**2 + radius**2)
    product_allowance = added_mass_abs * radius**2
    inertia_component_bounds = np.stack(
        [
            torso_inertia * all_mass_scale[0] - principal_allowance,
            torso_inertia * all_mass_scale[1] + principal_allowance,
        ],
        axis=1,
    )
    inertia_scale_bounds = inertia_component_bounds / torso_inertia[:, None]
    inertia_lower_positive = bool(np.all(inertia_component_bounds[:, 0] > 0.0))
    nominal_inertia_triangle_valid = bool(
        np.max(torso_inertia) < np.sum(torso_inertia) - np.max(torso_inertia)
    )

    bounds = break_result["bounds"]
    current_candidate_fails_required_x_domain = bool(
        bounds["negative"]["observed_outer_fail_m"] > com_offsets["x"][0]
        and bounds["positive"]["observed_outer_fail_m"] < com_offsets["x"][1]
    )

    checks = {
        "cpu_only_model_readback": True,
        "playground_clean_official_origin": (
            not status
            and origin == "https://github.com/apirrone/Open_Duck_Playground.git"
        ),
        "compiled_torso_name_id_massive": torso_id == 2 and torso_mass > 0.0,
        "frozen_com_xyz_endpoints_exact": True,
        "frozen_mass_endpoints_exact": True,
        "all_com_corners_inside_compiled_torso_aabb": com_corners_inside_torso_aabb,
        "derived_inertia_lower_bounds_positive": inertia_lower_positive,
        "compiled_nominal_inertia_triangle_valid": nominal_inertia_triangle_valid,
        "derived_mass_and_inertia_scales_span_nominal": bool(
            torso_mass_scale_range[0] < 1.0 < torso_mass_scale_range[1]
            and np.all(inertia_scale_bounds[:, 0] < 1.0)
            and np.all(inertia_scale_bounds[:, 1] > 1.0)
        ),
        "optional_parts_use_aggregate_domain_not_manual_inventory": True,
        "current_candidate_fails_minimum_required_x_domain": (
            current_candidate_fails_required_x_domain
        ),
        "no_passing_runtime_envelope_emitted": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    decision = (
        "PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD"
        if not failed
        else "HOLD_VARIABLE_CONFIGURATION_DOMAIN_BASIS_INVALID"
    )

    result = {
        "schema_version": "winner_v3.supported_configuration_basis.v1",
        "status": decision,
        "decision": decision,
        "sources": {
            "playground_repository": "apirrone/Open_Duck_Playground",
            "playground_commit": playground_commit,
            "scene_xml": str(xml_path.relative_to(playground)),
            "scene_xml_sha256": sha256_file(xml_path),
            "randomizer": str(randomizer_path.relative_to(playground)),
            "randomizer_sha256": sha256_file(randomizer_path),
            "r2_preregistration": str(R2_PATH.relative_to(ROOT)),
            "r2_preregistration_sha256": sha256_file(R2_PATH),
            "break_radius_result": str(BREAK_PATH.relative_to(ROOT)),
            "break_radius_result_sha256": sha256_file(BREAK_PATH),
        },
        "compiled_torso": {
            "name": "trunk_assembly",
            "body_id": torso_id,
            "mass_kg": torso_mass,
            "ipos_m": torso_ipos.tolist(),
            "principal_inertia_kg_m2": torso_inertia.tolist(),
            "geometry_aabb_m": {
                "min": aabb_min.tolist(),
                "max": aabb_max.tolist(),
                "size": (aabb_max - aabb_min).tolist(),
            },
        },
        "frozen_continuous_domain": {
            "torso_com_offset_m": com_offsets,
            "all_link_mass_scale": all_mass_scale,
            "torso_mass_add_kg": torso_mass_add,
            "resulting_torso_mass_kg": mass_range,
            "resulting_torso_mass_scale": torso_mass_scale_range,
            "torso_inertia": {
                "base_density_scale": all_mass_scale,
                "principal_additive_allowance_abs_kg_m2": principal_allowance,
                "product_additive_allowance_abs_kg_m2": product_allowance,
                "principal_component_bounds_kg_m2": {
                    axis: inertia_component_bounds[index].tolist()
                    for index, axis in enumerate(("ixx", "iyy", "izz"))
                },
                "principal_scale_bounds": {
                    axis: inertia_scale_bounds[index].tolist()
                    for index, axis in enumerate(("xx", "yy", "zz"))
                },
                "sampling_rule": (
                    "sample coupled mass/COM/inertia cells; reconstruct the full "
                    "symmetric inertia tensor; accept only positive-definite tensors "
                    "whose principal moments satisfy triangle inequalities"
                ),
                "derivation": (
                    "frozen 0.9x/1.1x density scaling plus the parallel-axis upper "
                    "bound from 0.1 kg at two orthogonal 0.05 m radii"
                ),
            },
        },
        "optional_configuration_semantics": {
            "manual_component_inventory_required": False,
            "per_unit_mass_or_com_entry_required": False,
            "supported_if": (
                "the aggregate dynamics and later automatic response profile both "
                "remain inside the frozen continuous and observable-response domains"
            ),
            "discrete_eval_anchors": [
                "nominal",
                "mass_inertia_low",
                "mass_inertia_high",
                "com_x_neg",
                "com_x_pos",
                "com_y_neg",
                "com_y_pos",
                "com_z_neg",
                "com_z_pos",
                "eight_xyz_com_corners_with_coupled_mass_inertia",
            ],
        },
        "observable_response_contract": {
            "schema": "open_duck_x5.supported_configuration_envelope.v2",
            "clearance_schema": "open_duck_x5.policy_robot_clearance.v1",
            "clearance_status": "NOT_AUTHORIZED_CURRENT_CANDIDATE_HELD",
            "metric_count": 73,
            "bounds_status": "PENDING_PASSING_REPLACEMENT_SIM_EVIDENCE",
            "selection_rule": (
                "freeze derivation and held-out split before replacement outcomes; "
                "derive bounds from passing simulated configuration cells only; "
                "physical calibration cannot widen them"
            ),
        },
        "current_candidate": {
            "selected_onnx_sha256": SELECTED_ONNX_SHA256,
            "break_radius_bounds": bounds,
            "decision": "HOLD_POLICY_CONFIGURATION_SENSITIVITY_NO_PER_UNIT_MEASUREMENT",
            "eligible_for_supported_envelope": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "cpu_only": True,
            "preregister_replacement_study": not failed,
            "emit_passing_runtime_envelope": False,
            "training": False,
            "hosted_compute": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "gate5_or_deployment": False,
            "robot_clearance": False,
        },
    }
    args.output_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.output_md.write_text(
        f"""# Winner-v3 Supported-Configuration Domain Basis — 2026-07-19

Decision: `{decision}`

The supported domain is derived from the already-frozen R2 dynamics endpoints
and the compiled `trunk_assembly` readback, not from a per-unit measurement or
an invented component ledger. Torso COM spans `±0.05 m` independently in X, Y
and Z. All-link mass scale remains `0.9–1.1`; torso added mass remains
`±0.1 kg`, producing a torso-mass range of
`{mass_range[0]:.9f}–{mass_range[1]:.9f} kg`.

The compiled torso has mass `{torso_mass:.9f} kg`, inertial position
`{torso_ipos.tolist()}`, principal inertia `{torso_inertia.tolist()} kg·m²`,
and geometry AABB `{aabb_min.tolist()}–{aabb_max.tolist()} m`. Every frozen
COM corner stays inside that geometry. Inertia variation is coupled to the
frozen mass/placement ranges using the parallel-axis bound; only positive-
definite, triangle-valid inertia tensors may be sampled.

Optional non-locomotion combinations are represented by their aggregate
dynamics. No manual inventory, mass, COM or inertia entry is required. A build
is supportable only when both its aggregate configuration and later automatic
response profile remain inside the frozen envelopes.

The current `99d3afce…304de` graph cannot supply the runtime v2 envelope or a
policy-clearance artifact: its
verified X-COM bracket fails well inside the required `±0.05 m` domain. It
remains held and no `supported_configuration_envelope.v2` is emitted. The 73
automatic-response bounds remain pending a passing replacement and may not be
widened from physical outcomes.

This result authorizes only prospective replacement-study preregistration. It
does not authorize training, hosted compute, GPU/iGPU, RDK-X5, robot, automatic
calibration, X5 preflight, Gate 5, deployment or robot clearance.
""",
        encoding="utf-8",
    )
    print(decision)
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
