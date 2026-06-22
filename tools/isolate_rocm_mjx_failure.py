#!/usr/bin/env python3
"""Isolate ROCm/MJX closed-loop runtime failures with subprocess tests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform as platform_module
import re
import shlex
import subprocess
import sys
import textwrap
import time
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"
DEFAULT_POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
DEFAULT_FIT_JSON = ROOT / "outputs" / "analysis" / "actuator_response_fit.json"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "rocm_mjx_isolation"


VARIANT_ENVS = {
    "default": {},
    "preallocate_false": {"XLA_PYTHON_CLIENT_PREALLOCATE": "false"},
    "mem_fraction_050": {"XLA_PYTHON_CLIENT_MEM_FRACTION": "0.50"},
    "mem_fraction_060": {"XLA_PYTHON_CLIENT_MEM_FRACTION": "0.60"},
    "allocator_platform": {"XLA_PYTHON_CLIENT_ALLOCATOR": "platform"},
    "disable_jit": {"JAX_DISABLE_JIT": "true"},
    "debug_nans_infs": {"JAX_DEBUG_NANS": "true", "JAX_DEBUG_INFS": "true"},
    "tensor_parallel_one": {"TENSOR_PARALLEL_SIZE": "1"},
    "gfx1100_override": {
        "HSA_OVERRIDE_GFX_VERSION": "11.0.0",
        "TENSOR_PARALLEL_SIZE": "1",
    },
    "gfx1100_mem_safe": {
        "HSA_OVERRIDE_GFX_VERSION": "11.0.0",
        "TENSOR_PARALLEL_SIZE": "1",
        "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        "XLA_PYTHON_CLIENT_MEM_FRACTION": "0.60",
    },
    "miopen_fusion_disabled": {"MIOPEN_DEBUG_FUSION_ENGINE_DISABLE": "1"},
    "xla_disable_latency_scheduler": {
        "XLA_FLAGS": "--xla_gpu_enable_latency_hiding_scheduler=false"
    },
    "xla_disable_triton_gemm": {"XLA_FLAGS": "--xla_gpu_enable_triton_gemm=false"},
    "xla_disable_triton_gemm_softmax": {
        "XLA_FLAGS": (
            "--xla_gpu_enable_triton_gemm=false "
            "--xla_gpu_enable_triton_softmax=false"
        )
    },
    "xla_compiler_conservative": {
        "MIOPEN_DEBUG_FUSION_ENGINE_DISABLE": "1",
        "XLA_FLAGS": (
            "--xla_gpu_enable_latency_hiding_scheduler=false "
            "--xla_gpu_enable_triton_gemm=false"
        ),
    },
    "rocm_strict_ieee": {
        "ROCM_CHIP_COMPILER_FLAGS": "-fno-fast-math -fhonor-infinities -fhonor-nans"
    },
    "xla_rocm_data_dir": {"XLA_FLAGS": "--xla_gpu_target_cuda_data_dir=/opt/rocm/lib"},
    "xla_triton_strict_ieee": {
        "ROCM_CHIP_COMPILER_FLAGS": "-fno-fast-math -fhonor-infinities -fhonor-nans",
        "XLA_FLAGS": (
            "--xla_gpu_enable_triton_gemm=false "
            "--xla_gpu_enable_triton_softmax=false "
            "--xla_gpu_target_cuda_data_dir=/opt/rocm/lib"
        ),
    },
}


ROCM_ENV_KEYS = [
    "JAX_PLATFORM_NAME",
    "JAX_PLATFORMS",
    "JAX_DISABLE_JIT",
    "JAX_DEBUG_NANS",
    "JAX_DEBUG_INFS",
    "TENSOR_PARALLEL_SIZE",
    "XLA_PYTHON_CLIENT_PREALLOCATE",
    "XLA_PYTHON_CLIENT_MEM_FRACTION",
    "XLA_PYTHON_CLIENT_ALLOCATOR",
    "XLA_FLAGS",
    "MIOPEN_DEBUG_FUSION_ENGINE_DISABLE",
    "ROCM_CHIP_COMPILER_FLAGS",
    "HIP_VISIBLE_DEVICES",
    "ROCR_VISIBLE_DEVICES",
    "HSA_OVERRIDE_GFX_VERSION",
    "MUJOCO_GL",
]


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_steps(value: str) -> list[int]:
    output = []
    for item in split_csv(value):
        output.append(max(1, int(item)))
    return sorted(set(output))


def sanitize(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def command_exists(name: str) -> bool:
    return subprocess.run(
        ["bash", "-lc", f"command -v {shlex.quote(name)} >/dev/null"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def run_command(command: list[str], timeout_s: int = 10) -> dict:
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as exc:
        return {"command": command, "error": f"{type(exc).__name__}: {exc}"}


def host_info() -> dict:
    info = {
        "python": sys.version,
        "platform": platform_module.platform(),
        "kernel": platform_module.release(),
        "machine": platform_module.machine(),
        "env": {key: os.environ.get(key) for key in ROCM_ENV_KEYS if key in os.environ},
    }
    if command_exists("rocm-smi"):
        info["rocm_smi"] = run_command(["rocm-smi", "--showproductname"], timeout_s=10)
    if command_exists("rocminfo"):
        info["rocminfo"] = run_command(["bash", "-lc", "rocminfo | head -80"], timeout_s=10)
    if command_exists("uname"):
        info["uname"] = run_command(["uname", "-a"], timeout_s=5)
    cwsr_path = Path("/sys/module/amdgpu/parameters/cwsr_enable")
    if cwsr_path.exists():
        try:
            info["amdgpu_cwsr_enable"] = cwsr_path.read_text().strip()
        except OSError as exc:
            info["amdgpu_cwsr_enable_error"] = f"{type(exc).__name__}: {exc}"
    return info


def info_prologue(playground: Path) -> str:
    return f"""
