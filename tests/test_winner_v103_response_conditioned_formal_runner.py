from __future__ import annotations

import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    json_finite,
    load_hosted_artifact,
    response_trace_audit,
    safe_extract,
    zero_cell_plan_contract,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_zero_cell_formal_plan_is_the_frozen_1024_cell_matrix() -> None:
    contract = zero_cell_plan_contract()
    assert contract["pass"] is True
    assert contract["failed_checks"] == []
    assert contract["formal_behavior_cells_executed"] == 0
    assert contract["matrix_cells"] == 1024
    assert contract["condition_count"] == 64
    assert contract["matrix_plan_sha256"] == (
        "10b5d3e407636d276275f3f39145233c3cd63688c3229235411ed2734651e073"
    )
    assert contract["response_cell_template"] == {
        "observation_dim": 115,
        "action_dim": 14,
        "policy_inputs": [
            "obs",
            "previous_action",
            "h_in",
            "calibration_context",
        ],
        "policy_outputs": [
            "continuous_actions",
            "previous_action_out",
            "h_out",
        ],
        "graph_authoritative_output": True,
        "calibration_ticks": 250,
        "home_return_ticks": 250,
        "calibrator_sha256": (
            "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
        ),
        "scored_ticks": 600,
    }
    assert contract["selection_rule"] == {
        "both_checkpoints_must_pass_all_512": True,
        "selected_step_if_both_pass": 2_007_040,
        "no_closest_or_reward_selection": True,
    }


def test_safe_extract_rejects_parent_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "malicious.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        member = tarfile.TarInfo("../escape.txt")
        payload = b"escape"
        member.size = len(payload)
        stream.addfile(member, io.BytesIO(payload))
    with pytest.raises(ValueError, match="unsafe V102 archive member"):
        safe_extract(archive, tmp_path / "extract")
    assert not (tmp_path / "escape.txt").exists()


def test_hosted_artifact_receipts_bind_both_eligible_graphs(
    tmp_path: Path,
) -> None:
    source = (
        tmp_path
        / "source"
        / "winner_v102_response_conditioned_curriculum"
        / "stage3_domain_100_percent"
    )
    source.mkdir(parents=True)
    paths = {
        1_003_520: source / "policy_1003520.onnx",
        2_007_040: source / "policy_2007040.onnx",
    }
    for step, path in paths.items():
        path.write_bytes(f"graph-{step}".encode())
    archive = tmp_path / "artifact.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(
            source.parents[0],
            arcname="winner_v102_response_conditioned_curriculum",
        )
    graph_rows = [
        {
            "step": step,
            "sha256": digest(path),
            "abi_exact": True,
            "initializers_finite": True,
            "x0_action_exact_zero": True,
            "x0_previous_action_out_exact_zero": True,
            "x0_hidden_finite": True,
        }
        for step, path in sorted(paths.items())
    ]
    payload = {
        "status": "PASS_WINNER_V102_RESPONSE_CONDITIONED_TRAINING_ARTIFACT",
        "failed_checks": [],
        "checks": {"formal_behavior_cells_zero": True},
        "stages": [
            {"id": "DOMAIN_25_PERCENT"},
            {"id": "DOMAIN_50_PERCENT"},
            {
                "id": "DOMAIN_100_PERCENT",
                "checkpoint_steps": [0, 1_003_520, 2_007_040],
                "onnx_steps": [0, 1_003_520, 2_007_040],
                "onnx": graph_rows,
            },
        ],
        "artifact": {
            "sha256": digest(archive),
            "bytes": archive.stat().st_size,
        },
    }
    artifact_json = tmp_path / "artifact.json"
    artifact_json.write_text(json.dumps(payload), encoding="utf-8")
    observed = load_hosted_artifact(
        artifact_json=artifact_json,
        artifact_archive=archive,
        extract_root=tmp_path / "extract",
    )
    assert observed["policy_hashes"] == {
        step: digest(path) for step, path in paths.items()
    }
    assert set(observed["policy_paths"]) == set(paths)
    assert all(path.exists() for path in observed["policy_paths"].values())


def test_response_trace_audit_requires_immutable_context_and_zero_host_delta(
    tmp_path: Path,
) -> None:
    trace = tmp_path / "trace.jsonl"
    context_sha256 = "a" * 64
    rows = [
        {
            "mode": "fitted",
            "policy_graph_authoritative_output": True,
            "policy_host_action_delta_max_abs": 0.0,
            "policy_calibration_context_sha256": context_sha256,
        }
        for _ in range(2)
    ]
    trace.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    result = {
        "policy_io": {
            "obs_input_name": "obs",
            "action_output_name": "continuous_actions",
            "state_input_names": ["h_in", "previous_action"],
            "state_output_names": ["h_out", "previous_action_out"],
            "context_input_name": "calibration_context",
            "context_input_shape": [1, 64],
        },
        "modes": {
            "fitted": {
                "response_calibration": {
                    "enabled": True,
                    "calibration_ticks": 250,
                    "home_return_ticks": 250,
                    "calibrator_sha256": (
                        "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
                    ),
                    "context_shape": [1, 64],
                    "context_finite": True,
                    "context_sha256": context_sha256,
                    "locomotion_phase_reset": [1.0, 0.0],
                    "locomotion_hidden_exact_zero": True,
                    "locomotion_previous_action_exact_zero": True,
                }
            }
        },
    }
    audit = response_trace_audit(trace, result)
    assert audit["pass"] is True
    assert audit["failed_checks"] == []
    assert audit["trace_rows"] == 2


def test_json_finite_converts_nonstandard_floats() -> None:
    value = json_finite(
        {
            "positive": float("inf"),
            "negative": float("-inf"),
            "nan": float("nan"),
        }
    )
    assert value == {
        "positive": 1.0e308,
        "negative": -1.0e308,
        "nan": None,
    }
    json.dumps(value, allow_nan=False)
