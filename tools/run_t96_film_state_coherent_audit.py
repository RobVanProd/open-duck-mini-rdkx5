#!/usr/bin/env python3
"""Audit T95 FiLM action binding with T11's state-coherent construction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t96_film_state_coherent_audit_preregistration.json"
)
OUTPUT = ANALYSIS / "t96_film_state_coherent_audit_result.json"
MARKDOWN = ANALYSIS / "T96_FILM_STATE_COHERENT_AUDIT_RESULT_20260728.md"
STAGES = {
    "context_film_scale": 64,
    "context_film_delta": 64,
    "film_hidden": 64,
    "adapter_location": 14,
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


def canonical_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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
        != "open_duck.t96_film_state_coherent_preregistration.v1"
        or value["status"]
        != "PREREGISTERED_T96_FILM_STATE_COHERENT_AUDIT"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T96 preregistration changed")
    for item in value["sources"].values():
        path = Path(item["path"])
        if path.stat().st_size != item["bytes"] or sha256(path) != item[
            "sha256"
        ]:
            raise RuntimeError(f"T96 source changed: {path}")


def add_debug_outputs(source: Path, destination: Path) -> None:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, width in STAGES.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name, TensorProto.FLOAT, [1, width]
                )
            )
    onnx.checker.check_model(model)
    onnx.save(model, destination)


def random_observation(
    rng: np.random.Generator, command_x: float
) -> np.ndarray:
    obs = rng.normal(0.0, 0.2, size=(1, 115)).astype(np.float32)
    obs[:, 6] = np.float32(command_x)
    obs[:, 13:27] = rng.uniform(
        -0.1, 0.1, size=(1, 14)
    ).astype(np.float32)
    obs[:, 101:115] = rng.uniform(
        -0.8, 0.8, size=(1, 14)
    ).astype(np.float32)
    return obs


def run_stages(
    session: ort.InferenceSession,
    obs: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> dict[str, np.ndarray]:
    values = session.run(
        list(STAGES),
        {
            "obs": obs,
            "previous_action": previous,
            "h_in": hidden,
            "calibration_context": context,
        },
    )
    return dict(zip(STAGES, values, strict=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.read_only_authorized:
        raise PermissionError("T96 requires both read-only CPU guards")
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T96: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    work = args.work_root.resolve()
    work.mkdir(parents=True)
    source = Path(prereg["sources"]["t95_final_graph"]["path"])
    debug = work / "t96_film_debug.onnx"
    add_debug_outputs(source, debug)
    session = ort.InferenceSession(
        str(debug), providers=["CPUExecutionProvider"]
    )
    initializers = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item))
        for item in onnx.load(debug).graph.initializer
    }
    max_rate = initializers["max_action_delta"]
    t94 = json.loads(
        (
            ANALYSIS / "t94_r2_calibration_manifold_result.json"
        ).read_text(encoding="utf-8")
    )
    contexts = [
        (
            cell["configuration_id"],
            cell["fit_id"],
            np.asarray(cell["context"], dtype=np.float32)[None, :],
        )
        for cell in t94["cells"]
    ]
    rng = np.random.Generator(np.random.PCG64(20260728096))
    cases_per_context = prereg["formal_contract"]["cases_per_context"]
    stage_maximum = {name: 0.0 for name in STAGES}
    effect_ticks = 0
    pair_effects: dict[str, bool] = {}
    maximum_rate_excess = 0.0
    maximum_previous_error = 0.0
    x0_exact = True
    for configuration_id, fit_id, context in contexts:
        pair_effect = False
        for case in range(cases_per_context):
            obs = random_observation(
                rng, (0.074, 0.077, 0.080)[case % 3]
            )
            hidden = rng.uniform(
                -0.5, 0.5, size=(1, 64)
            ).astype(np.float32)
            zero_context = np.zeros((1, 64), dtype=np.float32)
            probe = run_stages(
                session,
                obs,
                np.zeros((1, 14), dtype=np.float32),
                hidden,
                zero_context,
            )
            previous = np.asarray(
                probe["raw_continuous_actions"], dtype=np.float32
            )
            zero = run_stages(
                session, obs, previous, hidden, zero_context
            )
            conditioned = run_stages(
                session, obs, previous, hidden, context
            )
            for name in STAGES:
                stage_maximum[name] = max(
                    stage_maximum[name],
                    float(
                        np.max(np.abs(zero[name] - conditioned[name]))
                    ),
                )
            action_delta = float(
                np.max(
                    np.abs(
                        zero["continuous_actions"]
                        - conditioned["continuous_actions"]
                    )
                )
            )
            changed = action_delta > 1e-8
            effect_ticks += int(changed)
            pair_effect |= changed
            for output in (zero, conditioned):
                maximum_rate_excess = max(
                    maximum_rate_excess,
                    float(
                        np.max(
                            np.maximum(
                                np.abs(
                                    output["continuous_actions"]
                                    - previous
                                )
                                - max_rate,
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
            zero_obs = obs.copy()
            zero_obs[:, 6] = 0.0
            x0 = run_stages(
                session, zero_obs, previous, hidden, context
            )
            x0_exact &= np.count_nonzero(x0["continuous_actions"]) == 0
        pair_effects[f"{configuration_id}:{fit_id}"] = pair_effect
    total = len(contexts) * cases_per_context
    neg = [
        value
        for key, value in pair_effects.items()
        if key.startswith("TORSO_COM_X_NEG:")
    ]
    metrics = {
        "contexts": len(contexts),
        "cases_per_context": cases_per_context,
        "total_cases": total,
        "effect_cases": effect_ticks,
        "effect_case_fraction": effect_ticks / total,
        "context_pairs_with_effect": sum(pair_effects.values()),
        "context_pair_effect_fraction": (
            sum(pair_effects.values()) / len(pair_effects)
        ),
        "both_negative_com_pairs_effective": len(neg) == 2 and all(neg),
        "stage_maximum_abs_delta": stage_maximum,
        "maximum_rate_excess": maximum_rate_excess,
        "maximum_previous_action_error": maximum_previous_error,
        "x0_exact_zero": bool(x0_exact),
        "pair_effects": pair_effects,
    }
    contract = prereg["formal_contract"]
    checks = {
        "cpu_provider": session.get_providers()
        == ["CPUExecutionProvider"],
        "exact_40_contexts": len(contexts) == 40,
        "effect_fraction_at_least_frozen_threshold": metrics[
            "effect_case_fraction"
        ]
        >= contract["minimum_effect_tick_fraction"],
        "pair_fraction_at_least_frozen_threshold": metrics[
            "context_pair_effect_fraction"
        ]
        >= contract["minimum_context_pair_effect_fraction"],
        "maximum_action_delta_at_least_frozen_threshold": metrics[
            "stage_maximum_abs_delta"
        ]["continuous_actions"]
        >= contract["minimum_maximum_action_delta"],
        "both_negative_com_pairs_effective": metrics[
            "both_negative_com_pairs_effective"
        ],
        "rate_projection_preserved": maximum_rate_excess <= 1e-7,
        "graph_owned_previous_action": maximum_previous_error == 0.0,
        "x0_exact": metrics["x0_exact_zero"],
        "recurrent_state_invariant": metrics[
            "stage_maximum_abs_delta"
        ]["h_out"]
        == 0.0,
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    decision = (
        "INVALIDATE_T95_FALSE_NEGATIVE_AND_EARN_CORRECTED_CPU_CONTRACT_ONLY"
        if not failed
        else "CONFIRM_T95_FILM_CLOSURE"
    )
    basis = {
        "schema_version": "open_duck.t96_film_state_coherent_result.v1",
        "status": (
            "PASS_T96_FILM_STATE_COHERENT_AUDIT"
            if not failed
            else "HOLD_T96_FILM_STATE_COHERENT_AUDIT"
        ),
        "decision": decision,
        "failed_checks": failed,
        "checks": checks,
        "metrics": metrics,
        "debug_graph": receipt(debug),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "execution": {
            "optimizer_steps": 0,
            "simulator_ticks": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "corrected_cpu_contract_preregistration": not failed,
            "hosted_training": False,
            "behavior": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T96 FiLM state-coherent audit result",
                "",
                f"Status: `{value['status']}`",
                f"Decision: `{decision}`",
                "",
                f"- Effective cases: **{effect_ticks}/{total}**",
                f"- Effective contexts: "
                f"**{sum(pair_effects.values())}/40**",
                f"- Maximum final-action delta: "
                f"**{stage_maximum['continuous_actions']:.9g}**",
                f"- Both negative-COM contexts effective: "
                f"**{metrics['both_negative_com_pairs_effective']}**",
                "",
                "No optimizer, simulator, hosted compute, or hardware ran.",
                "",
                f"Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={decision}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

