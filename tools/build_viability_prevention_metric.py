#!/usr/bin/env python3
"""Build the frozen B1 viability-neighborhood metric from committed states."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = ROOT / "outputs/analysis/oracle_com_viability_funnel_states"
OUTPUT = ROOT / "outputs/analysis/viability_prevention_metric.json"
OUTPUT_MD = ROOT / "outputs/analysis/VIABILITY_PREVENTION_METRIC_RESULT_20260716.md"
DOF_INDICES = (6, 8, 10, 12, 14, 16, 17, 18, 19, 20, 22, 24, 26, 28)
VELOCITY_SCALES = np.asarray(
    [5.24, 5.24, 1.50, 1.50, 1.50, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25],
    dtype=float,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def quat_roll_pitch(q: list[float]) -> tuple[float, float]:
    w, x, y, z = (float(value) for value in q)
    sinr = 2.0 * (w * x + y * z)
    cosr = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)
    sinp = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
    return roll, math.asin(sinp)


def vector(payload: dict) -> np.ndarray:
    qpos = payload["qpos"]
    qvel = payload["qvel"]
    roll, pitch = quat_roll_pitch(qpos[3:7])
    contacts = (payload.get("oracle_state") or {}).get("contacts")
    if contacts is None:
        raise ValueError("frozen state missing oracle_state.contacts")
    raw = np.asarray(
        [
            *payload["actual_position_rad"],
            *(qvel[index] for index in DOF_INDICES),
            roll,
            pitch,
            qpos[2],
            *contacts,
        ],
        dtype=float,
    )
    scales = np.asarray([*([0.25] * 14), *VELOCITY_SCALES, 0.20, 0.20, 0.05, 1.0, 1.0])
    if raw.shape != (33,) or scales.shape != (33,):
        raise ValueError(f"metric shape mismatch: {raw.shape} {scales.shape}")
    return raw / scales


def distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(left - right))))


def main() -> int:
    paths = sorted(STATE_ROOT.glob("*.json"))
    if len(paths) != 298:
        raise ValueError(f"expected 298 frozen states, found {len(paths)}")
    rows = []
    for path in paths:
        payload = json.loads(path.read_text())
        rows.append({
            "path": str(path), "sha256": sha256(path), "payload": payload,
            "vector": vector(payload),
            "group": (payload["condition"], payload["policy"], payload["fit"], float(payload["command_x"])),
            "tick": int(payload["tick"]),
        })
    nearest_temporal = []
    for row in rows:
        candidates = [other for other in rows if other["group"] == row["group"] and other["tick"] != row["tick"]]
        if not candidates:
            raise ValueError(f"state has no temporal neighbor: {row['path']}")
        nearest_temporal.append(min(distance(row["vector"], other["vector"]) for other in candidates))
    radius = float(np.percentile(np.asarray(nearest_temporal, dtype=float), 95))
    state_listing = "".join(f"{row['sha256']}  {Path(row['path']).name}\n" for row in rows)
    payload = {
        "schema_version": "viability_prevention_metric.v1",
        "status": "PASS_VIABILITY_PREVENTION_METRIC_FROZEN",
        "dimensions": [
            "14_actual_joint_positions", "14_actuated_joint_velocities",
            "base_roll", "base_pitch", "base_height", "left_contact", "right_contact",
        ],
        "dimension_count": 33,
        "dof_indices": list(DOF_INDICES),
        "normalization": {
            "joint_position_rad": 0.25,
            "joint_velocity_rad_s": VELOCITY_SCALES.tolist(),
            "roll_rad": 0.20, "pitch_rad": 0.20, "height_m": 0.05,
            "contacts": 1.0,
        },
        "distance": "root_mean_square_of_normalized_dimension_deltas",
        "radius_rule": "95th_percentile_of_each_frozen_state_nearest_different_tick_neighbor_within_same_condition_policy_fit_command_trajectory",
        "radius": radius,
        "nearest_temporal_distance": {
            "minimum": float(np.min(nearest_temporal)),
            "median": float(np.median(nearest_temporal)),
            "p95": radius,
            "maximum": float(np.max(nearest_temporal)),
        },
        "sign_weights": {"X_NEG": 3.0, "X_POS": 1.0},
        "sign_weight_basis": "inverse_frozen_recovery_window_ratio_12_ticks_over_4_ticks",
        "states": [
            {
                "path": row["path"], "sha256": row["sha256"],
                "condition": row["payload"]["condition"], "policy": row["payload"]["policy"],
                "fit": row["payload"]["fit"], "command_x": row["payload"]["command_x"],
                "tick": row["tick"], "normalized_vector": row["vector"].tolist(),
            }
            for row in rows
        ],
        "state_count": len(rows),
        "state_sha256_listing_sha256": hashlib.sha256(state_listing.encode()).hexdigest(),
        "source_hashes": {
            "tool": sha256(Path(__file__)),
            "preregistration_json": sha256(ROOT / "outputs/analysis/viability_prevention_metric_preregistration.json"),
            "preregistration_md": sha256(ROOT / "outputs/analysis/VIABILITY_PREVENTION_METRIC_PREREGISTRATION_20260716.md"),
        },
        "execution": {"cpu_only": True, "simulator": False, "training": False, "hosted": False, "robot_or_rdk": False, "gpu_or_igpu": False},
        "robot_clearance": "NO",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    OUTPUT_MD.write_text(
        "# Viability Prevention Metric Result\n\n"
        f"status: `{payload['status']}`\n\n"
        f"Frozen states: {len(rows)}. Dimension count: 33. Radius: `{radius:.12f}`.\n\n"
        "The radius was derived only from within-trajectory four-tick failure-state spacing; no comparator replay was read. "
        "X_NEG proximity is priced at 3x X_POS. CPU-only read-only analysis; robot clearance remains `NO`.\n"
    )
    print(json.dumps({"status": payload["status"], "states": len(rows), "radius": radius}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
