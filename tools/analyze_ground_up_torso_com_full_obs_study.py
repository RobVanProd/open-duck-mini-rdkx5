#!/usr/bin/env python3
"""Analyze the frozen full-observation decode and identical-state actor forks."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort

from check_ground_up_torso_com_full_obs_contract import POLICY_ROOT, POLICIES, sha256


CLASS_NAMES = ["NEG", "NOMINAL", "POS"]
CLASS_BY_CONDITION = {
    "TORSO_COM_X_NEG": "NEG",
    "NOMINAL": "NOMINAL",
    "TORSO_COM_X_POS": "POS",
}
TICKS = list(range(41))
ENDS = [8, 16, 24, 32, 40]
WIDTHS = [1, 2, 4, 8, 16]
FORK_TICKS = [0, 24, 32, 40]
COM_DIRECTION = np.asarray(
    [1.1654748916625977, 0.11948448419570923, 1.0919904708862305],
    dtype=np.float32,
)


def confusion(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    out = np.zeros((3, 3), dtype=np.int64)
    for true, pred in zip(y_true, y_pred, strict=True):
        out[int(true), int(pred)] += 1
    return out


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    cm = confusion(y_true, y_pred)
    recall, f1 = [], []
    for index in range(3):
        tp = int(cm[index, index])
        fn = int(np.sum(cm[index]) - tp)
        fp = int(np.sum(cm[:, index]) - tp)
        rec = tp / (tp + fn) if tp + fn else 0.0
        pre = tp / (tp + fp) if tp + fp else 0.0
        recall.append(rec)
        f1.append(2 * pre * rec / (pre + rec) if pre + rec else 0.0)
    return {
        "samples": int(y_true.size),
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(np.mean(f1)),
        "class_recall": recall,
        "confusion": cm.tolist(),
    }


def ridge_scores(x_train: np.ndarray, x_test: np.ndarray, labels: np.ndarray) -> np.ndarray:
    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    std = np.where(std == 0.0, 1.0, std)
    train = np.column_stack([(x_train - mean) / std, np.ones(x_train.shape[0])])
    test = np.column_stack([(x_test - mean) / std, np.ones(x_test.shape[0])])
    reg = np.eye(train.shape[1])
    reg[-1, -1] = 0.0
    projection = np.linalg.solve(train.T @ train + reg, train.T)
    return test @ projection @ np.eye(3)[labels]


def folds(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    definitions = []
    for family, field, values in (
        ("arm", "arm", ["A05_DIRECT", "U05_DIRECT", "U_CURRICULUM"]),
        ("command_x", "command_key", ["0.000", "0.074", "0.077", "0.080"]),
        ("fit", "fit", ["p30", "p31_34"]),
    ):
        for value in values:
            test = np.asarray([i for i, row in enumerate(samples) if row[field] == value])
            train = np.asarray([i for i, row in enumerate(samples) if row[field] != value])
            definitions.append({"family": family, "held_out": value, "train": train, "test": test})
    return definitions


def probe(x: np.ndarray, labels: np.ndarray, definitions: list[dict[str, Any]]) -> dict[str, Any]:
    fold_rows = []
    family_true: dict[str, list[np.ndarray]] = defaultdict(list)
    family_pred: dict[str, list[np.ndarray]] = defaultdict(list)
    for fold in definitions:
        train, test = fold["train"], fold["test"]
        pred = np.argmax(ridge_scores(x[train], x[test], labels[train]), axis=1)
        row = metrics(labels[test], pred)
        row.update({"family": fold["family"], "held_out": fold["held_out"]})
        fold_rows.append(row)
        family_true[fold["family"]].append(labels[test])
        family_pred[fold["family"]].append(pred)
    families = {
        family: metrics(np.concatenate(family_true[family]), np.concatenate(family_pred[family]))
        for family in family_true
    }
    minimum_recall = min(value for row in families.values() for value in row["class_recall"])
    passed = (
        min(row["accuracy"] for row in fold_rows) >= 0.75
        and all(row["macro_f1"] >= 0.80 for row in families.values())
        and minimum_recall >= 0.70
    )
    return {
        "pass": bool(passed),
        "minimum_fold_accuracy": min(row["accuracy"] for row in fold_rows),
        "minimum_pooled_class_recall": minimum_recall,
        "families": families,
        "folds": fold_rows,
    }


def load_samples(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    samples = []
    seen = set()
    for item in manifest["traces"]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"trace hash mismatch: {path}")
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if len(rows) != item["rows"] or len(rows) < 42:
            raise ValueError(f"trace row contract mismatch: {path}")
        if [row.get("tick") for row in rows] != list(range(len(rows))):
            raise ValueError(f"trace ticks not contiguous: {path}")
        obs = np.asarray([row.get("obs_state") for row in rows], dtype=np.float32)
        if obs.shape != (len(rows), 115) or not np.all(np.isfinite(obs)):
            raise ValueError(f"invalid obs_state corpus: {path}")
        condition, arm, step, fit = item["condition"], item["arm"], int(item["step"]), item["fit"]
        command = float(item["command_x"])
        key = (condition, arm, step, fit, f"{command:.3f}")
        if key in seen:
            raise ValueError(f"duplicate sample: {key}")
        seen.add(key)
        samples.append({
            "path": str(path), "rows": rows, "obs": obs,
            "condition": condition, "class_name": CLASS_BY_CONDITION[condition],
            "arm": arm, "step": step, "policy_key": f"{arm}_{step}",
            "fit": fit, "command_x": command, "command_key": f"{command:.3f}",
        })
    if len(samples) != 144 or len(seen) != 144:
        raise ValueError("expected exact 144-sample corpus")
    counts = {name: sum(row["class_name"] == name for row in samples) for name in CLASS_NAMES}
    if counts != {name: 48 for name in CLASS_NAMES}:
        raise ValueError(f"class count mismatch: {counts}")
    return sorted(samples, key=lambda row: row["path"])


def decode(samples: list[dict[str, Any]]) -> dict[str, Any]:
    labels = np.asarray([CLASS_NAMES.index(row["class_name"]) for row in samples])
    definitions = folds(samples)
    families = {"ACCEL3": slice(3, 6), "FULL115": slice(0, 115)}
    instantaneous: dict[str, Any] = {}
    windows: dict[str, Any] = {}
    envelopes: dict[str, Any] = {}
    for name, feature_slice in families.items():
        instantaneous[name] = {}
        for tick in TICKS:
            x = np.stack([row["obs"][tick, feature_slice] for row in samples]).astype(np.float64)
            instantaneous[name][str(tick)] = probe(x, labels, definitions)
        windows[name], envelopes[name] = {}, {}
        for end in ENDS:
            windows[name][str(end)], envelopes[name][str(end)] = {}, {}
            valid = []
            for width in WIDTHS:
                if width > end + 1:
                    continue
                x = np.stack([
                    row["obs"][end - width + 1 : end + 1, feature_slice].reshape(-1)
                    for row in samples
                ]).astype(np.float64)
                result = probe(x, labels, definitions)
                windows[name][str(end)][str(width)] = result
                valid.append(width)
            envelopes[name][str(end)] = {
                "passing_widths": [width for width in valid if windows[name][str(end)][str(width)]["pass"]],
                "any_frozen_width_passes": any(windows[name][str(end)][str(width)]["pass"] for width in valid),
            }
    persistent = [
        name for name in families
        if all(instantaneous[name][str(tick)]["pass"] for tick in range(24, 41))
    ]
    local = []
    for name in families:
        for width in [2, 4, 8, 16]:
            if all(windows[name][str(end)].get(str(width), {}).get("pass", False) for end in [24, 32, 40]):
                local.append({"feature_family": name, "width": width})
    tick0 = [name for name in families if instantaneous[name]["0"]["pass"]]
    if persistent:
        decision = "PERSISTENT_CURRENT_STATE_DECODE_UNDER_FROZEN_PROBES"
    elif local:
        decision = "LOCAL_HISTORY_DECODE_UNDER_FROZEN_PROBES"
    elif tick0:
        decision = "RESET_TRANSIENT_ONLY_UNDER_FROZEN_PROBES"
    else:
        decision = "NO_DECODE_UNDER_FROZEN_PROBES"
    return {
        "decision": decision,
        "persistent_feature_families": persistent,
        "local_history_passes": local,
        "tick0_passing_feature_families": tick0,
        "instantaneous": instantaneous,
        "windows": windows,
        "existence_envelopes": envelopes,
        "statistical_inference": False,
        "p_value": None,
    }


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))


def summarize_forks(rows: list[dict[str, Any]]) -> dict[str, float]:
    rms = [row["action_difference_rms"] for row in rows]
    maximum = [row["action_difference_max_abs"] for row in rows]
    return {
        "samples": len(rows),
        "rms_median": percentile(rms, 50), "rms_p95": percentile(rms, 95), "rms_max": max(rms),
        "max_abs_median": percentile(maximum, 50), "max_abs_p95": percentile(maximum, 95), "max_abs_max": max(maximum),
    }


def sensitivity(samples: list[dict[str, Any]]) -> dict[str, Any]:
    sessions = {}
    for key, digest in POLICIES.items():
        arm, step = key.rsplit("_", 1)
        path = POLICY_ROOT / arm / f"{key}.onnx"
        if sha256(path) != digest:
            raise ValueError(f"policy changed: {key}")
        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError(f"non-CPU provider: {key}")
        sessions[key] = session
    fork_rows, baseline_max = [], 0.0
    direction_norm = float(np.linalg.norm(COM_DIRECTION))
    for sample in samples:
        session = sessions[sample["policy_key"]]
        previous = np.zeros((1, 14), dtype=np.float32)
        for tick, (obs, record) in enumerate(zip(sample["obs"], sample["rows"], strict=True)):
            state_input = previous.copy()
            action, previous = session.run(None, {"obs": obs[None], "previous_action": state_input})
            expected = np.asarray(record["policy_raw_action"], dtype=np.float32)
            error = float(np.max(np.abs(action[0] - expected)))
            baseline_max = max(baseline_max, error)
            if error > 1e-6:
                raise ValueError(f"baseline ONNX replay mismatch {sample['path']} tick {tick}: {error}")
            if tick in FORK_TICKS:
                minus, plus = obs.copy(), obs.copy()
                minus[3:6] -= COM_DIRECTION
                plus[3:6] += COM_DIRECTION
                action_minus = session.run(None, {"obs": minus[None], "previous_action": state_input})[0][0]
                action_plus = session.run(None, {"obs": plus[None], "previous_action": state_input})[0][0]
                delta = np.asarray(action_plus - action_minus, dtype=np.float64)
                fork_rows.append({
                    "policy": sample["policy_key"], "condition": sample["condition"],
                    "fit": sample["fit"], "command_x": sample["command_x"], "tick": tick,
                    "action_difference": delta.tolist(),
                    "action_difference_rms": float(np.sqrt(np.mean(np.square(delta)))),
                    "action_difference_max_abs": float(np.max(np.abs(delta))),
                    "central_directional_slope": (delta / (2.0 * direction_norm)).tolist(),
                })
            if tick >= max(FORK_TICKS):
                break
    expected_rows = 144 * len(FORK_TICKS)
    if len(fork_rows) != expected_rows:
        raise ValueError(f"fork cardinality mismatch: {len(fork_rows)}")
    summaries = {}
    near_zero = True
    substantial = False
    for policy in sorted(POLICIES):
        selected = [row for row in fork_rows if row["policy"] == policy]
        reset = [row for row in selected if row["tick"] == 0]
        mid = [row for row in selected if row["tick"] in [24, 32, 40]]
        summaries[policy] = {
            "reset": summarize_forks(reset),
            "mid_gait": summarize_forks(mid),
            "ticks": {str(tick): summarize_forks([row for row in selected if row["tick"] == tick]) for tick in FORK_TICKS},
        }
        for band in (summaries[policy]["reset"], summaries[policy]["mid_gait"]):
            near_zero &= band["rms_p95"] <= 0.001 and band["max_abs_p95"] <= 0.004
            substantial |= band["rms_median"] >= 0.004 or band["max_abs_median"] >= 0.016
    if near_zero:
        decision = "NEAR_ZERO_ACCEL_RESPONSE"
    elif substantial:
        decision = "SUBSTANTIAL_ACCEL_RESPONSE"
    else:
        decision = "INTERMEDIATE_ACCEL_RESPONSE"
    return {
        "decision": decision,
        "measured_direction_m_s2": COM_DIRECTION.astype(float).tolist(),
        "baseline_max_abs_replay_error": baseline_max,
        "summaries": summaries,
        "forks": fork_rows,
        "corrective_sign_inferred": False,
    }


def joint_decision(decode_label: str, sensitivity_label: str) -> str:
    if sensitivity_label == "SUBSTANTIAL_ACCEL_RESPONSE":
        return "SUPPORT_PREREGISTERED_SIGNED_CAUSAL_RESPONSE_STUDY"
    if sensitivity_label != "NEAR_ZERO_ACCEL_RESPONSE":
        return "NO_ARM_FAMILY_SELECTED"
    if decode_label == "PERSISTENT_CURRENT_STATE_DECODE_UNDER_FROZEN_PROBES":
        return "SUPPORT_PREREGISTERED_OBJECTIVE_OPTIMIZATION_EXPLOITATION_STUDY"
    if decode_label in {"LOCAL_HISTORY_DECODE_UNDER_FROZEN_PROBES", "RESET_TRANSIENT_ONLY_UNDER_FROZEN_PROBES"}:
        return "SUPPORT_PREREGISTERED_MEMORY_OR_ESTIMATOR_INPUT_STUDY"
    return "NO_ARM_FAMILY_SELECTED"


def write_md(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Ground-Up Torso-COM Full-Observation and Actor-Sensitivity Result", "",
        f"status: `{payload['status']}`",
        f"decode: `{payload['decode']['decision']}`",
        f"actor sensitivity: `{payload['sensitivity']['decision']}`",
        f"decision: `{payload['decision']}`", "",
        "No p-value or independent-sample inference is reported. The actor forks change only `obs[3:6]` and do not establish corrective sign.", "",
        "| policy | reset RMS p95 | reset max p95 | mid RMS p95 | mid max p95 |", "|---|---:|---:|---:|---:|",
    ]
    for policy, row in payload["sensitivity"]["summaries"].items():
        lines.append(
            f"| {policy} | {row['reset']['rms_p95']:.8f} | {row['reset']['max_abs_p95']:.8f} | "
            f"{row['mid_gait']['rms_p95']:.8f} | {row['mid_gait']['max_abs_p95']:.8f} |"
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--replay-manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("exact CPU environment required")
    contract = json.loads(args.contract.read_text())
    if contract.get("status") != "PASS_TORSO_COM_FULL_OBS_STUDY_CONTRACT":
        raise RuntimeError("passing contract required")
    if sha256(Path(__file__)) != contract["details"]["study_tool_hashes"]["analysis"]:
        raise RuntimeError("analysis tool changed after contract")
    replay = json.loads(args.replay_manifest.read_text())
    if replay.get("status") != "PASS_EXACT_FULL_OBSERVATION_REPLAY":
        raise RuntimeError("passing exact replay required")
    samples = load_samples(replay)
    decoded = decode(samples)
    actor = sensitivity(samples)
    decision = joint_decision(decoded["decision"], actor["decision"])
    payload = {
        "schema_version": "ground_up_torso_com_full_obs_study.v1",
        "status": "PASS_TORSO_COM_FULL_OBS_STUDY_COMPLETE",
        "decision": decision,
        "decode": decoded,
        "sensitivity": actor,
        "sources": {
            "contract_sha256": sha256(args.contract),
            "replay_manifest_sha256": sha256(args.replay_manifest),
        },
        "execution": {"cpu_only": True, "training": False, "robot_or_rdk": False, "p_value": None},
        "authority": {"next_preregistration_only": True, "training": False, "gpu_or_igpu": False, "robot_or_rdk": False},
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_md(payload, args.output_md)
    print(json.dumps({"status": payload["status"], "decision": decision, "decode": decoded["decision"], "sensitivity": actor["decision"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
