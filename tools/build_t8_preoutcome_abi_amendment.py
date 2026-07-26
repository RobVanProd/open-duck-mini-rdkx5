#!/usr/bin/env python3
"""Freeze the pre-outcome T8 recurrent-ABI ordering correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
OUTPUT = ANALYSIS / "t8_state_coherent_handoff_abi_amendment.json"
MARKDOWN = (
    ANALYSIS / "T8_STATE_COHERENT_HANDOFF_ABI_AMENDMENT_20260726.md"
)
FAILED_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t8_state_coherent_handoff_v1"
    r"\V121_TRAIN_MATCHED_HALF\p30"
)


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


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def graph_abi(path: Path) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "inputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_inputs()
        ],
        "outputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_outputs()
        ],
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T8 ABI amendment")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    evaluation_path = FAILED_ROOT / "evaluation.json"
    log_path = FAILED_ROOT / "stdout.log"
    trace_dir = FAILED_ROOT / "traces"
    if not evaluation_path.is_file() or not log_path.is_file():
        raise RuntimeError("T8 failed pre-outcome evidence is missing")
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    runs = evaluation.get("runs") or []
    trace_files = list(trace_dir.glob("*.jsonl"))
    if (
        len(runs) != 4
        or any(run.get("status") != "HOLD_POLICY_IO_CONTRACT" for run in runs)
        or any(run.get("modes") is not None for run in runs)
        or any(run.get("dynamics_override") is not None for run in runs)
        or trace_files
        or (ANALYSIS / "t8_state_coherent_handoff_result.json").exists()
    ):
        raise RuntimeError("T8 failure crossed the pre-outcome boundary")

    graphs = [
        graph_abi(Path(item["wrapped"]["path"]))
        for item in prereg["candidate"]["checkpoints"]
    ]
    expected_input_names = {
        "obs",
        "previous_action",
        "h_in",
        "calibration_context",
    }
    expected_output_names = {
        "continuous_actions",
        "previous_action_out",
        "h_out",
    }
    for graph in graphs:
        if (
            {item["name"] for item in graph["inputs"]}
            != expected_input_names
            or {item["name"] for item in graph["outputs"]}
            != expected_output_names
        ):
            raise RuntimeError("T8 wrapped ONNX ABI changed")

    corrected_files = {
        "runner": receipt(
            ROOT / "tools" / "run_t8_state_coherent_handoff.py"
        ),
        "worker": receipt(
            ROOT / "tools" / "evaluate_t8_state_coherent_handoff.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t8_state_coherent_handoff.py"
        ),
    }
    basis = {
        "original_preregistration": {
            "path": str(PREREG.resolve()),
            "file_sha256": sha256(PREREG),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "repository_inputs": {
                label: prereg["repository_inputs"][label]
                for label in corrected_files
            },
            "published_commit": "c2c1b587",
        },
        "preoutcome_evidence": {
            "failed_evaluation": receipt(evaluation_path),
            "failed_stdout": receipt(log_path),
            "failure": (
                "the frozen response-conditioned ABI requires state tuple "
                "order h_in,previous_action paired with "
                "h_out,previous_action_out; the worker declared the reverse "
                "order and was rejected before simulator modes were run"
            ),
            "attempted_commands": [run["command_x"] for run in runs],
            "policy_io_holds": len(runs),
            "simulator_modes_returned": 0,
            "dynamics_readbacks_returned": 0,
            "jsonl_trace_files": 0,
            "completed_block_manifests": 0,
            "behavior_cells_with_decision_weight": 0,
            "result_exists": False,
        },
        "onnx_abi": {
            "graphs": graphs,
            "input_name_set": sorted(expected_input_names),
            "output_name_set": sorted(expected_output_names),
            "policy_state_pairing": [
                ["h_in", "h_out"],
                ["previous_action", "previous_action_out"],
            ],
        },
        "authorized_change": {
            "old_state_inputs": ["previous_action", "h_in"],
            "old_state_outputs": ["previous_action_out", "h_out"],
            "new_state_inputs": ["h_in", "previous_action"],
            "new_state_outputs": ["h_out", "previous_action_out"],
            "reason": (
                "match the already-frozen response-conditioned evaluator ABI "
                "and preserve correct input/output state pairing"
            ),
        },
        "corrected_files": corrected_files,
        "unchanged_contract": {
            "candidate_and_checkpoints": True,
            "policies_and_hashes": True,
            "asset_parity": True,
            "calibrator_and_support_action": True,
            "fits_commands_seed_and_duration": True,
            "handoff_semantics": True,
            "behavior_and_protection_gates": True,
            "decision_rule": True,
            "authority": True,
            "training_steps": 0,
        },
        "authority": {
            "resume_exact_t8_cpu_screen": True,
            "training_or_hosted_compute": False,
            "robot_rdkx5_gate5_torque_motion": False,
        },
    }
    payload = {
        "schema_version": "open_duck.t8_preoutcome_abi_amendment.v1",
        "status": "PREREGISTERED_T8_PREOUTCOME_ABI_ORDER_CORRECTION",
        **basis,
        "amendment_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T8 recurrent-ABI pre-outcome amendment",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['amendment_contract_sha256']}`",
        "- Evidence boundary: `0` simulator modes, `0` JSONL traces, "
        "`0` completed blocks, `0` behavior cells, and no result artifact.",
        "- Failure: the worker declared the recurrent state tuple in the reverse "
        "order from the already-frozen response-conditioned evaluator ABI.",
        "- Correction: inputs `h_in,previous_action`; outputs "
        "`h_out,previous_action_out`.",
        "- Both wrapped V121 graphs retain the exact frozen input/output name "
        "sets, shapes, hashes, and 1,024-tick bit-exact source parity.",
        "- Candidate, policies, support prefix, physical handoff semantics, "
        "matrix, gates, decision rule, and authority are unchanged.",
        "",
        "This amendment permits only resumption of the exact T8 CPU screen. "
        "It does not authorize training, hosted compute, robot/RDK-X5 access, "
        "Gate 5, torque, motion, deployment, or grounded replay.",
    ]
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"contract_sha256={payload['amendment_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