import json
import os
import platform
import sys
from pathlib import Path

REPO_ROOT = {str(ROOT)!r}
TOOLS_PATH = str(Path(REPO_ROOT) / "tools")
PLAYGROUND_PATH = {str(playground)!r}
if TOOLS_PATH not in sys.path:
    sys.path.insert(0, TOOLS_PATH)
if PLAYGROUND_PATH not in sys.path:
    sys.path.insert(0, PLAYGROUND_PATH)

def emit(tag, payload):
    print(tag)
    print(json.dumps(payload, sort_keys=True, default=str))
    print(tag.replace("START", "END"))
    sys.stdout.flush()

def block_tree(value):
    import jax
    def block_item(item):
        return item.block_until_ready() if hasattr(item, "block_until_ready") else item
    return jax.tree_util.tree_map(block_item, value)

def emit_info(extra=None):
    info = {{
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "env": {{key: os.environ.get(key) for key in {ROCM_ENV_KEYS!r} if key in os.environ}},
    }}
    try:
        import jax
        info["jax_version"] = getattr(jax, "__version__", None)
        try:
            import jaxlib
            info["jaxlib_version"] = getattr(jaxlib, "__version__", None)
        except Exception as exc:
            info["jaxlib_error"] = f"{{type(exc).__name__}}: {{exc}}"
        info["jax_backend"] = jax.default_backend()
        info["jax_devices"] = [str(device) for device in jax.devices()]
    except Exception as exc:
        info["jax_error"] = f"{{type(exc).__name__}}: {{exc}}"
    try:
        import mujoco
        info["mujoco_version"] = getattr(mujoco, "__version__", None)
    except Exception as exc:
        info["mujoco_error"] = f"{{type(exc).__name__}}: {{exc}}"
    try:
        from mujoco import mjx
        info["mujoco_mjx_available"] = True
        info["mujoco_mjx_has_step"] = hasattr(mjx, "step")
    except Exception as exc:
        info["mujoco_mjx_error"] = f"{{type(exc).__name__}}: {{exc}}"
    try:
        import ml_collections
        info["ml_collections_version"] = getattr(ml_collections, "__version__", None)
    except Exception as exc:
        info["ml_collections_error"] = f"{{type(exc).__name__}}: {{exc}}"
    if extra:
        info.update(extra)
    emit("SUBTEST_INFO_JSON_START", info)
"""


def code_basic_jax(playground: Path) -> str:
    return info_prologue(playground) + """
emit_info({"subtest": "basic_jax"})
import jax
import jax.numpy as jnp
x = jnp.arange(2048, dtype=jnp.float32)
y = jnp.sin(x) * jnp.cos(x)
z = jnp.sum(y)
z.block_until_ready()
emit("SUBTEST_RESULT_JSON_START", {"status": "PASS", "value": float(z)})
"""


def code_jax_jit_scan(playground: Path, steps: Sequence[int]) -> str:
    return info_prologue(playground) + f"""
emit_info({{"subtest": "jax_jit_scan", "steps": {list(steps)!r}}})
import jax
import jax.numpy as jnp

def body(carry, _):
    carry = jnp.tanh(carry * 1.001 + 0.001)
    return carry, jnp.sum(carry)

out = {{}}
for n in {list(steps)!r}:
    fn = jax.jit(lambda x, n=n: jax.lax.scan(body, x, None, length=n))
    carry, ys = fn(jnp.ones((64,), dtype=jnp.float32))
    block_tree((carry, ys))
    out[str(n)] = float(jnp.sum(carry))
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": n, "status": "PASS"}})
emit("SUBTEST_RESULT_JSON_START", {{"status": "PASS", "steps": out}})
"""


def code_minimal_mjx(playground: Path, steps: Sequence[int]) -> str:
    return info_prologue(playground) + f"""
emit_info({{"subtest": "minimal_mjx_step", "steps": {list(steps)!r}}})
import jax
import jax.numpy as jnp
import mujoco
from mujoco import mjx

xml = '''
<mujoco>
  <option timestep="0.002"/>
  <worldbody>
    <body name="body" pos="0 0 0.2">
      <joint name="hinge" type="hinge" axis="0 1 0"/>
      <geom type="capsule" size="0.02 0.08" fromto="0 0 0 0 0 0.16"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="motor" joint="hinge" gear="1"/>
  </actuator>
</mujoco>
'''
model = mujoco.MjModel.from_xml_string(xml)
mx = mjx.put_model(model)
data = mjx.make_data(mx)
data = data.replace(ctrl=jnp.array([0.1], dtype=jnp.float32))
data = mjx.step(mx, data)
block_tree(data)
one = jax.jit(lambda d: mjx.step(mx, d))
data = one(data)
block_tree(data)

def body(carry, _):
    return mjx.step(mx, carry), None

