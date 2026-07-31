#!/usr/bin/env python3
"""Build one hashed, envelope-projected reference table for training and RDK."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import io
import zipfile
from pathlib import Path

import numpy as np

HOME = np.array([.002,.053,-.630,1.368,-.784,0,0,0,0,-.003,-.065,.635,1.379,-.796])
LIMITS = np.array([5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25])
ACTION_SCALE = 0.25
DT = 0.02


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reference", required=True)
    p.add_argument("--output-npz", required=True)
    p.add_argument("--output-json", required=True)
    args = p.parse_args()
    source = Path(args.reference)
    raw = pickle.loads(source.read_bytes())
    keys = sorted(raw, key=lambda k: tuple(float(v) for v in k.split("_")))
    first = raw[keys[0]]
    steps = int(first["period"] * first["fps"])
    commands, tables, scales = [], [], []
    for key in keys:
        command = np.array([float(v) for v in key.split("_")])
        coeffs = [np.flip(np.asarray(v, dtype=float)) for v in raw[key]["coefficients"].values()]
        frames = np.stack([[np.polyval(c, i / steps) for c in coeffs] for i in range(steps)])
        targets = np.tile(HOME, (steps, 1))
        targets[:, :5] = frames[:, :5]
        targets[:, 9:14] = frames[:, 11:16]
        delta = targets - HOME
        velocity = np.abs(np.diff(np.vstack([targets, targets[:1]]), axis=0) / DT)
        max_delta, max_velocity = np.max(np.abs(delta), axis=0), np.max(velocity, axis=0)
        scale = np.ones(14)
        np.minimum(scale, np.divide(ACTION_SCALE, max_delta, out=np.ones(14), where=max_delta>1e-12), out=scale)
        np.minimum(scale, np.divide(LIMITS, max_velocity, out=np.ones(14), where=max_velocity>1e-12), out=scale)
        actions = delta * np.clip(scale, 0, 1) / ACTION_SCALE
        commands.append(command); tables.append(actions); scales.append(scale)
    commands = np.asarray(commands); table = np.asarray(tables); scales = np.asarray(scales)
    rate = np.abs(np.diff(np.concatenate([table, table[:, :1]], axis=1), axis=1) * ACTION_SCALE / DT)
    if np.max(np.abs(table)) > 1 + 1e-9 or np.any(np.max(rate, axis=(0,1)) > LIMITS + 1e-8):
        raise SystemExit("projected table violates action or velocity envelope")
    out = Path(args.output_npz); out.parent.mkdir(parents=True, exist_ok=True)
    write_deterministic_npz(out, {
        "commands": commands.astype(np.float32), "actions": table.astype(np.float32),
        "projection_scales": scales.astype(np.float32), "home_rad": HOME.astype(np.float32),
        "velocity_limits_rad_s": LIMITS.astype(np.float32),
        "action_scale_rad": np.array(ACTION_SCALE, dtype=np.float32),
        "dt_s": np.array(DT, dtype=np.float32),
    })
    report = {"status":"PASS_PROJECTED_REFERENCE_FEATURE_TABLE","source":str(source),
              "source_sha256":sha256(source),"output_npz":str(out),"output_sha256":sha256(out),
              "command_cells":len(commands),"phase_steps":steps,"shape":list(table.shape),
              "max_abs_action":float(np.max(np.abs(table))),
              "max_rate_by_joint_rad_s":np.max(rate,axis=(0,1)).tolist(),
              "velocity_limits_rad_s":LIMITS.tolist(),"zero_command_override":"all-zero feature"}
    Path(args.output_json).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
