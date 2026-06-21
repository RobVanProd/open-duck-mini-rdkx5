#!/usr/bin/env python3
import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALKER = ROOT / "runtime" / "scripts" / "v2_rl_walk_mujoco.py"
SCHEMA = ROOT / "docs" / "telemetry_schema.json"

REQUIRED_INIT_ARGS = {
    "log_telemetry",
    "telemetry_path",
    "telemetry_read_voltage",
    "telemetry_every_n",
}
REQUIRED_CLI_FLAGS = {
    "--log-telemetry",
    "--telemetry-path",
    "--telemetry-read-voltage",
    "--telemetry-every-n",
}
REQUIRED_SCHEMA_PROPERTIES = {
    "schema_version",
    "tick",
    "timestamp_monotonic_s",
    "dt_s",
    "policy",
    "control",
    "imu",
    "joints",
    "observation",
    "action",
    "bus",
}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_walker_ast():
    if not WALKER.exists():
        fail(f"missing walker file: {WALKER}")
    return ast.parse(WALKER.read_text(), filename=str(WALKER))


def find_rlwalk_init(tree):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "RLWalk":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    return child
    fail("could not find RLWalk.__init__")


def init_arg_names(init_node):
    args = []
    args.extend(arg.arg for arg in init_node.args.posonlyargs)
    args.extend(arg.arg for arg in init_node.args.args)
    args.extend(arg.arg for arg in init_node.args.kwonlyargs)
    return set(args)


def add_argument_flags(tree):
    flags = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "add_argument":
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if arg.value.startswith("--"):
                    flags.add(arg.value)
    return flags


def check_schema():
    if not SCHEMA.exists():
        fail(f"missing telemetry schema: {SCHEMA}")
    with SCHEMA.open() as f:
        schema = json.load(f)
    if schema.get("type") != "object":
        fail("telemetry schema root type is not object")
    properties = set(schema.get("properties", {}))
    missing = sorted(REQUIRED_SCHEMA_PROPERTIES - properties)
    if missing:
        fail(f"telemetry schema missing properties: {', '.join(missing)}")
    required = set(schema.get("required", []))
    missing_required = sorted((REQUIRED_SCHEMA_PROPERTIES - {"bus"}) - required)
    if missing_required:
        fail(f"telemetry schema missing required keys: {', '.join(missing_required)}")
    print("OK: telemetry schema JSON parsed and required properties are present")


def main():
    tree = load_walker_ast()

    init_node = find_rlwalk_init(tree)
    init_args = init_arg_names(init_node)
    missing_init_args = sorted(REQUIRED_INIT_ARGS - init_args)
    if missing_init_args:
        fail(f"RLWalk.__init__ missing args: {', '.join(missing_init_args)}")
    print("OK: RLWalk.__init__ exposes telemetry args")

    flags = add_argument_flags(tree)
    missing_flags = sorted(REQUIRED_CLI_FLAGS - flags)
    if missing_flags:
        fail(f"v2_rl_walk_mujoco.py missing CLI flags: {', '.join(missing_flags)}")
    print("OK: v2_rl_walk_mujoco.py exposes telemetry CLI flags")

    check_schema()
    print("OK: runtime telemetry contract check passed")


if __name__ == "__main__":
    main()