out = {{}}
for n in {list(steps)!r}:
    scan_fn = jax.jit(lambda d, n=n: jax.lax.scan(body, d, None, length=n)[0])
    data = scan_fn(data)
    block_tree(data)
    out[str(n)] = float(data.qpos[0])
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": n, "status": "PASS"}})
emit("SUBTEST_RESULT_JSON_START", {{"status": "PASS", "steps": out}})
"""


def playground_common_code(playground: Path) -> str:
    return info_prologue(playground) + f"""
import os
from pathlib import Path
os.chdir({str(playground)!r})

def make_env():
    from playground.open_duck_mini_v2.joystick import Joystick
    return Joystick('flat_terrain', config_overrides={{
        'push_config.enable': False,
        'lin_vel_x': [0.08, 0.08],
        'lin_vel_y': [0.0, 0.0],
        'ang_vel_yaw': [0.0, 0.0],
        'neck_pitch_range': [0.0, 0.0],
        'head_pitch_range': [0.0, 0.0],
        'head_yaw_range': [0.0, 0.0],
        'head_roll_range': [0.0, 0.0],
        'noise_config.level': 0.0,
        'noise_config.action_min_delay': 0,
        'noise_config.action_max_delay': 1,
        'noise_config.imu_min_delay': 0,
        'noise_config.imu_max_delay': 1,
    }})
"""


def code_playground_xml_contact_audit(playground: Path) -> str:
    return info_prologue(playground) + f"""
emit_info({{"subtest": "playground_xml_contact_audit"}})
import json
from pathlib import Path
import xml.etree.ElementTree as ET

xml_dir = Path({str(playground)!r}) / "playground" / "open_duck_mini_v2" / "xmls"
files = sorted(xml_dir.glob("*.xml"))
rows = []
for path in files:
    root = ET.fromstring(path.read_text())
    for elem in root.iter():
        if elem.tag not in {{"default", "geom", "pair"}}:
            continue
        name = (
            elem.attrib.get("name")
            or elem.attrib.get("class")
            or elem.attrib.get("type")
            or ""
        )
        attrs = {{
            "file": str(path),
            "tag": elem.tag,
            "name": name,
            "type": elem.attrib.get("type"),
            "class": elem.attrib.get("class"),
            "contype": elem.attrib.get("contype"),
            "conaffinity": elem.attrib.get("conaffinity"),
            "condim": elem.attrib.get("condim"),
            "friction": elem.attrib.get("friction"),
            "solref": elem.attrib.get("solref"),
            "solimp": elem.attrib.get("solimp"),
        }}
        is_contact_relevant = (
            elem.tag == "pair"
            or attrs["contype"] not in (None, "0")
            or attrs["conaffinity"] not in (None, "0")
            or name in {{"floor", "left_foot_bottom_tpu", "right_foot_bottom_tpu"}}
            or attrs["condim"] is not None
        )
        if is_contact_relevant:
            rows.append(attrs)

missing_solref = [row for row in rows if row["solref"] is None]
missing_solimp = [row for row in rows if row["solimp"] is None]
emit("SUBTEST_RESULT_JSON_START", {{
    "status": "PASS",
    "xml_dir": str(xml_dir),
    "files": [str(path) for path in files],
    "contact_relevant_items": rows,
    "missing_solref_count": len(missing_solref),
    "missing_solimp_count": len(missing_solimp),
    "floor_items": [row for row in rows if row["name"] == "floor"],
    "foot_items": [
        row
        for row in rows
        if row["name"] in {{"left_foot_bottom_tpu", "right_foot_bottom_tpu"}}
    ],
}})
"""


def code_playground_contract(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_contract_only"})
env = make_env()
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "action_size": int(env.action_size),
    "mjcf": {"nu": int(env.mj_model.nu), "nq": int(env.mj_model.nq), "nv": int(env.mj_model.nv)},
    "actuator_names": list(env.actuator_names),
})
"""


def code_playground_reset(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_reset"})
import jax
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
block_tree(state.obs)
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "observation_size": {key: list(value.shape) for key, value in state.obs.items()},
    "action_size": int(env.action_size),
})
"""


def state_finite_report_code() -> str:
    return """
def finite_report(state):
    import jax
    import jax.numpy as jnp
    report = {}
    for name in ["qpos", "qvel", "qacc", "ctrl", "act", "qfrc_constraint"]:
        value = getattr(state.data, name, None)
        if value is None:
            continue
        arr = jax.device_get(value)
        item = {
            "shape": list(arr.shape),
            "size": int(arr.size),
            "finite": bool(jnp.all(jnp.isfinite(value))),
            "nan_count": int(jax.device_get(jnp.sum(jnp.isnan(value)))),
            "posinf_count": int(jax.device_get(jnp.sum(jnp.isposinf(value)))),
            "neginf_count": int(jax.device_get(jnp.sum(jnp.isneginf(value)))),
        }
        if arr.size:
            item["min"] = float(jax.device_get(jnp.nanmin(jnp.nan_to_num(value))))
            item["max"] = float(jax.device_get(jnp.nanmax(jnp.nan_to_num(value))))
        else:
            item["min"] = None
            item["max"] = None
        report[name] = item
    return report

