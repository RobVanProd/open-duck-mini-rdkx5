#!/usr/bin/env python3
"""Independently audit the frozen T11 context-action observability result."""

from __future__ import annotations

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
AUDIT = (
    ANALYSIS / "t11_context_action_observability_independent_audit.json"
)
MARKDOWN = (
    ANALYSIS
    / "T11_CONTEXT_ACTION_OBSERVABILITY_INDEPENDENT_AUDIT_20260726.md"
)
DEBUG = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t10_response_conditioned_cpu_contract_v2"
    r"\t11_independent_debug.onnx"
)
OUTPUTS = {
    "context_location": 14,
    "raw_continuous_actions": 14,
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


def make_debug(source: Path) -> None:
    if DEBUG.exists():
        raise FileExistsError(f"refusing to overwrite {DEBUG}")
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, width in OUTPUTS.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name,
                    TensorProto.FLOAT,
                    [1, width],
                )
            )
    onnx.checker.check_model(model)
    onnx.save(model, DEBUG)


def observation(
    rng: np.random.Generator,
    command_x: float,
) -> np.ndarray:
    value = rng.normal(0.0, 0.2, size=(1, 115)).astype(np.float32)
    value[:, 6] = np.float32(command_x)
    value[:, 13:27] = rng.uniform(-0.1, 0.1, size=(1, 14))
    value[:, 101:115] = rng.uniform(-0.8, 0.8, size=(1, 14))
    return value


def run(
    session: ort.InferenceSession,
    obs: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> dict[str, np.ndarray]:
    names = list(OUTPUTS)
    values = session.run(
        names,
        {
            "obs": obs,
            "previous_action": previous,
            "h_in": hidden,
            "calibration_context": context,
        },
    )
    return dict(zip(names, values, strict=True))


def reproduce_original(
    session: ort.InferenceSession,
    seed: int,
    cases: int,
) -> dict[str, float]:
    rng = np.random.Generator(np.random.PCG64(seed))
    action_delta = 0.0
    hidden_delta = 0.0
    for _ in range(cases):
        obs = observation(rng, 0.077)
        previous = rng.uniform(-0.3, 0.3, size=(1, 14)).astype(np.float32)
        hidden = rng.uniform(-0.5, 0.5, size=(1, 64)).astype(np.float32)
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        zero = run(
            session,
            obs,
            previous,
            hidden,
            np.zeros((1, 64), dtype=np.float32),
        )
        conditioned = run(
            session, obs, previous, hidden, context
        )
        action_delta = max(
            action_delta,
            float(
                np.max(
                    np.abs(
                        zero["continuous_actions"]
                        - conditioned["continuous_actions"]
                    )
                )
            ),
        )
        hidden_delta = max(
            hidden_delta,
            float(
                np.max(np.abs(zero["h_out"] - conditioned["h_out"]))
            ),
        )
    return {
        "maximum_action_delta": action_delta,
        "maximum_hidden_delta": hidden_delta,
    }


def coherent(
    session: ort.InferenceSession,
    seed: int,
    cases: int,
    maximum_rate: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    maxima = {name: 0.0 for name in OUTPUTS}
    effective = 0
    rate_excess = 0.0
    previous_error = 0.0
    x0_exact = True
    for _ in range(cases):
        obs = observation(rng, 0.077)
        hidden = rng.uniform(-0.5, 0.5, size=(1, 64)).astype(np.float32)
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        zeros = np.zeros((1, 64), dtype=np.float32)
        raw = run(
            session,
            obs,
            np.zeros((1, 14), dtype=np.float32),
            hidden,
            zeros,
        )["raw_continuous_actions"]
        left = run(session, obs, raw, hidden, zeros)
        right = run(session, obs, raw, hidden, context)
        for name in OUTPUTS:
            maxima[name] = max(
                maxima[name],
                float(np.max(np.abs(left[name] - right[name]))),
            )
        effective += int(
            np.max(
                np.abs(
                    left["continuous_actions"]
                    - right["continuous_actions"]
                )
            )
            > 1.0e-8
        )
        for item in (left, right):
            rate_excess = max(
                rate_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(item["continuous_actions"] - raw)
                            - maximum_rate,
                            0.0,
                        )
                    )
                ),
            )
            previous_error = max(
                previous_error,
                float(
                    np.max(
                        np.abs(
                            item["continuous_actions"]
                            - item["previous_action_out"]
                        )
                    )
                ),
            )
        zero_obs = obs.copy()
        zero_obs[:, 6] = 0.0
        zero_result = run(session, zero_obs, raw, hidden, context)
        x0_exact &= np.count_nonzero(
            zero_result["continuous_actions"]
        ) == 0
    return {
        "stage_maximum_abs_delta": maxima,
        "effective_cases": effective,
        "effective_case_fraction": effective / cases,
        "maximum_rate_excess": rate_excess,
        "maximum_previous_action_error": previous_error,
        "x0_exact_zero": bool(x0_exact),
    }


