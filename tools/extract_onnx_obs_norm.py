#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PKG = ROOT / "Open_Duck_Mini_Runtime" / "mini_bdx_runtime"
if RUNTIME_PKG.exists():
    sys.path.insert(0, str(RUNTIME_PKG))

from mini_bdx_runtime.telemetry import extract_onnx_obs_normalization, sha256_file


def summarize(values, n=6):
    return [round(float(v), 6) for v in values[:n]]


def main():
    parser = argparse.ArgumentParser(
        description="Extract embedded ONNX observation normalization constants."
    )
    parser.add_argument(
        "onnx_model_path",
        nargs="?",
        default="Open_Duck_Mini/BEST_WALK_ONNX_2.onnx",
    )
    parser.add_argument("--input-name", default="obs")
    parser.add_argument("--obs-size", type=int, default=101)
    parser.add_argument("--save-json", default=None)
    args = parser.parse_args()

    info = extract_onnx_obs_normalization(
        args.onnx_model_path, input_name=args.input_name, obs_size=args.obs_size
    )
    payload = {
        "onnx_path": os.path.expanduser(args.onnx_model_path),
        "onnx_sha256": sha256_file(args.onnx_model_path),
        "input_name": args.input_name,
        "obs_size": args.obs_size,
        **info,
    }

    if args.save_json:
        Path(args.save_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.save_json, "w") as f:
            json.dump(payload, f, indent=2)

    if info.get("error"):
        print("ERROR:", info["error"])
        return 1

    mean = info["mean"]
    std_recip = info["std_recip"]
    std = info["std"]
    print("ONNX:", payload["onnx_path"])
    print("SHA256:", payload["onnx_sha256"])
    print("source:", info["source"])
    print("mean length:", len(mean))
    print("std_recip length:", len(std_recip))
    print("first 6 means [gyro0:3 accel0:3]:", summarize(mean))
    print("first 6 std_recip:", summarize(std_recip))
    print("first 6 std:", summarize(std))
    print("")
    print("IMU z-score helper:")
    for i, label in enumerate(
        ["gyro_x", "gyro_y", "gyro_z", "accel_x", "accel_y", "accel_z"]
    ):
        print(
            f"  obs[{i}] {label}: z = (value - {mean[i]:.6f}) * {std_recip[i]:.6f}"
        )
    if args.save_json:
        print("saved:", args.save_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