def sanitize_state(state):
    import jax.numpy as jnp
    updates = {}
    for name in ["qpos", "qvel", "qacc", "ctrl", "act"]:
        value = getattr(state.data, name, None)
        if value is None:
            continue
        updates[name] = jnp.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)
    if updates:
        state = state.replace(data=state.data.replace(**updates))
    return state
"""


def code_playground_reset_state_finite(playground: Path) -> str:
    return playground_common_code(playground) + state_finite_report_code() + """
emit_info({"subtest": "playground_reset_state_finite"})
import jax
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
block_tree((state.obs, state.data.qpos, state.data.qvel, state.done))
report = finite_report(state)
emit("SUBTEST_RESULT_JSON_START", {"status": "PASS", "finite_report": report})
"""


def code_playground_direct_mjx_step(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_direct_mjx_step"})
import jax
from mujoco_playground._src import mjx_env
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
data = mjx_env.step(env.mjx_model, state.data, state.data.ctrl, env.n_substeps)
block_tree((data.qpos, data.qvel, data.ctrl))
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "qpos0": float(data.qpos[0]),
    "base_height": float(data.qpos[2]),
})
"""


def code_playground_direct_mjx_step_jit(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_direct_mjx_step_jit"})
import jax
from mujoco_playground._src import mjx_env
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
step_fn = jax.jit(lambda data, ctrl: mjx_env.step(env.mjx_model, data, ctrl, env.n_substeps))
data = step_fn(state.data, state.data.ctrl)
block_tree((data.qpos, data.qvel, data.ctrl))
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "qpos0": float(data.qpos[0]),
    "base_height": float(data.qpos[2]),
})
"""


def code_playground_one_step(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_one_step_vanilla"})
import jax
import jax.numpy as jnp
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
action = jnp.zeros(env.action_size)
state = env.step(state, action)
block_tree((state.obs, state.data.qpos, state.done))
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "done": bool(state.done),
    "qpos0": float(state.data.qpos[0]),
})
"""


def code_playground_one_step_jit(playground: Path) -> str:
    return playground_common_code(playground) + """
emit_info({"subtest": "playground_one_step_jit"})
import jax
import jax.numpy as jnp
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
action = jnp.zeros(env.action_size)
step_fn = jax.jit(lambda s, a: env.step(s, a))
state = step_fn(state, action)
block_tree((state.obs, state.data.qpos, state.done))
emit("SUBTEST_RESULT_JSON_START", {
    "status": "PASS",
    "done": bool(state.done),
    "qpos0": float(state.data.qpos[0]),
})
"""


def code_playground_multi_step(playground: Path, steps: Sequence[int]) -> str:
    return playground_common_code(playground) + f"""
emit_info({{"subtest": "playground_multi_step_vanilla", "steps": {list(steps)!r}}})
import jax
import jax.numpy as jnp
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
action = jnp.zeros(env.action_size)
target_steps = {list(steps)!r}
current = 0
out = {{}}
for target in target_steps:
    while current < target:
        state = env.step(state, action)
        current += 1
    block_tree((state.obs, state.data.qpos, state.done))
    out[str(target)] = {{"done": bool(state.done), "qpos0": float(state.data.qpos[0])}}
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": target, "status": "PASS"}})
emit("SUBTEST_RESULT_JSON_START", {{"status": "PASS", "steps": out}})
"""


def code_playground_scan_step(playground: Path, steps: Sequence[int]) -> str:
    return playground_common_code(playground) + f"""
emit_info({{"subtest": "playground_scan_step_vanilla", "steps": {list(steps)!r}}})
import jax
import jax.numpy as jnp
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
action = jnp.zeros(env.action_size)

def body(carry, _):
    next_state = env.step(carry, action)
    return next_state, {{
        "qpos0": next_state.data.qpos[0],
        "done": next_state.done,
    }}

out = {{}}
for n in {list(steps)!r}:
    scan_fn = jax.jit(lambda s, n=n: jax.lax.scan(body, s, None, length=n))
    state, traj = scan_fn(state)
    block_tree((state.obs, state.data.qpos, state.done, traj["qpos0"], traj["done"]))
    out[str(n)] = {{
        "done": bool(state.done),
        "qpos0": float(state.data.qpos[0]),
        "traj_samples": int(traj["qpos0"].shape[0]),
    }}
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": n, "status": "PASS"}})
emit("SUBTEST_RESULT_JSON_START", {{"status": "PASS", "steps": out}})
"""


def code_playground_scan_step_sanitized(playground: Path, steps: Sequence[int]) -> str:
    return playground_common_code(playground) + state_finite_report_code() + f"""
emit_info({{"subtest": "playground_scan_step_sanitized", "steps": {list(steps)!r}}})
import jax
import jax.numpy as jnp
env = make_env()
state = env.reset(jax.random.PRNGKey(0))
state = sanitize_state(state)
action = jnp.zeros(env.action_size)

def body(carry, _):
    next_state = sanitize_state(carry)
    next_state = env.step(next_state, action)
    next_state = sanitize_state(next_state)
    return next_state, {{
        "qpos0": next_state.data.qpos[0],
        "done": next_state.done,
    }}

out = {{}}
initial_report = finite_report(state)
for n in {list(steps)!r}:
    scan_fn = jax.jit(lambda s, n=n: jax.lax.scan(body, s, None, length=n))
    state, traj = scan_fn(state)
    block_tree((state.obs, state.data.qpos, state.done, traj["qpos0"], traj["done"]))
    out[str(n)] = {{
        "done": bool(state.done),
        "qpos0": float(state.data.qpos[0]),
        "traj_samples": int(traj["qpos0"].shape[0]),
        "finite_report": finite_report(state),
    }}
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": n, "status": "PASS"}})
emit("SUBTEST_RESULT_JSON_START", {{
    "status": "PASS",
    "initial_finite_report": initial_report,
    "steps": out,
}})
"""


