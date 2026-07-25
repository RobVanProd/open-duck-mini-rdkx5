#!/usr/bin/env python3
"""Run the preregistered, coverage-aware T3 observation z-score audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t3_observation_zscore_v2_preregistration.json"
OUTPUT = ANALYSIS / "t3_observation_zscore_v2_result.json"
MARKDOWN = ANALYSIS / "T3_OBSERVATION_ZSCORE_V2_RESULT_20260725.md"
JOINTS = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def channel_names() -> list[str]:
    result = [
        "gyro_x_rad_s",
        "gyro_y_rad_s",
        "gyro_z_rad_s",
        "accel_x_m_s2",
        "accel_y_m_s2",
        "accel_z_m_s2",
    ]
    result.extend(
        [
            "command_x_m_s",
            "command_y_m_s",
            "command_yaw_rad_s",
            "command_neck_pitch",
            "command_head_pitch",
            "command_head_yaw",
            "command_head_roll",
        ]
    )
    result.extend(f"position_error_{name}_rad" for name in JOINTS)
    result.extend(f"velocity_scaled_{name}" for name in JOINTS)
    result.extend(f"action_t_minus_1_{name}" for name in JOINTS)
    result.extend(f"action_t_minus_2_{name}" for name in JOINTS)
    result.extend(f"action_t_minus_3_{name}" for name in JOINTS)
    result.extend(f"previous_target_{name}_rad" for name in JOINTS)
    result.extend(["contact_left", "contact_right", "phase_cos", "phase_sin"])
    if len(result) != 101:
        raise AssertionError(f"channel map has {len(result)} entries")
    return result


@dataclass
class SourceSeries:
    source_id: str
    evidence_kind: str
    values: dict[int, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    complete_policy_observations: int = 0
    rejected_stale_samples: int = 0

    def add_vector(self, vector: Any) -> None:
        array = np.asarray(vector, dtype=np.float64)
        if array.shape != (101,) or not np.all(np.isfinite(array)):
            raise ValueError(
                f"{self.source_id}: invalid complete observation {array.shape}"
            )
        for index, value in enumerate(array):
            self.values[index].append(float(value))
        self.complete_policy_observations += 1

    def add(self, index: int, value: Any) -> None:
        number = float(value)
        if not np.isfinite(number):
            raise ValueError(f"{self.source_id}: non-finite obs[{index}]")
        self.values[index].append(number)


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc


def load_normalizer(prereg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    policy = Path(prereg["input_paths"]["policy"])
    model = onnx.load(str(policy), load_external_data=False)
    arrays = {
        initializer.name: numpy_helper.to_array(initializer).astype(
            np.float64
        )
        for initializer in model.graph.initializer
    }
    contract = prereg["normalizer_contract"]
    mean_name = contract["mean_initializer"]
    recip_name = contract["reciprocal_std_initializer"]
    if mean_name not in arrays or recip_name not in arrays:
        raise RuntimeError(
            "normalizer initializer missing: "
            f"{mean_name in arrays=}, {recip_name in arrays=}"
        )
    mean = arrays[mean_name]
    reciprocal_std = arrays[recip_name]
    if mean.shape != (101,) or reciprocal_std.shape != (101,):
        raise RuntimeError(
            "normalizer shape mismatch: "
            f"mean={mean.shape}, reciprocal_std={reciprocal_std.shape}"
        )
    if not np.all(np.isfinite(mean)) or not np.all(
        np.isfinite(reciprocal_std)
    ):
        raise RuntimeError("normalizer contains non-finite values")
    if np.any(reciprocal_std <= 0):
        raise RuntimeError("normalizer reciprocal std is not positive")
    return mean, reciprocal_std


def verify_inputs(prereg: dict[str, Any]) -> None:
    if prereg["status"] != "PREREGISTERED_T3_V2_OBSERVATION_ZSCORE_AUDIT":
        raise RuntimeError(f"invalid preregistration: {prereg['status']}")
    for name, expected in prereg["input_sha256"].items():
        path = Path(prereg["input_paths"][name])
        if not path.is_file():
            raise FileNotFoundError(f"missing preregistered input: {path}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(
                f"input hash changed for {name}: {actual} != {expected}"
            )


def load_complete_observation_sources(
    prereg: dict[str, Any],
) -> list[SourceSeries]:
    sources: list[SourceSeries] = []
    golden = json.loads(
        Path(prereg["input_paths"]["golden"]).read_text(encoding="utf-8")
    )
    for key in ("prior", "current"):
        source = SourceSeries(
            f"legacy_suspended_replay_20260621_{key}",
            "complete_policy_observation",
        )
        observation = golden[key]["observation"]
        if observation.get("normalization_error") is None:
            raise RuntimeError(
                "historical swallowed-normalization-error evidence changed"
            )
        source.add_vector(observation["raw_vector"])
        sources.append(source)

    corrected = json.loads(
        Path(prereg["input_paths"]["corrected_contract"]).read_text(
            encoding="utf-8"
        )
    )
    source = SourceSeries(
        "corrected_knee_suspended_replay_20260627",
        "complete_policy_observation",
    )
    source.add_vector(corrected["legacy_outputs"]["observation"])
    sources.append(source)
    return sources


def load_gate3_sources(prereg: dict[str, Any]) -> list[SourceSeries]:
    sources: list[SourceSeries] = []
    names = sorted(
        key.removeprefix("gate3_sensor_")
        for key in prereg["input_paths"]
        if key.startswith("gate3_sensor_")
    )
    for label in names:
        source = SourceSeries(
            f"gate3_{label}", "direct_sensor_component_capture"
        )
        path = Path(prereg["input_paths"][f"gate3_sensor_{label}"])
        for record in read_jsonl(path):
            imu = record["imu"]
            contacts = record["contacts"]
            if imu.get("stale") or contacts.get("stale"):
                source.rejected_stale_samples += 1
                continue
            for index, value in enumerate(imu["gyro_rad_s"]):
                source.add(index, value)
            for offset, value in enumerate(imu["acceleration_m_s2"]):
                source.add(3 + offset, value)
            source.add(97, contacts["left"])
            source.add(98, contacts["right"])
        sources.append(source)
    return sources


def longest_true_run(values: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in values:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def summarize(
    sources: list[SourceSeries],
    mean: np.ndarray,
    reciprocal_std: np.ndarray,
    threshold: float,
    sustained_samples: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels = channel_names()
    rows: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for index, label in enumerate(labels):
        all_z: list[float] = []
        complete_count = 0
        component_count = 0
        source_rows = []
        for source in sources:
            raw = source.values.get(index, [])
            if not raw:
                continue
            z = (
                np.asarray(raw, dtype=np.float64) - mean[index]
            ) * reciprocal_std[index]
            all_z.extend(float(value) for value in z)
            if source.evidence_kind == "complete_policy_observation":
                complete_count += len(z)
            else:
                component_count += len(z)
            longest = longest_true_run(np.abs(z) > threshold)
            source_row = {
                "source_id": source.source_id,
                "evidence_kind": source.evidence_kind,
                "samples": int(len(z)),
                "raw_p50": float(np.percentile(raw, 50)),
                "signed_z_p50": float(np.percentile(z, 50)),
                "absolute_z_p50": float(np.percentile(np.abs(z), 50)),
                "absolute_z_p95": float(np.percentile(np.abs(z), 95)),
                "absolute_z_max": float(np.max(np.abs(z))),
                "longest_consecutive_abs_z_over_threshold": longest,
                "sustained": longest >= sustained_samples,
            }
            source_rows.append(source_row)
            if source_row["sustained"]:
                violations.append(
                    {
                        "index": index,
                        "channel": label,
                        **source_row,
                    }
                )
        if all_z:
            values = np.asarray(all_z, dtype=np.float64)
            abs_values = np.abs(values)
            row = {
                "index": index,
                "channel": label,
                "mean": float(mean[index]),
                "reciprocal_std": float(reciprocal_std[index]),
                "std": float(1.0 / reciprocal_std[index]),
                "sample_count": int(len(values)),
                "complete_observation_samples": complete_count,
                "component_samples": component_count,
                "source_count": len(source_rows),
                "signed_z_p50": float(np.percentile(values, 50)),
                "absolute_z_p50": float(np.percentile(abs_values, 50)),
                "absolute_z_p95": float(np.percentile(abs_values, 95)),
                "absolute_z_max": float(np.max(abs_values)),
                "sustained_source_count": sum(
                    int(item["sustained"]) for item in source_rows
                ),
                "sources": source_rows,
            }
        else:
            row = {
                "index": index,
                "channel": label,
                "mean": float(mean[index]),
                "reciprocal_std": float(reciprocal_std[index]),
                "std": float(1.0 / reciprocal_std[index]),
                "sample_count": 0,
                "complete_observation_samples": 0,
                "component_samples": 0,
                "source_count": 0,
                "signed_z_p50": None,
                "absolute_z_p50": None,
                "absolute_z_p95": None,
                "absolute_z_max": None,
                "sustained_source_count": 0,
                "sources": [],
            }
        rows.append(row)
    rows.sort(
        key=lambda item: (
            item["absolute_z_max"] is not None,
            item["absolute_z_max"]
            if item["absolute_z_max"] is not None
            else -1.0,
        ),
        reverse=True,
    )
    violations.sort(
        key=lambda item: (
            item["absolute_z_p50"],
            item["absolute_z_max"],
        ),
        reverse=True,
    )
    return rows, violations


def fmt(value: float | None) -> str:
    return "NA" if value is None else f"{value:.6f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_inputs(prereg)
    mean, reciprocal_std = load_normalizer(prereg)
    sources = load_complete_observation_sources(prereg)
    sources.extend(load_gate3_sources(prereg))
    threshold = float(prereg["analysis"]["threshold_absolute_z"])
    sustained_samples = int(
        prereg["analysis"]["minimum_sustained_samples"]
    )
    rows, violations = summarize(
        sources,
        mean,
        reciprocal_std,
        threshold,
        sustained_samples,
    )
    complete_coverage = all(
        row["complete_observation_samples"] >= sustained_samples for row in rows
    )
    uncovered = [
        row["index"] for row in rows if row["sample_count"] == 0
    ]
    insufficient_complete = [
        row["index"]
        for row in rows
        if row["complete_observation_samples"] < sustained_samples
    ]
    accel_x_row = next(row for row in rows if row["index"] == 3)
    accel_x_sources = {
        row["source_id"]: row for row in accel_x_row["sources"]
    }
    upright_accel_x = accel_x_sources["gate3_upright"]
    corrected_accel_x = accel_x_sources[
        "corrected_knee_suspended_replay_20260627"
    ]
    legacy_current_accel_x = accel_x_sources[
        "legacy_suspended_replay_20260621_current"
    ]
    if violations and not complete_coverage:
        status = "HOLD_T3_V2_VIOLATIONS_AND_INCOMPLETE_REAL_OBS_COVERAGE"
    elif violations:
        status = "HOLD_T3_V2_SUSTAINED_OBSERVATION_CONTRACT_VIOLATIONS"
    elif not complete_coverage:
        status = "HOLD_T3_V2_INCOMPLETE_REAL_OBSERVATION_COVERAGE"
    else:
        status = "PASS_T3_V2_OBSERVATION_ZSCORE_AUDIT"
    payload = {
        "schema_version": "open_duck.t3_observation_zscore_result.v2",
        "status": status,
        "preregistration_path": str(PREREG.relative_to(ROOT)),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "policy_sha256": prereg["input_sha256"]["policy"],
        "normalizer": {
            "mean_initializer": prereg["normalizer_contract"][
                "mean_initializer"
            ],
            "reciprocal_std_initializer": prereg["normalizer_contract"][
                "reciprocal_std_initializer"
            ],
            "mean": mean.tolist(),
            "reciprocal_std": reciprocal_std.tolist(),
            "std": (1.0 / reciprocal_std).tolist(),
        },
        "source_summary": [
            {
                "source_id": source.source_id,
                "evidence_kind": source.evidence_kind,
                "complete_policy_observations": (
                    source.complete_policy_observations
                ),
                "covered_channel_count": len(source.values),
                "rejected_stale_samples": source.rejected_stale_samples,
                "samples_by_channel_min": (
                    min(map(len, source.values.values()))
                    if source.values
                    else 0
                ),
                "samples_by_channel_max": (
                    max(map(len, source.values.values()))
                    if source.values
                    else 0
                ),
            }
            for source in sources
        ],
        "coverage": {
            "complete": complete_coverage,
            "required_complete_samples_per_channel": sustained_samples,
            "uncovered_channel_indices": sorted(uncovered),
            "insufficient_complete_observation_channel_indices": sorted(
                insufficient_complete
            ),
            "claim_obs3_is_only_violation_authorized": (
                complete_coverage
                and {item["index"] for item in violations} == {3}
            ),
            "raw_corrected_replay_available": False,
        },
        "decision": {
            "threshold_absolute_z": threshold,
            "sustained_samples": sustained_samples,
            "violation_count": len(violations),
            "violating_channel_indices": sorted(
                {item["index"] for item in violations}
            ),
            "violations": violations,
            "selection_weight": 0,
        },
        "key_findings": {
            "calibrated_gate3_upright_accel_x": {
                "samples": upright_accel_x["samples"],
                "raw_p50_m_s2": upright_accel_x["raw_p50"],
                "signed_z_p50": upright_accel_x["signed_z_p50"],
                "absolute_z_p95": upright_accel_x["absolute_z_p95"],
                "longest_consecutive_abs_z_over_0p5": upright_accel_x[
                    "longest_consecutive_abs_z_over_threshold"
                ],
                "sustained_violation": upright_accel_x["sustained"],
            },
            "sparse_suspended_accel_x": {
                "legacy_20260621_current_raw_m_s2": (
                    legacy_current_accel_x["raw_p50"]
                ),
                "legacy_20260621_current_z": legacy_current_accel_x[
                    "signed_z_p50"
                ],
                "corrected_20260627_raw_m_s2": corrected_accel_x["raw_p50"],
                "corrected_20260627_z": corrected_accel_x["signed_z_p50"],
                "samples_each": 1,
                "sustained_conclusion_authorized": False,
            },
            "interpretation": (
                "The hash-frozen calibrated Gate-3 upright capture does not "
                "show a sustained obs[3] violation. Two sparse suspended "
                "snapshots are above 0.5 z, but the missing replay prevents "
                "deciding whether that condition persisted."
            ),
        },
        "channels_sorted_by_absolute_z_max": rows,
        "authority": prereg["authority"],
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    table = [
        "| rank | obs | channel | samples | complete | |z| p50 | |z| p95 | |z| max | sustained sources |",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(rows, start=1):
        table.append(
            f"| {rank} | {row['index']} | `{row['channel']}` | "
            f"{row['sample_count']} | {row['complete_observation_samples']} | "
            f"{fmt(row['absolute_z_p50'])} | "
            f"{fmt(row['absolute_z_p95'])} | "
            f"{fmt(row['absolute_z_max'])} | "
            f"{row['sustained_source_count']} |"
        )
    violation_lines = (
        "\n".join(
            f"- `obs[{item['index']}] {item['channel']}` in "
            f"`{item['source_id']}`: longest run "
            f"{item['longest_consecutive_abs_z_over_threshold']} samples, "
            f"median `|z|={item['absolute_z_p50']:.4f}`."
            for item in violations
        )
        if violations
        else "- None."
    )
    MARKDOWN.write_text(
        "# T3 observation z-score v2 result\n\n"
        f"- Status: `{status}`\n"
        f"- Policy SHA-256: `{payload['policy_sha256']}`\n"
        f"- Sustained threshold: `|z| > {threshold}` for "
        f"`{sustained_samples}` consecutive samples.\n"
        f"- Complete-observation coverage: `{complete_coverage}`.\n"
        f"- Sustained source-level flags: `{len(violations)}`.\n"
        f"- Calibrated Gate 3 upright `obs[3]`: median "
        f"`{upright_accel_x['raw_p50']:.4f} m/s^2`, median "
        f"`z={upright_accel_x['signed_z_p50']:.4f}`, longest violation run "
        f"`{upright_accel_x['longest_consecutive_abs_z_over_threshold']}` "
        "ticks—there is no sustained upright `obs[3]` violation in this "
        "capture.\n"
        f"- Sparse suspended snapshots: legacy current `obs[3]="
        f"{legacy_current_accel_x['raw_p50']:.2f}` "
        f"(`z={legacy_current_accel_x['signed_z_p50']:.3f}`), corrected "
        f"`obs[3]={corrected_accel_x['raw_p50']:.2f}` "
        f"(`z={corrected_accel_x['signed_z_p50']:.3f}`); one sample each "
        "cannot establish persistence.\n"
        "- The historical telemetry's swallowed ONNX import error is "
        "confirmed; the runtime/diagnostic path now fails before capture.\n\n"
        "## Sustained flags\n\n"
        f"{violation_lines}\n\n"
        "## 101-channel table\n\n"
        + "\n".join(table)
        + "\n\n"
        "## Interpretation\n\n"
        "The available archive does not contain the full 747-tick corrected "
        "policy replay. Component captures are reported without filling "
        "unrecorded fields. Therefore this result cannot authorize the claim "
        "that `obs[3]` is the only real-observation violation; it identifies "
        "measured candidates and preserves the missing-data hold.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"violations={len(violations)}")
    print(f"complete_coverage={complete_coverage}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
