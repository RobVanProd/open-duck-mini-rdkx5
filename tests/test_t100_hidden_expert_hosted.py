from __future__ import annotations

import json
from pathlib import Path

from tools import build_t100_hidden_expert_hosted_preregistration as t100


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t100_driver_command_contract() -> None:
    from tools import colab_t100_hidden_expert_continuation as driver

    command = driver.runner_command(
        Path("/bundle/playground"),
        Path("/work"),
        Path("/bundle/assets/source_checkpoint"),
        Path("/bundle/assets/reference.npz"),
    )
    assert "--winner_t98_hidden_expert_continuation" in command
    assert "--winner_t77_endpoint_joint_adapter_continuation" not in command
    gate = command.index("--winner_t98_hidden_gate_asset_path")
    assert command[gate + 1].endswith(driver.GATE_NAME)
    assert command[command.index("--ppo_num_envs") + 1] == "256"
    assert command[command.index("--num_timesteps") + 1] == "2007040"


def test_t100_preregistration_when_present() -> None:
    path = ANALYSIS / "t100_hidden_expert_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == t100.canonical_sha256(
        basis
    )
    assert value["status"] == (
        "PREREGISTERED_T100_HIDDEN_EXPERT_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["actor_trainable_groups"] == [
        "negative_adapter_location"
    ]
    assert value["training"]["retry"] is False
    assert value["training"]["resume"] is False