def code_closed_loop(playground: Path, policy: Path, fit_json: Path, steps: Sequence[int], bridge_mode: str, command_x: float) -> str:
    return info_prologue(playground) + f"""
emit_info({{"subtest": "closed_loop_policy_eval", "steps": {list(steps)!r}, "bridge_mode": {bridge_mode!r}}})
import json
from pathlib import Path
from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim
fit = json.load(open({str(fit_json)!r}))
out = {{}}
for n in {list(steps)!r}:
    result = run_closed_loop_sim(ClosedLoopConfig(
        policy_path=Path({str(policy)!r}),
        fit=fit,
        playground_root=Path({str(playground)!r}),
        command_x={float(command_x)!r},
        duration_s=float(n) * 0.02,
        bridge_mode={bridge_mode!r},
    ))
    out[str(n)] = {{
        "status": result.get("status"),
        "modes": {{
            key: {{
                "samples": value.get("samples"),
                "termination_reason": value.get("termination_reason"),
                "pitch_chain_summary": value.get("pitch_chain_summary"),
            }}
            for key, value in (result.get("modes") or {{}}).items()
        }},
        "error": result.get("error"),
    }}
    emit("SUBTEST_PROGRESS_JSON_START", {{"steps": n, "status": result.get("status")}})
emit("SUBTEST_RESULT_JSON_START", {{"status": "PASS", "steps": out}})
"""


def build_subtests(args) -> list[dict]:
    steps = parse_steps(args.steps)
    subtests = []
    for platform_name in split_csv(args.platforms):
        subtests.extend(
            [
                {
                    "name": "basic_jax",
                    "platform": platform_name,
                    "code": code_basic_jax(args.playground_path),
                },
                {
                    "name": "jax_jit_scan",
                    "platform": platform_name,
                    "code": code_jax_jit_scan(args.playground_path, steps),
                },
                {
                    "name": "minimal_mjx_step",
                    "platform": platform_name,
                    "code": code_minimal_mjx(args.playground_path, steps),
                },
                {
                    "name": "playground_contract_only",
                    "platform": platform_name,
                    "code": code_playground_contract(args.playground_path),
                },
                {
                    "name": "playground_xml_contact_audit",
                    "platform": platform_name,
                    "code": code_playground_xml_contact_audit(args.playground_path),
                },
                {
                    "name": "playground_reset",
                    "platform": platform_name,
                    "code": code_playground_reset(args.playground_path),
                },
                {
                    "name": "playground_reset_state_finite",
                    "platform": platform_name,
                    "code": code_playground_reset_state_finite(args.playground_path),
                },
                {
                    "name": "playground_direct_mjx_step",
                    "platform": platform_name,
                    "code": code_playground_direct_mjx_step(args.playground_path),
                },
                {
                    "name": "playground_direct_mjx_step_jit",
                    "platform": platform_name,
                    "code": code_playground_direct_mjx_step_jit(args.playground_path),
                },
                {
                    "name": "playground_one_step_vanilla",
                    "platform": platform_name,
                    "code": code_playground_one_step(args.playground_path),
                },
                {
                    "name": "playground_one_step_jit",
                    "platform": platform_name,
                    "code": code_playground_one_step_jit(args.playground_path),
                },
                {
                    "name": "playground_multi_step_vanilla",
                    "platform": platform_name,
                    "code": code_playground_multi_step(args.playground_path, steps),
                },
                {
                    "name": "playground_scan_step_vanilla",
                    "platform": platform_name,
                    "code": code_playground_scan_step(args.playground_path, steps),
                },
                {
                    "name": "playground_scan_step_sanitized",
                    "platform": platform_name,
                    "code": code_playground_scan_step_sanitized(args.playground_path, steps),
                },
            ]
        )
        if args.include_bridge:
            subtests.append(
                {
                    "name": "playground_multi_step_bridge",
                    "platform": platform_name,
                    "code": code_closed_loop(
                        args.playground_path,
                        args.policy,
                        args.fit_json,
                        steps,
                        "fitted",
                        args.command_x,
                    ),
                }
            )
        bridge_mode = "all" if platform_name == "gpu" and args.include_bridge else "vanilla"
        subtests.append(
            {
                "name": f"closed_loop_policy_eval_{platform_name}",
                "platform": platform_name,
                "code": code_closed_loop(
                    args.playground_path,
                    args.policy,
                    args.fit_json,
                    steps,
                    bridge_mode,
                    args.command_x,
                ),
            }
        )
    requested = split_csv(args.subtests)
    if requested and requested != ["all"]:
        allowed = set(requested)
        subtests = [item for item in subtests if item["name"] in allowed]
    return subtests


