from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "colab_t23_support_trainthrough_continuation.py"
T22_RESULT = (
    ROOT / "outputs" / "analysis" / "t22_corrected_one_update_cpu_result.json"
)


def test_t22_is_the_only_hosted_preregistration_authority() -> None:
    value = json.loads(T22_RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
    assert value["decision"] == "EARN_T22_HOSTED_CONTINUATION_PREREGISTRATION"
    assert value["failed_checks"] == []
    assert value["execution"]["hosted_or_colab_compute"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0


def test_driver_freezes_one_persistent_two_checkpoint_continuation() -> None:
    text = DRIVER.read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert '"2007040"' in text
    assert '"--winner_t19_support_trainthrough"' in text
    assert '"--winner_v119_train_transition_match"' in text
    assert '"--ppo_num_envs"' in text and '"256"' in text
    assert '"--ppo_episode_length"' in text and '"600"' in text


def test_driver_uses_source_rate_vector_and_no_runtime_surface() -> None:
    text = DRIVER.read_text(encoding="utf-8")
    for value in (
        "1.4736209064722061",
        "1.4300791546702385",
        "1.3976470567286015",
        "1.2215287424623966",
    ):
        assert value in text
    assert '"rdkx5_or_robot": False' in text
    assert '"gate5_authorized": False' in text


def test_driver_has_no_retry_or_resume_path() -> None:
    text = DRIVER.read_text(encoding="utf-8")
    assert "resume" not in text.lower()
    assert "retry" in text.lower()
    assert "no-retry path exists" in text
    assert "cpu_topology_validation_required" in text
