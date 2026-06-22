#!/usr/bin/env python3
"""Generate reduced Open Duck MJCF variants and probe raw MJX stepping.

This is an offline ROCm debugging helper. It does not instantiate the training
env, run policy inference, train, or touch robot hardware.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from typing import Any, Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_SOURCE_XML_DIR = (
    DEFAULT_PLAYGROUND / "playground" / "open_duck_mini_v2" / "xmls"
)
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "rocm_mjx_reduced_model_probe"


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def safe_symlink(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        return
    dst.symlink_to(src, target_is_directory=src.is_dir())


def copy_xml_tree(source_xml_dir: Path, variant_dir: Path) -> None:
    variant_dir.mkdir(parents=True, exist_ok=True)
    for path in source_xml_dir.glob("*.xml"):
        shutil.copy2(path, variant_dir / path.name)
    config = source_xml_dir / "config.json"
    if config.exists():
        shutil.copy2(config, variant_dir / config.name)
    assets = source_xml_dir / "assets"
    if assets.exists():
        safe_symlink(assets.resolve(), variant_dir / "assets")


def parse(path: Path) -> ET.ElementTree:
    return ET.parse(path)


def write_xml(tree: ET.ElementTree, path: Path) -> None:
    tree.write(path, encoding="utf-8", xml_declaration=True)


def set_contact_enabled(elem: ET.Element, enabled: bool) -> None:
    if enabled:
        elem.attrib.setdefault("contype", "1")
        elem.attrib.setdefault("conaffinity", "1")
    else:
        elem.set("contype", "0")
        elem.set("conaffinity", "0")


def contact_geom(elem: ET.Element) -> bool:
    name = elem.attrib.get("name")
    return name in {"left_foot_bottom_tpu", "right_foot_bottom_tpu", "floor"}


def foot_geom(elem: ET.Element) -> bool:
    return elem.attrib.get("name") in {"left_foot_bottom_tpu", "right_foot_bottom_tpu"}


def patch_no_contact(variant_dir: Path) -> None:
    for filename in ["scene_flat_terrain.xml", "open_duck_mini_v2.xml"]:
        path = variant_dir / filename
        tree = parse(path)
        for elem in tree.getroot().iter("geom"):
            if contact_geom(elem):
                set_contact_enabled(elem, False)
        write_xml(tree, path)


def patch_floor_contact_off(variant_dir: Path) -> None:
    path = variant_dir / "scene_flat_terrain.xml"
    tree = parse(path)
    for elem in tree.getroot().iter("geom"):
        if elem.attrib.get("name") == "floor":
            set_contact_enabled(elem, False)
    write_xml(tree, path)


def patch_box_feet(variant_dir: Path) -> None:
    path = variant_dir / "open_duck_mini_v2.xml"
    tree = parse(path)
    for elem in tree.getroot().iter("geom"):
        if foot_geom(elem):
            elem.attrib.pop("mesh", None)
            elem.attrib.pop("material", None)
            elem.set("type", "box")
            elem.set("size", "0.035 0.025 0.006")
            elem.set("contype", "1")
            elem.set("conaffinity", "1")
            elem.set("condim", "3")
            elem.set("friction", "1.0 0.005 0.0001")
    write_xml(tree, path)


def patch_remove_visual_meshes(variant_dir: Path) -> None:
    path = variant_dir / "open_duck_mini_v2.xml"
    tree = parse(path)
    for parent in tree.getroot().iter():
        children = list(parent)
        for child in children:
            if child.tag == "geom" and child.attrib.get("class") == "visual":
                parent.remove(child)
    write_xml(tree, path)


VARIANTS: dict[str, tuple[str, tuple[Callable[[Path], None], ...]]] = {
    "baseline": ("Unmodified scene_flat_terrain model copy", ()),
    "no_contact": (
        "Disable floor and TPU foot contact geoms",
        (patch_no_contact,),
    ),
    "floor_contact_off": (
        "Disable only floor contact, leaving foot contact attrs intact",
        (patch_floor_contact_off,),
    ),
    "box_feet": (
        "Replace TPU foot collision mesh geoms with simple box geoms",
        (patch_box_feet,),
    ),
    "box_feet_no_visual": (
        "Replace TPU foot collision meshes with boxes and remove visual mesh geoms",
        (patch_box_feet, patch_remove_visual_meshes),
    ),
    "no_visual_meshes": (
        "Remove visual mesh geoms, leaving collision geoms intact",
        (patch_remove_visual_meshes,),
    ),
}


def generate_variant(source_xml_dir: Path, output_dir: Path, name: str) -> dict[str, Any]:
    if name not in VARIANTS:
        raise ValueError(f"Unknown variant: {name}")
    description, patchers = VARIANTS[name]
    variant_dir = output_dir / "variants" / name
    if variant_dir.exists():
        shutil.rmtree(variant_dir)
    copy_xml_tree(source_xml_dir, variant_dir)
    for patcher in patchers:
        patcher(variant_dir)
    return {
        "name": name,
        "description": description,
        "xml": str(variant_dir / "scene_flat_terrain.xml"),
        "variant_dir": str(variant_dir),
    }


def worker_probe(xml_path: Path, n_substeps: int) -> int:
    import jax
    import jax.numpy as jnp
    import mujoco
    from mujoco import mjx

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    mx = mjx.put_model(model)
    data = mjx.make_data(mx)
    if model.nkey:
        data = data.replace(
            qpos=jnp.asarray(model.key_qpos[0], dtype=jnp.float32),
            qvel=jnp.zeros(model.nv, dtype=jnp.float32),
            ctrl=jnp.asarray(model.key_ctrl[0], dtype=jnp.float32),
        )
    def body(carry, _):
        return mjx.step(mx, carry), None

    if n_substeps <= 1:
        data = mjx.step(mx, data)
    else:
        data = jax.lax.scan(body, data, (), length=n_substeps)[0]
    jax.tree_util.tree_map(
        lambda value: value.block_until_ready()
        if hasattr(value, "block_until_ready")
        else value,
        (data.qpos, data.qvel, data.ctrl),
    )
    result = {
        "status": "PASS",
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
        "mujoco_version": getattr(mujoco, "__version__", None),
        "n_substeps": n_substeps,
        "counts": {
            "nq": int(model.nq),
            "nv": int(model.nv),
            "nu": int(model.nu),
            "ngeom": int(model.ngeom),
            "nmesh": int(model.nmesh),
            "nsensor": int(model.nsensor),
        },
        "qpos0": float(data.qpos[0]),
        "base_height": float(data.qpos[2]) if model.nq > 2 else None,
    }
    print("PROBE_RESULT_JSON_START")
    print(json.dumps(result, sort_keys=True))
    print("PROBE_RESULT_JSON_END")
    return 0


def extract_result(text: str) -> dict[str, Any] | None:
    match = re.search(
        r"PROBE_RESULT_JSON_START\s*(\{.*?\})\s*PROBE_RESULT_JSON_END",
        text,
        flags=re.S,
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def run_probe(
    env_python: Path,
    xml_path: Path,
    platform: str,
    timeout_s: int,
    log_dir: Path,
    variant: str,
    n_substeps: int,
) -> dict[str, Any]:
    log_dir.mkdir(parents=True, exist_ok=True)
    test_id = f"{variant}_{platform}"
    stdout_path = log_dir / f"{test_id}.stdout.txt"
    stderr_path = log_dir / f"{test_id}.stderr.txt"
    env = dict(os.environ)
    env["JAX_PLATFORM_NAME"] = platform
    command = [
        str(env_python),
        str(Path(__file__).resolve()),
        "--worker-probe",
        str(xml_path),
        "--worker-n-substeps",
        str(n_substeps),
    ]
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            env=env,
            cwd=str(ROOT),
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
        returncode = None
    elapsed = time.monotonic() - start
    stdout_path.write_text(stdout)
    stderr_path.write_text(stderr)
    status = "TIMEOUT" if timed_out else ("PASS" if returncode == 0 else "FAIL")
    return {
        "variant": variant,
        "platform": platform,
        "n_substeps": n_substeps,
        "status": status,
        "returncode": returncode,
        "elapsed_s": elapsed,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-3000:],
        "result": extract_result(stdout + "\n" + stderr),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ROCm MJX Reduced Model Probe",
        "",
        f"generated_at: `{payload['generated_at']}`",
        f"source_xml_dir: `{payload['source_xml_dir']}`",
        f"env_python: `{payload['env_python']}`",
        "",
        "## Executive Summary",
        "",
        "This is an offline reduced-MJCF probe. It generates model variants and",
        "runs raw `mjx.step(...)` or a scanned substep loop in subprocesses",
        "with explicit timeouts.",
        "No training, policy inference, robot SSH, deployment, or robot motion is",
        "involved.",
        "",
        "## Result Matrix",
        "",
        "| variant | platform | n_substeps | status | elapsed_s | returncode |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in payload["results"]:
        lines.append(
            f"| `{row['variant']}` | `{row['platform']}` | {row['n_substeps']} | `{row['status']}` | "
            f"{row['elapsed_s']:.2f} | `{row.get('returncode')}` |"
        )
    lines.extend(["", "## Variants", "", "| variant | description | xml |", "|---|---|---|"])
    for variant in payload["variants"]:
        lines.append(
            f"| `{variant['name']}` | {variant['description']} | `{variant['xml']}` |"
        )
    lines.extend(["", "## Failing Output Excerpts", ""])
    for row in payload["results"]:
        if row["status"] == "PASS":
            continue
        excerpt = (row.get("stderr_tail") or row.get("stdout_tail") or "").strip()
        lines.append(f"### {row['variant']} / {row['platform']}")
        lines.append("")
        lines.append(f"- stdout: `{row['stdout_path']}`")
        lines.append(f"- stderr: `{row['stderr_path']}`")
        lines.append("")
        lines.append("```text")
        lines.append(excerpt or "No output captured.")
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "If a reduced variant passes on ROCm while baseline hangs, that variant",
            "identifies a model feature worth isolating further. If all variants",
            "share the same ROCm hold, the issue is likely deeper than the tested",
            "contact/mesh simplifications.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate reduced Open Duck MJCF variants and probe raw MJX stepping."
    )
    parser.add_argument("--source-xml-dir", type=Path, default=DEFAULT_SOURCE_XML_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-python", type=Path, default=Path(sys.executable))
    parser.add_argument("--variants", default="baseline,no_contact,floor_contact_off,box_feet,box_feet_no_visual,no_visual_meshes")
    parser.add_argument("--platforms", default="cpu")
    parser.add_argument("--n-substeps", type=int, default=1)
    parser.add_argument("--timeout-s", type=int, default=60)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--worker-probe", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-n-substeps", type=int, default=1, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker_probe:
        return worker_probe(args.worker_probe, args.worker_n_substeps)

    args.source_xml_dir = args.source_xml_dir.expanduser().absolute()
    args.output_dir = args.output_dir.expanduser().absolute()
    args.env_python = args.env_python.expanduser().absolute()
    output_md = (
        args.output_md.expanduser().absolute()
        if args.output_md
        else args.output_dir / "ROCM_MJX_REDUCED_MODEL_PROBE.md"
    )
    output_json = (
        args.output_json.expanduser().absolute()
        if args.output_json
        else args.output_dir / "rocm_mjx_reduced_model_probe.json"
    )

    variant_names = split_csv(args.variants)
    unknown = [name for name in variant_names if name not in VARIANTS]
    if unknown:
        raise SystemExit(f"Unknown variants: {', '.join(unknown)}")
    if not args.source_xml_dir.exists():
        raise SystemExit(f"Source XML dir not found: {args.source_xml_dir}")
    if not args.env_python.exists():
        raise SystemExit(f"Env Python not found: {args.env_python}")

    variants = [
        generate_variant(args.source_xml_dir, args.output_dir, name)
        for name in variant_names
    ]
    results = []
    for variant in variants:
        for platform in split_csv(args.platforms):
            row = run_probe(
                args.env_python,
                Path(variant["xml"]),
                platform,
                args.timeout_s,
                args.output_dir / "logs",
                variant["name"],
                args.n_substeps,
            )
            results.append(row)
            print(
                f"{variant['name']} {platform}: {row['status']} "
                f"elapsed={row['elapsed_s']:.2f}s"
            )
            sys.stdout.flush()

    payload = {
        "mission": "Open Duck reduced MJX model probe",
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "source_xml_dir": str(args.source_xml_dir),
        "env_python": str(args.env_python),
        "inputs": {
            "variants": variant_names,
            "platforms": split_csv(args.platforms),
            "n_substeps": args.n_substeps,
            "timeout_s": args.timeout_s,
        },
        "variants": variants,
        "results": results,
    }
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(payload))
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    print(output_md)
    print(output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