def extract_marker(output: str, start_marker: str) -> dict | None:
    end_marker = start_marker.replace("START", "END")
    match = re.search(
        re.escape(start_marker) + r"\s*(\{.*?\})\s*" + re.escape(end_marker),
        output,
        flags=re.S,
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def extract_progress(output: str) -> list[dict]:
    pattern = (
        re.escape("SUBTEST_PROGRESS_JSON_START")
        + r"\s*(\{.*?\})\s*"
        + re.escape("SUBTEST_PROGRESS_JSON_END")
    )
    progress = []
    for match in re.finditer(pattern, output, flags=re.S):
        try:
            progress.append(json.loads(match.group(1)))
        except json.JSONDecodeError:
            pass
    return progress


def merged_env(base: Mapping[str, str], platform_name: str, variant: str) -> dict:
    env = dict(base)
    env["JAX_PLATFORM_NAME"] = platform_name
    env.update(VARIANT_ENVS[variant])
    existing = env.get("PYTHONPATH", "")
    paths = [str(ROOT / "tools"), str(ROOT), str(DEFAULT_PLAYGROUND)]
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def run_subtest(subtest: Mapping[str, Any], variant: str, args) -> dict:
    subdir = args.output_dir
    subdir.mkdir(parents=True, exist_ok=True)
    test_id = sanitize(f"{variant}_{subtest['platform']}_{subtest['name']}")
    stdout_path = subdir / f"{test_id}.stdout.txt"
    stderr_path = subdir / f"{test_id}.stderr.txt"
    env = merged_env(os.environ, subtest["platform"], variant)
    command = [str(args.env_python), "-c", subtest["code"]]
    start = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout_s,
            env=env,
            cwd=str(ROOT),
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        returncode = result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
        returncode = None
    elapsed = time.monotonic() - start
    stdout_path.write_text(stdout)
    stderr_path.write_text(stderr)
    combined = stdout + "\n" + stderr
    info = extract_marker(combined, "SUBTEST_INFO_JSON_START")
    result_payload = extract_marker(combined, "SUBTEST_RESULT_JSON_START")
    progress = extract_progress(combined)
    if timed_out:
        status = "TIMEOUT"
    elif returncode == 0:
        status = "PASS"
    else:
        status = "FAIL"
    return {
        "id": test_id,
        "name": subtest["name"],
        "platform": subtest["platform"],
        "variant": variant,
        "status": status,
        "returncode": returncode,
        "elapsed_s": elapsed,
        "command": command,
        "env_overrides": {
            key: env.get(key)
            for key in ROCM_ENV_KEYS
            if key in env and (key in VARIANT_ENVS.get(variant, {}) or key == "JAX_PLATFORM_NAME")
        },
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "info": info,
        "result": result_payload,
        "progress": progress,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-4000:],
    }


def result_passed(results: Sequence[dict], name: str, platform_name: str) -> bool:
    matching = [
        item
        for item in results
        if item["name"] == name and item["platform"] == platform_name and item["variant"] == "default"
    ]
    if not matching:
        matching = [
            item for item in results if item["name"] == name and item["platform"] == platform_name
        ]
    return bool(matching) and all(item["status"] == "PASS" for item in matching)


def result_failed(results: Sequence[dict], name: str, platform_name: str) -> bool:
    matching = [
        item
        for item in results
        if item["name"] == name and item["platform"] == platform_name and item["variant"] == "default"
    ]
    if not matching:
        matching = [
            item for item in results if item["name"] == name and item["platform"] == platform_name
        ]
    return any(
        item["name"] == name
        and item["platform"] == platform_name
        and item["status"] != "PASS"
        for item in matching
    )


def classify(results: Sequence[dict], platforms: Sequence[str]) -> dict:
    gpu = "gpu" in platforms
    cpu = "cpu" in platforms
    smallest = next((item for item in results if item["status"] != "PASS"), None)
    if gpu:
        if result_failed(results, "basic_jax", "gpu"):
            gate = "HOLD_BASIC_JAX_GPU"
        elif result_failed(results, "jax_jit_scan", "gpu"):
            gate = "HOLD_JAX_JIT_SCAN"
        elif result_failed(results, "minimal_mjx_step", "gpu"):
            gate = "HOLD_MINIMAL_MJX_GPU"
        elif any(
            result_failed(results, name, "gpu")
            for name in [
                "playground_reset",
                "playground_direct_mjx_step",
                "playground_direct_mjx_step_jit",
                "playground_one_step_vanilla",
                "playground_one_step_jit",
                "playground_multi_step_vanilla",
                "playground_scan_step_vanilla",
                "playground_scan_step_sanitized",
            ]
        ):
            gate = "HOLD_PLAYGROUND_GPU_STEP"
        elif (
            result_passed(results, "playground_multi_step_vanilla", "gpu")
            and result_failed(results, "playground_multi_step_bridge", "gpu")
        ):
            gate = "HOLD_BRIDGE_GPU_ONLY"
        elif result_failed(results, "closed_loop_policy_eval_gpu", "gpu"):
            if cpu and result_passed(results, "closed_loop_policy_eval_cpu", "cpu"):
                gate = "PASS_CPU_EVAL_ONLY"
            else:
                gate = "HOLD_LONG_HORIZON_GPU"
        elif all(item["status"] == "PASS" for item in results if item["platform"] == "gpu"):
            gate = "PASS_ROCM_MJX_READY"
        else:
            gate = "HOLD_INSUFFICIENT_DATA"
    elif cpu and result_passed(results, "closed_loop_policy_eval_cpu", "cpu"):
        gate = "PASS_CPU_EVAL_ONLY"
    else:
        gate = "HOLD_INSUFFICIENT_DATA"
    return {
        "gate_result": gate,
        "smallest_failing_subtest": None if smallest is None else smallest["id"],
        "smallest_failing_status": None if smallest is None else smallest["status"],
    }


