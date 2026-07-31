import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT / "outputs/analysis/winner_v114_linear_torque_cpu_preregistration.json"
)


def test_v114_cpu_preregistration_is_narrow_and_compute_free() -> None:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    objective = value["objective"]
    assert objective["default_off_scale"] == 0.0
    assert objective["squared_peak_torque_scale"] == 0.0
    assert objective["training_scale"] == -307.48131091308585
    assert value["cpu_smoke"]["timesteps"] == 1024
    assert value["cpu_smoke"]["required_exports"] == [0, 1024]
    hosted = value["hosted_if_cpu_passes"]
    assert hosted["one_continuation_only"] is True
    assert hosted["retry"] is False
    assert hosted["resume"] is False
    authority = value["authority"]
    assert authority["cpu_smoke_authorized"] is True
    assert authority["hosted_training_authorized"] is False
    assert authority["gate5_authorized"] is False
    assert authority["rdkx5_or_robot"] is False
