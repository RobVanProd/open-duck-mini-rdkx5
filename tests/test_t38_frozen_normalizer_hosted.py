from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t38_freezes_one_no_retry_hosted_continuation() -> None:
    payload = load("t38_frozen_normalizer_hosted_preregistration.json")
    assert (
        payload["status"]
        == "PREREGISTERED_T38_FROZEN_NORMALIZER_HOSTED_CONTINUATION"
    )
    assert payload["decision"] == (
        "AUTHORIZE_ONE_HASH_FROZEN_T38_L4_CONTINUATION_WITHOUT_RETRY"
    )
    assert payload["failed_checks"] == []
    training = payload["training"]
    assert training["source"] == "exact_T23_SUPPORT_HALF_checkpoint"
    assert training["support_trainthrough"]
    assert training["action_margin_trainthrough"]
    assert training["frozen_observation_normalizer"]
    assert training["frozen_observation_count"] == 16056320
    assert training["timesteps"] == 2007040
    assert training["exports"] == [0, 1003520, 2007040]
    assert not training["retry"]
    assert not training["resume"]
    assert not training["scalar_sweep"]
    assert payload["post_training"][
        "verify_normalizer_exact_at_all_exports"
    ]
    assert payload["post_training"][
        "both_postupdate_checkpoints_must_pass"
    ]
    assert not payload["post_training"]["checkpoint_cherry_pick"]
    assert payload["authority"][
        "one_hosted_gpu_continuation_after_package_contract"
    ]
    assert not payload["authority"]["additional_training_or_retry"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