def summarize_capabilities(results: Sequence[dict]) -> dict:
    def status_for(name: str, platform_name: str):
        matching = [
            item
            for item in results
            if item["name"] == name and item["platform"] == platform_name and item["variant"] == "default"
        ]
        if not matching:
            matching = [
                item for item in results if item["name"] == name and item["platform"] == platform_name
            ]
        if not matching:
            return "NOT_RUN"
        return "PASS" if all(item["status"] == "PASS" for item in matching) else "FAIL"

    return {
        "basic_jax_gpu": status_for("basic_jax", "gpu"),
        "jax_jit_scan_gpu": status_for("jax_jit_scan", "gpu"),
        "minimal_mjx_gpu": status_for("minimal_mjx_step", "gpu"),
        "playground_reset_gpu": status_for("playground_reset", "gpu"),
        "playground_direct_mjx_step_gpu": status_for(
            "playground_direct_mjx_step", "gpu"
        ),
        "playground_direct_mjx_step_jit_gpu": status_for(
            "playground_direct_mjx_step_jit", "gpu"
        ),
        "playground_step_gpu": status_for("playground_one_step_vanilla", "gpu"),
        "playground_step_jit_gpu": status_for("playground_one_step_jit", "gpu"),
        "playground_scan_step_gpu": status_for("playground_scan_step_vanilla", "gpu"),
        "playground_scan_step_sanitized_gpu": status_for(
            "playground_scan_step_sanitized", "gpu"
        ),
        "playground_bridge_gpu": status_for("playground_multi_step_bridge", "gpu"),
        "closed_loop_gpu": status_for("closed_loop_policy_eval_gpu", "gpu"),
        "closed_loop_cpu": status_for("closed_loop_policy_eval_cpu", "cpu"),
    }


def build_markdown(payload: Mapping[str, Any]) -> str:
    assessment = payload["assessment"]
    capabilities = payload["capabilities"]
    lines = [
        "# ROCm / MJX Runtime Isolation",
        "",
        f"gate_result: `{assessment['gate_result']}`",
        f"smallest_failing_subtest: `{assessment.get('smallest_failing_subtest')}`",
        "",
        "## Executive Summary",
        "",
        f"- Basic JAX GPU: `{capabilities['basic_jax_gpu']}`",
        f"- JAX jit/scan GPU: `{capabilities['jax_jit_scan_gpu']}`",
        f"- Minimal MJX GPU: `{capabilities['minimal_mjx_gpu']}`",
        f"- Playground reset GPU: `{capabilities['playground_reset_gpu']}`",
        f"- Playground direct MJX step GPU: `{capabilities['playground_direct_mjx_step_gpu']}`",
        f"- Playground direct MJX step JIT GPU: `{capabilities['playground_direct_mjx_step_jit_gpu']}`",
        f"- Playground one-step GPU: `{capabilities['playground_step_gpu']}`",
        f"- Playground one-step JIT GPU: `{capabilities['playground_step_jit_gpu']}`",
        f"- Playground scan-step GPU: `{capabilities['playground_scan_step_gpu']}`",
        f"- Playground sanitized scan-step GPU: `{capabilities['playground_scan_step_sanitized_gpu']}`",
        f"- Playground bridge GPU: `{capabilities['playground_bridge_gpu']}`",
        f"- Closed-loop GPU: `{capabilities['closed_loop_gpu']}`",
        f"- Closed-loop CPU: `{capabilities['closed_loop_cpu']}`",
        "",
        "This is an offline runtime/backend isolation report. No robot commands, SSH,",
        "deployment, or training are involved.",
        "",
        "## Matrix",
        "",
        "| id | variant | platform | subtest | status | returncode | elapsed_s | progress |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for item in payload["results"]:
        progress = item.get("progress") or []
        progress_text = ", ".join(
            f"{entry.get('steps')}:{entry.get('status')}" for entry in progress[-5:]
        )
        lines.append(
            f"| `{item['id']}` | `{item['variant']}` | `{item['platform']}` | "
            f"`{item['name']}` | `{item['status']}` | `{item.get('returncode')}` | "
            f"{item.get('elapsed_s', 0):.2f} | {progress_text or 'NA'} |"
        )
    lines.extend(
        [
            "",
            "## Failing Output Excerpts",
            "",
        ]
    )
    for item in payload["results"]:
        if item["status"] == "PASS":
            continue
        excerpt = (item.get("stderr_tail") or item.get("stdout_tail") or "").strip()
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"- stdout: `{item['stdout_path']}`")
        lines.append(f"- stderr: `{item['stderr_path']}`")
        lines.append("")
        lines.append("```text")
        lines.append(excerpt[-2500:] if excerpt else "No output captured.")
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Environment Variants Run",
            "",
            ", ".join(f"`{item}`" for item in payload["variants_run"]),
            "",
            "Supported variants are `default`, `preallocate_false`,",
            "`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,",
            "`disable_jit`, `debug_nans_infs`, `tensor_parallel_one`,",
            "`gfx1100_override`, `gfx1100_mem_safe`, `miopen_fusion_disabled`,",
            "`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,",
            "`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,",
            "`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.",
            "",
            "## Recommendation",
            "",
        ]
    )
    gate = assessment["gate_result"]
    if gate == "PASS_CPU_EVAL_ONLY":
        lines.append("Use CPU for the next correctness eval while the ROCm/MJX GPU path is fixed. Do not train yet.")
    elif gate == "HOLD_BASIC_JAX_GPU":
        lines.append("Fix the local JAX/ROCm install before debugging MuJoCo or Playground.")
    elif gate == "HOLD_JAX_JIT_SCAN":
        lines.append("Basic JAX GPU works, but jitted scan fails. Isolate JAX/XLA ROCm before MJX.")
    elif gate == "HOLD_MINIMAL_MJX_GPU":
        lines.append("JAX GPU works, but minimal MJX fails. Focus on MuJoCo MJX + ROCm compatibility.")
    elif gate == "HOLD_PLAYGROUND_GPU_STEP":
        lines.append("Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.")
    elif gate == "HOLD_BRIDGE_GPU_ONLY":
        lines.append("Vanilla Playground GPU stepping works, but bridge stepping fails. Inspect bridge insertion code.")
    elif gate == "HOLD_LONG_HORIZON_GPU":
        lines.append("Short GPU stepping works but longer closed-loop eval fails. Test memory settings and horizon/chunking.")
    elif gate == "PASS_ROCM_MJX_READY":
        lines.append("ROCm/MJX closed-loop eval is ready. Proceed to rerun actuator bridge eval, not training yet.")
    else:
        lines.append("Collect more isolation data before changing training or robot behavior.")
    return "\n".join(lines).rstrip() + "\n"


