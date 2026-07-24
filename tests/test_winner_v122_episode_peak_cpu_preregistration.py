import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v122_prereg_selects_exact_gate_objective_without_training() -> None:
    value = load("winner_v122_episode_peak_cpu_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["source"]["step"] == 1_003_520
    assert value["objective"]["name"] == (
        "episode_global_peak_torque_increment_integral"
    )
    assert value["objective"]["default_enabled"] is False
    assert value["objective"]["existing_linear_peak_scale"] == 0.0
    assert value["objective"]["scale_search"] is False
    assert value["hosted_if_cpu_passes"]["retry"] is False
    assert value["hosted_if_cpu_passes"][
        "both_postupdate_checkpoints_required"
    ] is True
    assert value["execution"]["training_steps"] == 0
    assert value["execution"]["colab_compute_units"] == 0
    assert value["authority"]["cpu_smoke_authorized"] is True
    assert value["authority"]["hosted_training_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_v122_runner_freezes_the_prereg_and_is_cpu_only() -> None:
    source = (
        ROOT / "tools/run_winner_v122_episode_peak_cpu_smoke.py"
    ).read_text(encoding="utf-8")
    assert (
        "3617e52dc26a3a6db317473162077ece264af8aef8e3afc276a1925d33cabc89"
        in source
    )
    assert 'os.environ["JAX_PLATFORMS"] = "cpu"' in source
    assert '"--num_timesteps",\n        "1024"' in source
    assert '"--ground_up_linear_peak_torque_exceedance_scale",\n        "0"' in source
    assert (
        '"--ground_up_episode_peak_torque_increment_scale"' in source
    )
    assert '"--winner_v119_train_transition_match"' in source


def test_v122_cpu_result_passes_before_any_hosted_authority() -> None:
    value = load("winner_v122_episode_peak_cpu_result.json")
    assert value["status"] == (
        "PASS_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["analytic_objective"]["max_abs_error_nm"] < 1.0e-7
    assert len(value["training"]["policy_leaf_deltas"]) == 15
    assert value["training"]["checkpoint_steps"] == [0, 1024]
    assert value["training"]["onnx_steps"] == [0, 1024]
    assert len(value["deployed_onnx"]) == 2
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["colab_compute_units"] == 0
    assert value["authority"]["hosted_preregistration_authorized"] is True
    assert value["authority"]["hosted_training_authorized"] is False


def test_v122_reward_mass_attribution_earns_only_preregistration() -> None:
    value = load("winner_v122_cpu_reward_mass_attribution.json")
    assert value["status"] == (
        "PASS_WINNER_V122_CPU_REWARD_MASS_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["interpretation"]["scalar_search"] is False
    assert value["interpretation"]["post_hoc_scale_change"] is False
    assert value["decision"] == (
        "PREREGISTER_ONE_V122_HOSTED_CONTINUATION"
    )
    assert value["execution"]["colab_compute_units"] == 0
    assert value["authority"]["hosted_preregistration_authorized"] is True
    assert value["authority"]["hosted_training_authorized"] is False
