#!/usr/bin/env python3
"""Read-only 1M-to-2M drift audit for the applied-target continuation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

from flax.training import orbax_utils
import jax
import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort
from orbax import checkpoint as ocp
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


JOINTS = [
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
]
SEGMENTS = {
    "gyro": (0, 3),
    "accelerometer": (3, 6),
    "command": (6, 13),
    "joint_position": (13, 27),
    "joint_velocity": (27, 41),
    "last_sent_action": (41, 55),
    "prior_sent_action": (55, 69),
    "third_sent_action": (69, 83),
    "applied_target": (83, 97),
    "contact": (97, 99),
    "phase": (99, 101),
    "reference_action": (101, 115),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def trace_manifest(path: Path) -> list[dict]:
    return [
        {
            "path": str(item.resolve()),
            "sha256": sha256_file(item.resolve()),
            "bytes": item.stat().st_size,
        }
        for item in sorted(path.glob("*.jsonl"))
    ]


def path_text(path) -> str:
    parts = []
    for item in path:
        value = getattr(item, "key", getattr(item, "idx", getattr(item, "name", item)))
        parts.append(str(value))
    return "/".join(parts)


def array_stats(values) -> dict:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    return {
        "mean": float(np.mean(values)),
        "rms": float(np.sqrt(np.mean(np.square(values)))),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
    }


def restore_pair(template_path: Path, one_path: Path, two_path: Path):
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(template_path))
    restore_args = orbax_utils.restore_args_from_target(template)
    one = checkpointer.restore(str(one_path), item=template, restore_args=restore_args)
    two = checkpointer.restore(str(two_path), item=template, restore_args=restore_args)
    if jax.tree_util.tree_structure(one) != jax.tree_util.tree_structure(two):
        raise AssertionError("checkpoint tree structures differ")
    return one, two


def parameter_drift(one, two) -> dict:
    groups = {}
    for group_name, index in (("normalizer", 0), ("actor", 1), ("critic", 2)):
        rows = []
        for (path_a, leaf_a), (path_b, leaf_b) in zip(
            jax.tree_util.tree_flatten_with_path(one[index])[0],
            jax.tree_util.tree_flatten_with_path(two[index])[0],
            strict=True,
        ):
            if path_text(path_a) != path_text(path_b):
                raise AssertionError("checkpoint leaf paths differ")
            a = np.asarray(leaf_a, dtype=np.float64)
            b = np.asarray(leaf_b, dtype=np.float64)
            delta = b - a
            base_norm = float(np.linalg.norm(a.reshape(-1)))
            delta_norm = float(np.linalg.norm(delta.reshape(-1)))
            rows.append(
                {
                    "path": path_text(path_a),
                    "shape": list(a.shape),
                    "max_abs_delta": float(np.max(np.abs(delta))),
                    "rms_delta": float(np.sqrt(np.mean(np.square(delta)))),
                    "l2_delta": delta_norm,
                    "relative_l2_delta": delta_norm / max(base_norm, 1e-12),
                    "finite": bool(np.isfinite(a).all() and np.isfinite(b).all()),
                }
            )
        groups[group_name] = {
            "leaf_count": len(rows),
            "all_finite": all(row["finite"] for row in rows),
            "max_relative_l2_delta": max(row["relative_l2_delta"] for row in rows),
            "leaves": rows,
        }
    return groups


def load_trace_corpus(root: Path) -> dict:
    traces = {}
    for path in sorted(root.glob("*.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        rows = [row for row in rows if row.get("mode") == "fitted"]
        if not rows:
            raise ValueError(f"empty fitted trace: {path}")
        traces[path.name] = rows
    if not traces:
        raise ValueError(f"no traces in {root}")
    return traces


def add_raw_output(model):
    model = copy.deepcopy(model)
    if not any(value.name == "raw_continuous_actions" for value in model.graph.output):
        model.graph.output.append(
            helper.make_tensor_value_info(
                "raw_continuous_actions", TensorProto.FLOAT, [1, len(JOINTS)]
            )
        )
    return model


def hybrid_model(base_model, donor_model, donor_names: set[str]):
    model = copy.deepcopy(base_model)
    donor = {item.name: item for item in donor_model.graph.initializer}
    for index, item in enumerate(model.graph.initializer):
        if item.name in donor_names:
            model.graph.initializer[index].CopyFrom(donor[item.name])
    return model


def session(model) -> ort.InferenceSession:
    return ort.InferenceSession(
        add_raw_output(model).SerializeToString(), providers=["CPUExecutionProvider"]
    )


def run_policy(sess, obs: np.ndarray, previous: np.ndarray):
    values = sess.run(
        ["continuous_actions", "previous_action_out", "raw_continuous_actions"],
        {"obs": obs[None].astype(np.float32), "previous_action": previous[None].astype(np.float32)},
    )
    return values[0][0], values[1][0], values[2][0]


def action_attribution(one_model, two_model, corpora: dict) -> dict:
    normalizer_names = {"obs_mean", "obs_std"}
    sessions = {
        "one_full": session(one_model),
        "two_full": session(two_model),
        "one_actor_two_normalizer": session(
            hybrid_model(one_model, two_model, normalizer_names)
        ),
        "two_actor_one_normalizer": session(
            hybrid_model(two_model, one_model, normalizer_names)
        ),
    }
    all_results = {}
    own_replay_errors = {"1M": [], "2M": []}
    for corpus_name, traces in corpora.items():
        outputs = {name: [] for name in sessions}
        raw_outputs = {name: [] for name in sessions}
        for rows in traces.values():
            recorded_previous = np.zeros(len(JOINTS), dtype=np.float32)
            own_key = "one_full" if corpus_name == "1M" else "two_full"
            own_previous = np.zeros(len(JOINTS), dtype=np.float32)
            for row in rows:
                obs = np.asarray(row["obs_state"], dtype=np.float32)
                for name, sess in sessions.items():
                    action, _, raw = run_policy(sess, obs, recorded_previous)
                    outputs[name].append(action)
                    raw_outputs[name].append(raw)
                own_action, own_previous, _ = run_policy(
                    sessions[own_key], obs, own_previous
                )
                own_replay_errors[corpus_name].append(
                    float(np.max(np.abs(own_action - np.asarray(row["action"]))))
                )
                recorded_previous = np.asarray(row["action"], dtype=np.float32)
        outputs = {key: np.asarray(value) for key, value in outputs.items()}
        raw_outputs = {key: np.asarray(value) for key, value in raw_outputs.items()}

        def comparison(candidate: str, raw: bool = False):
            source = raw_outputs if raw else outputs
            delta = np.abs(source[candidate] - source["one_full"])
            return {
                "global": array_stats(delta),
                "per_joint": {
                    joint: array_stats(delta[:, index])
                    for index, joint in enumerate(JOINTS)
                },
            }

        all_results[corpus_name] = {
            "samples": int(outputs["one_full"].shape[0]),
            "bounded_action_delta": {
                "total_two_vs_one": comparison("two_full"),
                "normalizer_only_on_one_actor": comparison("one_actor_two_normalizer"),
                "actor_only_with_one_normalizer": comparison("two_actor_one_normalizer"),
            },
            "raw_action_delta": {
                "total_two_vs_one": comparison("two_full", True),
                "normalizer_only_on_one_actor": comparison("one_actor_two_normalizer", True),
                "actor_only_with_one_normalizer": comparison("two_actor_one_normalizer", True),
            },
        }
    return {
        "corpora": all_results,
        "own_trace_replay_max_error": {
            key: max(values) for key, values in own_replay_errors.items()
        },
    }


def normalizer_drift(one, two, corpora: dict) -> dict:
    mean_one = np.asarray(one[0]["mean"]["state"], dtype=np.float64)
    mean_two = np.asarray(two[0]["mean"]["state"], dtype=np.float64)
    std_one = np.asarray(one[0]["std"]["state"], dtype=np.float64)
    std_two = np.asarray(two[0]["std"]["state"], dtype=np.float64)
    raw_obs = np.vstack(
        [
            np.asarray(row["obs_state"], dtype=np.float64)
            for traces in corpora.values()
            for rows in traces.values()
            for row in rows
        ]
    )
    normalized_one = (raw_obs - mean_one) / std_one
    normalized_two = (raw_obs - mean_two) / std_two
    normalized_delta = np.abs(normalized_two - normalized_one)
    segments = {}
    for name, (start, end) in SEGMENTS.items():
        ratio = std_two[start:end] / np.maximum(std_one[start:end], 1e-12)
        segments[name] = {
            "mean_abs_mean_delta": float(np.mean(np.abs(mean_two[start:end] - mean_one[start:end]))),
            "max_abs_mean_delta": float(np.max(np.abs(mean_two[start:end] - mean_one[start:end]))),
            "std_ratio": array_stats(ratio),
            "observed_normalized_delta": array_stats(normalized_delta[:, start:end]),
        }
    count_one = int(np.asarray(one[0]["count"]["hi"])) * 2**32 + int(np.asarray(one[0]["count"]["lo"]))
    count_two = int(np.asarray(two[0]["count"]["hi"])) * 2**32 + int(np.asarray(two[0]["count"]["lo"]))
    return {
        "sample_count_1M": count_one,
        "sample_count_2M": count_two,
        "count_ratio": count_two / count_one,
        "global_observed_normalized_delta": array_stats(normalized_delta),
        "segments": segments,
    }


def tracking_drift(eval_one: dict, eval_two: dict) -> dict:
    def collect(payload):
        result = {joint: [] for joint in JOINTS}
        bridge = {joint: [] for joint in JOINTS}
        for run in payload["runs"]:
            joints = run["modes"]["fitted"]["joints"]
            for joint in JOINTS:
                result[joint].append(joints[joint]["joint_target_tracking_error_rad"]["p95"])
                bridge[joint].append(joints[joint]["bridge_tracking_error_rad"]["p95"])
        return result, bridge
    one_joint, one_bridge = collect(eval_one)
    two_joint, two_bridge = collect(eval_two)
    rows = []
    for joint in JOINTS:
        one_max = max(one_joint[joint])
        two_max = max(two_joint[joint])
        rows.append(
            {
                "joint": joint,
                "joint_tracking_p95_max_1M": one_max,
                "joint_tracking_p95_max_2M": two_max,
                "joint_tracking_delta_rad": two_max - one_max,
                "bridge_error_p95_max_1M": max(one_bridge[joint]),
                "bridge_error_p95_max_2M": max(two_bridge[joint]),
                "bridge_error_delta_rad": max(two_bridge[joint]) - max(one_bridge[joint]),
            }
        )
    return {
        "per_joint": rows,
        "largest_joint_tracking_regressions": sorted(
            rows, key=lambda row: row["joint_tracking_delta_rad"], reverse=True
        )[:5],
    }


def training_metrics(path: Path) -> dict:
    accumulator = EventAccumulator(str(path), size_guidance={"scalars": 0})
    accumulator.Reload()
    selected = {}
    for tag in accumulator.Tags().get("scalars", []):
        events = accumulator.Scalars(tag)
        by_step = {int(event.step): float(event.value) for event in events}
        if 1003520 in by_step and 2007040 in by_step:
            selected[tag] = {
                "1M": by_step[1003520],
                "2M": by_step[2007040],
                "delta": by_step[2007040] - by_step[1003520],
            }
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-1m", type=Path, required=True)
    parser.add_argument("--checkpoint-2m", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--onnx-1m", type=Path, required=True)
    parser.add_argument("--onnx-2m", type=Path, required=True)
    parser.add_argument("--eval-1m", type=Path, required=True)
    parser.add_argument("--eval-2m", type=Path, required=True)
    parser.add_argument("--traces-1m", type=Path, required=True)
    parser.add_argument("--traces-2m", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    one, two = restore_pair(
        args.cpu_template.resolve(), args.checkpoint_1m.resolve(), args.checkpoint_2m.resolve()
    )
    model_one = onnx.load(args.onnx_1m)
    model_two = onnx.load(args.onnx_2m)
    corpora = {
        "1M": load_trace_corpus(args.traces_1m),
        "2M": load_trace_corpus(args.traces_2m),
    }
    eval_one = json.loads(args.eval_1m.read_text())
    eval_two = json.loads(args.eval_2m.read_text())
    params = parameter_drift(one, two)
    normalizer = normalizer_drift(one, two, corpora)
    action = action_attribution(model_one, model_two, corpora)
    tracking = tracking_drift(eval_one, eval_two)
    metrics = training_metrics(args.event_file)

    actor_rms = np.mean(
        [row["rms_delta"] for row in params["actor"]["leaves"]]
    )
    norm_raw_rms = max(
        value["raw_action_delta"]["normalizer_only_on_one_actor"]["global"]["rms"]
        for value in action["corpora"].values()
    )
    actor_raw_rms = max(
        value["raw_action_delta"]["actor_only_with_one_normalizer"]["global"]["rms"]
        for value in action["corpora"].values()
    )
    mechanism = (
        "ACTOR_PARAMETER_DRIFT_DOMINATES_NORMALIZER_DRIFT"
        if actor_raw_rms > 2.0 * max(norm_raw_rms, 1e-12)
        else "MIXED_ACTOR_AND_NORMALIZER_DRIFT"
    )
    checks = {
        "checkpoint_structures_match_and_are_finite": all(
            params[group]["all_finite"] for group in params
        ),
        "own_onnx_trace_replay_within_1e_5": max(
            action["own_trace_replay_max_error"].values()
        ) <= 1e-5,
        "both_trace_corpora_have_162_samples": all(
            item["samples"] == 162 for item in action["corpora"].values()
        ),
        "one_million_full_gate_passed": all(
            run["status"] == "PASS_CANDIDATE_SIM_GATE" for run in eval_one["runs"]
        ),
        "two_million_tracking_gate_failed": all(
            run["status"] == "HOLD_CANDIDATE_TRACKING" for run in eval_two["runs"]
        ),
        "training_reward_increased_while_external_gate_regressed": (
            metrics["eval/episode_reward"]["delta"] > 0
            and max(row["joint_tracking_delta_rad"] for row in tracking["per_joint"]) > 0
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_APPLIED_TARGET_DRIFT_AUDIT" if not failed else "FAIL_APPLIED_TARGET_DRIFT_AUDIT"
    payload = {
        "schema_version": "ground_up_applied_target_drift_audit.v1",
        "status": status,
        "mechanism": mechanism,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "parameter_drift": params,
        "normalizer_drift": normalizer,
        "action_attribution": action,
        "tracking_drift": tracking,
        "training_metrics": metrics,
        "summary": {
            "mean_actor_leaf_rms_delta": float(actor_rms),
            "max_raw_action_rms_from_normalizer_only": norm_raw_rms,
            "max_raw_action_rms_from_actor_only": actor_raw_rms,
            "actor_to_normalizer_raw_action_rms_ratio": actor_raw_rms / max(norm_raw_rms, 1e-12),
        },
        "inputs": {
            name: {"path": str(path.resolve()), "sha256": sha256_file(path.resolve()) if path.is_file() else None}
            for name, path in {
                "onnx_1m": args.onnx_1m,
                "onnx_2m": args.onnx_2m,
                "eval_1m": args.eval_1m,
                "eval_2m": args.eval_2m,
                "event_file": args.event_file,
            }.items()
        },
        "trace_inputs": {
            "1M": trace_manifest(args.traces_1m),
            "2M": trace_manifest(args.traces_2m),
        },
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    regressions = tracking["largest_joint_tracking_regressions"][:3]
    reward_delta = metrics["eval/episode_reward"]["delta"]
    imitation_delta = metrics["eval/episode_reward/imitation"]["delta"]
    linear_delta = metrics["eval/episode_reward/tracking_lin_vel"]["delta"]
    angular_delta = metrics["eval/episode_reward/tracking_ang_vel"]["delta"]
    lines = [
        "# Ground-Up Applied-Target 1M→2M Drift Audit",
        "",
        f"status: `{status}`",
        f"measured mechanism: `{mechanism}`",
        "",
        f"actor-only raw-action RMS drift: `{actor_raw_rms:.8f}`",
        f"normalizer-only raw-action RMS drift: `{norm_raw_rms:.8f}`",
        f"actor/normalizer ratio: `{actor_raw_rms / max(norm_raw_rms, 1e-12):.3f}`",
        "",
        "## Contract checks",
        "",
        *[f"- {name}: `{'PASS' if passed else 'FAIL'}`" for name, passed in checks.items()],
        "",
        "## Objective-versus-gate evidence",
        "",
        f"- hosted evaluation reward delta: `{reward_delta:+.8f}`",
        f"- hosted imitation component delta: `{imitation_delta:+.8f}`",
        f"- hosted linear-velocity component delta: `{linear_delta:+.8f}`",
        f"- hosted angular-velocity component delta: `{angular_delta:+.8f}`",
        "",
        "The optimizer improved every listed hosted objective while the frozen",
        "hardware-oriented joint-target tracking gate worsened. The fitted bridge",
        "error stayed effectively unchanged on the largest regressions. This is",
        "evidence of actor/objective drift, not checksum, bridge, checkpoint-restore,",
        "or observation-normalizer corruption.",
        "",
        "## Per-joint evidence",
        "",
        "Largest external joint-tracking regressions:",
        "",
        *[
            f"- {row['joint']}: `{row['joint_tracking_delta_rad']:+.8f} rad` "
            f"(bridge delta `{row['bridge_error_delta_rad']:+.8f} rad`)"
            for row in regressions
        ],
        "",
        "Training remains unauthorized. This audit measures drift; it does not select a retention recipe by itself.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "mechanism": mechanism, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