def write_reports(payload: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    report_dir = output_dir.parent if output_dir.name == "rocm_mjx_isolation" else output_dir
    report_dir.mkdir(parents=True, exist_ok=True)
    md_path = report_dir / "ROCM_MJX_RUNTIME_ISOLATION.md"
    json_path = report_dir / "rocm_mjx_runtime_isolation.json"
    md_path.write_text(build_markdown(payload))
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run subprocess isolation tests for ROCm/MJX closed-loop failures."
    )
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--env-python", type=Path, default=DEFAULT_ENV_PYTHON)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--fit-json", type=Path, default=DEFAULT_FIT_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--steps", default="1,2,10,100,747")
    parser.add_argument("--platforms", default="gpu,cpu")
    parser.add_argument(
        "--variants",
        default="default",
        help=(
            "comma-separated env variants: default, preallocate_false, "
            "mem_fraction_050, mem_fraction_060, allocator_platform, "
            "disable_jit, debug_nans_infs, tensor_parallel_one, "
            "gfx1100_override, gfx1100_mem_safe, miopen_fusion_disabled, "
            "xla_disable_latency_scheduler, xla_disable_triton_gemm, "
            "xla_disable_triton_gemm_softmax, xla_compiler_conservative, "
            "rocm_strict_ieee, xla_rocm_data_dir, xla_triton_strict_ieee"
        ),
    )
    parser.add_argument(
        "--subtests",
        default="all",
        help=(
            "comma-separated subtests or all. Examples: basic_jax,"
            "playground_one_step_vanilla,playground_one_step_jit,"
            "playground_direct_mjx_step,playground_direct_mjx_step_jit,"
            "playground_scan_step_vanilla,playground_scan_step_sanitized,"
            "playground_xml_contact_audit,closed_loop_policy_eval_gpu"
        ),
    )
    parser.add_argument("--include-bridge", action="store_true")
    parser.add_argument("--timeout-s", type=int, default=120)
    args = parser.parse_args()

    args.playground_path = args.playground_path.expanduser().absolute()
    args.env_python = args.env_python.expanduser().absolute()
    args.policy = args.policy.expanduser().absolute()
    args.fit_json = args.fit_json.expanduser().absolute()
    args.output_dir = args.output_dir.expanduser().absolute()

    variants = split_csv(args.variants)
    unknown = [item for item in variants if item not in VARIANT_ENVS]
    if unknown:
        raise SystemExit(f"Unknown variants: {', '.join(unknown)}")

    subtests = build_subtests(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for variant in variants:
        for subtest in subtests:
            result = run_subtest(subtest, variant, args)
            results.append(result)
            print(
                f"{result['id']}: {result['status']} returncode={result['returncode']} "
                f"elapsed={result['elapsed_s']:.2f}s"
            )
            sys.stdout.flush()

    platforms = split_csv(args.platforms)
    payload = {
        "mission": "ROCm/MJX closed-loop runtime isolation",
        "host_info": host_info(),
        "inputs": {
            "playground_path": str(args.playground_path),
            "env_python": str(args.env_python),
            "policy": str(args.policy),
            "fit_json": str(args.fit_json),
            "output_dir": str(args.output_dir),
            "command_x": args.command_x,
            "steps": parse_steps(args.steps),
            "platforms": platforms,
            "include_bridge": args.include_bridge,
            "timeout_s": args.timeout_s,
        },
        "variants_run": variants,
        "results": results,
        "capabilities": summarize_capabilities(results),
        "assessment": classify(results, platforms),
    }
    md_path, json_path = write_reports(payload, args.output_dir)
    print(md_path)
    print(json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