def sequences(
    session: ort.InferenceSession,
    seed: int,
    count: int,
    ticks: int,
    maximum_rate: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    divergent = 0
    maximum_delta = 0.0
    rate_excess = 0.0
    for _ in range(count):
        previous = [
            np.zeros((1, 14), dtype=np.float32),
            np.zeros((1, 14), dtype=np.float32),
        ]
        hidden = [
            np.zeros((1, 64), dtype=np.float32),
            np.zeros((1, 64), dtype=np.float32),
        ]
        context = rng.normal(0.0, 0.7, size=(1, 64)).astype(np.float32)
        observed = 0.0
        for _ in range(ticks):
            obs = observation(rng, 0.077)
            branch = []
            for index, value in enumerate(
                (np.zeros((1, 64), dtype=np.float32), context)
            ):
                item = run(
                    session,
                    obs,
                    previous[index],
                    hidden[index],
                    value,
                )
                rate_excess = max(
                    rate_excess,
                    float(
                        np.max(
                            np.maximum(
                                np.abs(
                                    item["continuous_actions"]
                                    - previous[index]
                                )
                                - maximum_rate,
                                0.0,
                            )
                        )
                    ),
                )
                branch.append(item)
            delta = float(
                np.max(
                    np.abs(
                        branch[0]["continuous_actions"]
                        - branch[1]["continuous_actions"]
                    )
                )
            )
            observed = max(observed, delta)
            maximum_delta = max(maximum_delta, delta)
            for index, item in enumerate(branch):
                previous[index] = item["previous_action_out"]
                hidden[index] = item["h_out"]
        divergent += int(observed > 1.0e-8)
    return {
        "divergent_sequences": divergent,
        "divergent_sequence_fraction": divergent / count,
        "maximum_action_delta": maximum_delta,
        "maximum_rate_excess": rate_excess,
    }


def append_if(issues: list[str], condition: bool, name: str) -> None:
    if not condition:
        issues.append(name)


def main() -> int:
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T11 independent audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg_basis = {
        key: prereg[key]
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
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    issues: list[str] = []
    append_if(
        issues,
        canonical_sha256(prereg_basis)
        == prereg["preregistered_contract_sha256"],
        "preregistration_canonical",
    )
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result_canonical",
    )
    for name, item in prereg["sources"].items():
        path = Path(item["path"])
        append_if(
            issues,
            path.is_file()
            and path.stat().st_size == item["bytes"]
            and sha256(path) == item["sha256"],
            f"source:{name}",
        )

    source = Path(prereg["sources"]["t10_final_onnx"]["path"])
    make_debug(source)
    session = ort.InferenceSession(
        str(DEBUG), providers=["CPUExecutionProvider"]
    )
    model = onnx.load(source)
    values = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item))
        for item in model.graph.initializer
    }
    contract = prereg["formal_contract"]
    original_contract = contract["original_test_reproduction"]
    coherent_contract = contract["disjoint_state_coherent_test"]
    sequence_contract = contract["disjoint_causal_sequence_test"]
    original = reproduce_original(
        session,
        original_contract["seed"],
        original_contract["cases"],
    )
    coherent_value = coherent(
        session,
        coherent_contract["seed"],
        coherent_contract["cases"],
        values["max_action_delta"],
    )
    sequence_value = sequences(
        session,
        sequence_contract["seed"],
        sequence_contract["sequences"],
        sequence_contract["ticks"],
        values["max_action_delta"],
    )
    append_if(
        issues,
        session.get_providers() == ["CPUExecutionProvider"],
        "cpu_provider",
    )
    append_if(
        issues,
        original["maximum_action_delta"]
        == original_contract["expected_final_delta"],
        "original_hold_reproduction",
    )
    append_if(
        issues,
        original["maximum_hidden_delta"] > 1.0e-8,
        "original_hidden_effect",
    )
    maxima = coherent_value["stage_maximum_abs_delta"]
    append_if(
        issues,
        maxima["context_location"]
        > coherent_contract["minimum_context_location_delta"],
        "coherent_context_location",
    )
    append_if(
        issues,
        maxima["raw_continuous_actions"]
        > coherent_contract["minimum_raw_action_delta"],
        "coherent_raw_action",
    )
    append_if(
        issues,
        maxima["continuous_actions"]
        > coherent_contract["minimum_final_action_delta"],
        "coherent_final_action",
    )
    append_if(
        issues,
        coherent_value["effective_case_fraction"]
        >= coherent_contract["minimum_effective_case_fraction"],
        "coherent_effect_frequency",
    )
    append_if(
        issues,
        sequence_value["divergent_sequence_fraction"]
        >= sequence_contract["minimum_divergent_sequence_fraction"],
        "causal_sequence_frequency",
    )
    append_if(
        issues,
        coherent_value["x0_exact_zero"],
        "x0_context_invariance",
    )
    append_if(
        issues,
        coherent_value["maximum_rate_excess"]
        <= contract["rate_excess_tolerance"]
        and sequence_value["maximum_rate_excess"]
        <= contract["rate_excess_tolerance"],
        "rate_projection",
    )
    append_if(
        issues,
        coherent_value["maximum_previous_action_error"] == 0.0,
        "graph_owned_previous_action",
    )
    passed = not issues
    basis = {
        "schema_version": "open_duck.t11_context_action_audit.v1",
        "status": (
            "PASS_T11_CONTEXT_ACTION_INDEPENDENT_AUDIT"
            if passed
            else "HOLD_T11_CONTEXT_ACTION_INDEPENDENT_AUDIT"
        ),
        "decision": (
            "EARN_SEPARATE_HOSTED_CONTINUATION_PREREGISTRATION"
            if passed
            else "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "result_sha256": result["result_sha256"],
        "original_recomputation": original,
        "coherent_recomputation": coherent_value,
        "sequence_recomputation": sequence_value,
        "issues": issues,
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "audit_sha256": canonical_sha256(basis)}
    AUDIT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T11 context-action independent audit\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Issues: `{issues}`\n"
        f"- Coherent final delta: "
        f"`{coherent_value['stage_maximum_abs_delta']['continuous_actions']:.9g}`\n"
        f"- Coherent cases: "
        f"`{coherent_value['effective_cases']}/"
        f"{coherent_contract['cases']}`\n"
        f"- Causal sequences: "
        f"`{sequence_value['divergent_sequences']}/"
        f"{sequence_contract['sequences']}`\n"
        "- Optimizer/behavior/hosted/robot execution: `0/0/0/0`\n"
        f"- Canonical SHA-256: `{value['audit_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"issues={issues}")
    print(f"audit_sha256={value['audit_sha256']}")
    print(f"file_sha256={sha256(AUDIT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
