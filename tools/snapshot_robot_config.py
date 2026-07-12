#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path


def timestamp_slug():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_path(path):
    path = Path(path).expanduser()
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    path = Path(path).expanduser()
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def package_version(name):
    try:
        from importlib.metadata import version

        return version(name)
    except Exception:
        return None


def package_versions_from_python(python_bin, package_names):
    python_bin = Path(python_bin).expanduser()
    if not python_bin.exists():
        return None
    code = """
import importlib.metadata as m
import json
import sys
names = sys.argv[1:]
out = {}
for name in names:
    try:
        out[name] = m.version(name)
    except Exception:
        out[name] = None
print(json.dumps(out, sort_keys=True))
"""
    try:
        proc = subprocess.run(
            [str(python_bin), "-c", code, *package_names],
            text=True,
            capture_output=True,
            timeout=5,
        )
        if proc.returncode != 0:
            return {"error": proc.stderr.strip() or proc.stdout.strip()}
        return json.loads(proc.stdout)
    except Exception as exc:
        return {"error": repr(exc)}


def git_commit(path):
    path = Path(path).expanduser()
    if not path.exists():
        return None


def git_dirty(path):
    path = Path(path).expanduser()
    if not path.exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            text=True,
            capture_output=True,
            timeout=2,
        )
        if proc.returncode != 0:
            return None
        return bool(proc.stdout.strip())
    except Exception:
        return None


def file_record(path):
    path = Path(path).expanduser()
    return {
        "path": str(path),
        "present": path.is_file(),
        "sha256": sha256_path(path),
    }


