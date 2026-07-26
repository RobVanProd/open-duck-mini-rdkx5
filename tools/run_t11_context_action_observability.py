#!/usr/bin/env python3
"""Run the preregistered T11 state-coherent action-observability audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t11_context_action_observability_preregistration.json"
RESULT = ANALYSIS / "t11_context_action_observability_result.json"
MARKDOWN = (
    ANALYSIS / "T11_CONTEXT_ACTION_OBSERVABILITY_RESULT_20260726.md"
)
STAGES = {
    "context_location": 14,
    "context_hidden_projected": 64,
    "raw_continuous_actions": 14,
    "first_rate_action": 14,
    "v121_preprojection_action": 14,
    "v121_final_rate_action": 14,
    "continuous_actions": 14,
    "previous_action_out": 14,
    "h_out": 64,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def validate_receipt(item: dict[str, Any]) -> None:
    path = Path(item["path"])
    if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
        raise RuntimeError(f"T11 frozen source changed: {path}")


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "formal_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    if (
        value["schema_version"]
        != "open_duck.t11_context_action_observability.v1"
        or value["status"]
        != "PREREGISTERED_T11_CONTEXT_ACTION_OBSERVABILITY"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T11 preregistration identity changed")
    for item in value["sources"].values():
        validate_receipt(item)


def add_debug_outputs(source: Path, destination: Path) -> None:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, width in STAGES.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name,
                    TensorProto.FLOAT,
                    [1, width],
                )
            )
    onnx.checker.check_model(model)
    onnx.save(model, destination)


def initializers(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(path)
    return {
        item.name: np.asarray(onnx.numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def feed(
    observation: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        "obs": observation,
        "previous_action": previous,
        "h_in": hidden,
        "calibration_context": context,
    }


def random_observation(
    rng: np.random.Generator,
    *,
    command_x: float,
) -> np.ndarray:
    observation = rng.normal(0.0, 0.2, size=(1, 115)).astype(np.float32)
    observation[:, 6] = np.float32(command_x)
    observation[:, 13:27] = rng.uniform(
        -0.1, 0.1, size=(1, 14)
    ).astype(np.float32)
    observation[:, 101:115] = rng.uniform(
        -0.8, 0.8, size=(1, 14)
    ).astype(np.float32)
    return observation


def stage_run(
    session: ort.InferenceSession,
    inputs: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    names = list(STAGES)
    return dict(zip(names, session.run(names, inputs), strict=True))


def original_test(
    session: ort.InferenceSession,
    *,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    maximum_action_delta = 0.0
    maximum_hidden_delta = 0.0
    for _ in range(cases):
        observation = random_observation(rng, command_x=0.077)
        previous = rng.uniform(-0.3, 0.3, size=(1, 14)).astype(np.float32)
        hidden = rng.uniform(-0.5, 0.5, size=(1, 64)).astype(np.float32)
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        first = stage_run(
            session,
            feed(
                observation,
                previous,
                hidden,
                np.zeros((1, 64), dtype=np.float32),
            ),
        )
        second = stage_run(
            session,
            feed(observation, previous, hidden, context),
        )
        maximum_action_delta = max(
            maximum_action_delta,
            float(
                np.max(
                    np.abs(
                        first["continuous_actions"]
                        - second["continuous_actions"]
                    )
                )
            ),
        )
        maximum_hidden_delta = max(
            maximum_hidden_delta,
            float(np.max(np.abs(first["h_out"] - second["h_out"]))),
        )
    return {
        "seed": seed,
        "cases": cases,
        "maximum_action_delta": maximum_action_delta,
        "maximum_hidden_delta": maximum_hidden_delta,
    }


def coherent_test(
    session: ort.InferenceSession,
    *,
    seed: int,
    cases: int,
    max_action_delta: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    stage_maximum = {name: 0.0 for name in STAGES}
    effective_cases = 0
    x0_exact = True
    maximum_rate_excess = 0.0
    maximum_previous_error = 0.0
    for _ in range(cases):
        observation = random_observation(rng, command_x=0.077)
        hidden = rng.uniform(-0.5, 0.5, size=(1, 64)).astype(np.float32)
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        zero = np.zeros((1, 64), dtype=np.float32)
        probe = stage_run(
            session,
            feed(
                observation,
                np.zeros((1, 14), dtype=np.float32),
                hidden,
                zero,
            ),
        )
        previous = np.asarray(
            probe["raw_continuous_actions"], dtype=np.float32
        )
        first = stage_run(
            session,
            feed(observation, previous, hidden, zero),
        )
        second = stage_run(
            session,
            feed(observation, previous, hidden, context),
        )
        for name in STAGES:
            stage_maximum[name] = max(
                stage_maximum[name],
                float(np.max(np.abs(first[name] - second[name]))),
            )
        final_delta = float(
            np.max(
                np.abs(
                    first["continuous_actions"]
                    - second["continuous_actions"]
                )
            )
        )
        effective_cases += int(final_delta > 1.0e-8)
        for output in (first, second):
            maximum_rate_excess = max(
                maximum_rate_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(output["continuous_actions"] - previous)
                            - max_action_delta,
                            0.0,
                        )
                    )
                ),
            )
            maximum_previous_error = max(
                maximum_previous_error,
                float(
                    np.max(
                        np.abs(
                            output["continuous_actions"]
                            - output["previous_action_out"]
                        )
                    )
                ),
            )
        zero_observation = observation.copy()
        zero_observation[:, 6] = 0.0
        zero_output = stage_run(
            session,
            feed(zero_observation, previous, hidden, context),
        )
        x0_exact &= np.count_nonzero(zero_output["continuous_actions"]) == 0
    return {
        "seed": seed,
        "cases": cases,
        "stage_maximum_abs_delta": stage_maximum,
        "effective_cases": effective_cases,
        "effective_case_fraction": effective_cases / cases,
        "maximum_rate_excess": maximum_rate_excess,
        "maximum_previous_action_error": maximum_previous_error,
        "x0_exact_zero": bool(x0_exact),
    }


def sequence_test(
    session: ort.InferenceSession,
    *,
    seed: int,
    sequences: int,
    ticks: int,
    max_action_delta: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    divergent = 0
    maximum_action_delta = 0.0
    maximum_rate_excess = 0.0
    for _ in range(sequences):
        previous = [
            np.zeros((1, 14), dtype=np.float32),
            np.zeros((1, 14), dtype=np.float32),
        ]
        hidden = [
            np.zeros((1, 64), dtype=np.float32),
            np.zeros((1, 64), dtype=np.float32),
        ]
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        sequence_delta = 0.0
        for _ in range(ticks):
            observation = random_observation(rng, command_x=0.077)
            outputs = []
            for branch, branch_context in enumerate(
                (np.zeros((1, 64), dtype=np.float32), context)
            ):
                output = stage_run(
                    session,
                    feed(
                        observation,
                        previous[branch],
                        hidden[branch],
                        branch_context,
                    ),
                )
                maximum_rate_excess = max(
                    maximum_rate_excess,
                    float(
                        np.max(
                            np.maximum(
                                np.abs(
                                    output["continuous_actions"]
                                    - previous[branch]
                                )
                                - max_action_delta,
                                0.0,
                            )
                        )
                    ),
                )
                outputs.append(output)
            delta = float(
                np.max(
                    np.abs(
                        outputs[0]["continuous_actions"]
                        - outputs[1]["continuous_actions"]
                    )
                )
            )
            sequence_delta = max(sequence_delta, delta)
            maximum_action_delta = max(maximum_action_delta, delta)
            for branch, output in enumerate(outputs):
                previous[branch] = output["previous_action_out"]
                hidden[branch] = output["h_out"]
        divergent += int(sequence_delta > 1.0e-8)
    return {
        "seed": seed,
        "sequences": sequences,
        "ticks": ticks,
        "divergent_sequences": divergent,
        "divergent_sequence_fraction": divergent / sequences,
        "maximum_action_delta": maximum_action_delta,
        "maximum_rate_excess": maximum_rate_excess,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_training_authorized:
        raise PermissionError(
            "T11 requires --offline-cpu-only --zero-training-authorized"
        )
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T11 result")
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing to reuse T11 work root: {work}")
    work.mkdir(parents=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    source = Path(prereg["sources"]["t10_final_onnx"]["path"])
    debug = work / "t11_final_debug.onnx"
    add_debug_outputs(source, debug)
    session = ort.InferenceSession(
        str(debug), providers=["CPUExecutionProvider"]
    )
    values = initializers(source)
    contract = prereg["formal_contract"]
    original = original_test(
        session,
        **{
            key: contract["original_test_reproduction"][key]
            for key in ("seed", "cases")
        },
    )
    coherent = coherent_test(
        session,
        seed=contract["disjoint_state_coherent_test"]["seed"],
        cases=contract["disjoint_state_coherent_test"]["cases"],
        max_action_delta=values["max_action_delta"],
    )
    sequence = sequence_test(
        session,
        seed=contract["disjoint_causal_sequence_test"]["seed"],
        sequences=contract["disjoint_causal_sequence_test"]["sequences"],
        ticks=contract["disjoint_causal_sequence_test"]["ticks"],
        max_action_delta=values["max_action_delta"],
    )
    thresholds = contract["disjoint_state_coherent_test"]
    sequence_thresholds = contract["disjoint_causal_sequence_test"]
    checks = {
        "cpu_provider": session.get_providers() == ["CPUExecutionProvider"],
        "original_random_previous_hold_reproduced": (
            original["maximum_action_delta"]
            == contract["original_test_reproduction"]["expected_final_delta"]
        ),
        "original_context_state_effect_reproduced": (
            original["maximum_hidden_delta"] > 1.0e-8
        ),
        "coherent_context_location_effect": (
            coherent["stage_maximum_abs_delta"]["context_location"]
            > thresholds["minimum_context_location_delta"]
        ),
        "coherent_raw_action_effect": (
            coherent["stage_maximum_abs_delta"]["raw_continuous_actions"]
            > thresholds["minimum_raw_action_delta"]
        ),
        "coherent_final_action_effect": (
            coherent["stage_maximum_abs_delta"]["continuous_actions"]
            > thresholds["minimum_final_action_delta"]
        ),
        "coherent_effect_frequency": (
            coherent["effective_case_fraction"]
            >= thresholds["minimum_effective_case_fraction"]
        ),
        "causal_sequence_effect_frequency": (
            sequence["divergent_sequence_fraction"]
            >= sequence_thresholds[
                "minimum_divergent_sequence_fraction"
            ]
        ),
        "x0_context_invariant": coherent["x0_exact_zero"],
        "rate_projection_preserved": (
            coherent["maximum_rate_excess"]
            <= contract["rate_excess_tolerance"]
            and sequence["maximum_rate_excess"]
            <= contract["rate_excess_tolerance"]
        ),
        "graph_owned_previous_action": (
            coherent["maximum_previous_action_error"] == 0.0
        ),
        "optimizer_steps_zero": True,
        "behavior_cells_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    passed = not failed
    basis = {
        "schema_version": "open_duck.t11_context_action_result.v1",
        "status": (
            "PASS_T11_CONTEXT_ACTION_OBSERVABILITY"
            if passed
            else "HOLD_T11_CONTEXT_ACTION_OBSERVABILITY"
        ),
        "decision": (
            "EARN_SEPARATE_HOSTED_CONTINUATION_PREREGISTRATION"
            if passed
            else "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_graph": prereg["sources"]["t10_final_onnx"],
        "debug_graph": {
            "path": str(debug),
            "bytes": debug.stat().st_size,
            "sha256": sha256(debug),
        },
        "original_state_incoherent_test": original,
        "disjoint_state_coherent_test": coherent,
        "disjoint_causal_sequence_test": sequence,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T11 context-action observability result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Original random-previous final delta: "
        f"`{original['maximum_action_delta']:.9g}`\n"
        f"- Disjoint coherent final delta: "
        f"`{coherent['stage_maximum_abs_delta']['continuous_actions']:.9g}`\n"
        f"- Coherent effective cases: "
        f"`{coherent['effective_cases']}/{coherent['cases']}`\n"
        f"- Causal divergent sequences: "
        f"`{sequence['divergent_sequences']}/{sequence['sequences']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Optimizer/behavior/hosted/robot execution: `0/0/0/0`\n"
        f"- Canonical SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    print(f"file_sha256={sha256(RESULT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
