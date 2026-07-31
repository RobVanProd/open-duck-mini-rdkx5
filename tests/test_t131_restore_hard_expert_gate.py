from __future__ import annotations

from pathlib import Path
import sys

import onnx


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from t131_restore_hard_expert_gate import restore_hard_gate  # noqa: E402


ALWAYS_ON = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/"
    "t100c_half_expected_always_on.onnx"
)
HARD_REFERENCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_023820_1003520.onnx"
)


def test_restore_hard_gate_is_exact_inverse(tmp_path: Path) -> None:
    if not ALWAYS_ON.exists() or not HARD_REFERENCE.exists():
        return
    value = restore_hard_gate(
        ALWAYS_ON,
        tmp_path / "restored" / "hard.onnx",
        reference=HARD_REFERENCE,
    )
    assert value["node_count_exact"]
    assert value["abi_exact"]
    assert value["initializers_exact"]
    assert value["replacement_exact"]
    assert value["negative_gate_consumer_count"] == 1
    assert value["reference"]["byte_exact"]
    onnx.checker.check_model(onnx.load(value["output"]["path"]))