def policy_inventory(home, runtime_path):
    candidates = set(Path(home).glob("*.onnx"))
    if runtime_path:
        runtime = Path(runtime_path)
        candidates.update(runtime.glob("*.onnx"))
        candidates.update((runtime / "policies").glob("*.onnx"))
    return [file_record(path) for path in sorted(candidates, key=lambda p: str(p))]
    try:
        return (
            subprocess.check_output(
                ["git", "-C", str(path), "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2,
            )
            .strip()
        )
    except Exception:
        return None


def find_first_existing(paths):
    for path in paths:
        p = Path(path).expanduser()
        if p.exists():
            return str(p)
    return None


def local_snapshot(config_path="~/duck_config.json"):
    home = Path.home()
    runtime_path = find_first_existing(
        [
            home / "project" / "Open_Duck_Mini_Runtime-2_RDK_X5",
            home / "Open_Duck_Mini_Runtime",
            home / "robots" / "Open_Duck_Mini_Runtime",
            Path.cwd() / "Open_Duck_Mini_Runtime",
            Path.cwd(),
        ]
    )
    python_env_path = find_first_existing([home / "duck_env" / "bin" / "python"])
    imu_calib = find_first_existing(
        [
            Path.cwd() / "imu_calib_data.pkl",
            home / "imu_calib_data.pkl",
            home / "Open_Duck_Mini_Runtime" / "scripts" / "imu_calib_data.pkl",
            home
            / "project"
            / "Open_Duck_Mini_Runtime-2_RDK_X5"
            / "scripts"
            / "imu_calib_data.pkl",
        ]
    )
    onnx_policy_path = find_first_existing(
        [
            home / "BEST_WALK_ONNX_2.onnx",
            Path.cwd() / "BEST_WALK_ONNX_2.onnx",
            Path.cwd() / "Open_Duck_Mini" / "BEST_WALK_ONNX_2.onnx",
        ]
    )
    duck_config = read_json(config_path)
    package_names = [
        "onnxruntime",
        "onnx",
        "adafruit-circuitpython-bno055",
        "adafruit_bno055",
        "rustypot",
        "pypot",
        "numpy",
        "pygame",
        "scipy",
    ]
    instrumentation_paths = []
    if runtime_path:
        runtime = Path(runtime_path)
        instrumentation_paths = [
            runtime / "mini_bdx_runtime" / "mini_bdx_runtime" / "telemetry.py",
            runtime / "scripts" / "sim2real_diagnostics.py",
            runtime / "scripts" / "v2_rl_walk_auto.py",
        ]
    return {
        "schema_version": "open_duck_mini_config_snapshot_v2",
        "snapshot_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version,
        "cwd": str(Path.cwd()),
        "duck_config_path": str(Path(config_path).expanduser()),
        "duck_config_sha256": sha256_path(config_path),
        "duck_config": duck_config,
        "imu_upside_down": None if duck_config is None else duck_config.get("imu_upside_down"),
        "joints_offsets": None if duck_config is None else duck_config.get("joints_offsets"),
        "phase_frequency_factor_offset": None
        if duck_config is None
        else duck_config.get("phase_frequency_factor_offset"),
        "imu_calib_data_path": imu_calib,
        "imu_calib_data_sha256": None if imu_calib is None else sha256_path(imu_calib),
        "onnx_policy_path": onnx_policy_path,
        "onnx_policy_sha256": None
        if onnx_policy_path is None
        else sha256_path(onnx_policy_path),
        "runtime_path": runtime_path,
        "runtime_git_commit": None if runtime_path is None else git_commit(runtime_path),
        "runtime_git_dirty": None if runtime_path is None else git_dirty(runtime_path),
        "runtime_instrumentation": [file_record(path) for path in instrumentation_paths],
        "onnx_policy_inventory": policy_inventory(home, runtime_path),
        "python_env_path": python_env_path,
        "packages": {
            name: package_version(name) for name in package_names
        },
        "python_env_packages": None
        if python_env_path is None
        else package_versions_from_python(python_env_path, package_names),
    }


def ssh_snapshot(
    target,
    config_path="~/duck_config.json",
    connect_timeout=5,
    temp_known_hosts=False,
    identity_file=None,
    known_hosts=None,
    strict_host_key_checking=None,
):
    collector_utc = dt.datetime.now(dt.timezone.utc)
    encoded = base64.b64encode(Path(__file__).read_bytes()).decode("ascii")
    remote_code = f"""
import base64
import json
namespace = {{'__name__': 'snapshot_robot_config_inline'}}
exec(compile(base64.b64decode('{encoded}'), '<snapshot_robot_config_inline>', 'exec'), namespace)
print(json.dumps(namespace['local_snapshot']({config_path!r}), sort_keys=True))
"""
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
    ]
    if identity_file:
        cmd += ["-i", os.path.expanduser(identity_file)]
    if known_hosts:
        cmd += ["-o", f"UserKnownHostsFile={os.path.expanduser(known_hosts)}"]
    if strict_host_key_checking:
        cmd += ["-o", f"StrictHostKeyChecking={strict_host_key_checking}"]
    if temp_known_hosts:
        cmd += [
            "-o",
            "UserKnownHostsFile=/tmp/open_duck_known_hosts",
            "-o",
            "StrictHostKeyChecking=accept-new",
        ]
    cmd += [target, "python3", "-"]
    proc = subprocess.run(
        cmd,
        input=remote_code,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    snapshot = json.loads(proc.stdout.strip().splitlines()[-1])
    snapshot["collector_utc"] = collector_utc.isoformat()
    snapshot["snapshot_utc_source"] = "remote_system_clock"
    try:
        remote_utc = dt.datetime.fromisoformat(snapshot["snapshot_utc"].replace("Z", "+00:00"))
        snapshot["remote_clock_offset_from_collector_s"] = (
            remote_utc - collector_utc
        ).total_seconds()
        snapshot["remote_clock_plausible"] = abs(
            snapshot["remote_clock_offset_from_collector_s"]
        ) <= 300
    except Exception:
        snapshot["remote_clock_offset_from_collector_s"] = None
        snapshot["remote_clock_plausible"] = False
    return snapshot


def main():
    parser = argparse.ArgumentParser(description="Snapshot Open Duck live config evidence.")
    parser.add_argument("--ssh", default=None, help="Optional SSH target, e.g. sunrise@192.168.1.50")
    parser.add_argument("--connect-timeout", type=int, default=5)
    parser.add_argument("--identity-file", default=None, help="SSH private key path.")
    parser.add_argument("--known-hosts", default=None, help="SSH known_hosts path.")
    parser.add_argument(
        "--strict-host-key-checking",
        default=None,
        choices=["yes", "no", "accept-new"],
        help="SSH StrictHostKeyChecking value.",
    )
    parser.add_argument(
        "--ssh-temp-known-hosts",
        action="store_true",
        help="Use /tmp/open_duck_known_hosts instead of the user's SSH known_hosts file.",
    )
    parser.add_argument("--config-path", default="~/duck_config.json")
    parser.add_argument(
        "--output-dir",
        default="outputs/evidence",
        help="Directory for *_rdkx5_config_snapshot.json",
    )
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    if args.ssh:
        snapshot = ssh_snapshot(
            args.ssh,
            config_path=args.config_path,
            connect_timeout=args.connect_timeout,
            temp_known_hosts=args.ssh_temp_known_hosts,
            identity_file=args.identity_file,
            known_hosts=args.known_hosts,
            strict_host_key_checking=args.strict_host_key_checking,
        )
        snapshot["ssh_target"] = args.ssh
    else:
        snapshot = local_snapshot(args.config_path)

    if args.print_only:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
        return

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{timestamp_slug()}_rdkx5_config_snapshot.json"
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)
        f.write("\n")
    print(out_path)


if __name__ == "__main__":
    main()
