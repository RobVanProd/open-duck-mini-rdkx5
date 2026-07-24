import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT / "outputs/analysis/winner_v115_nominal_behavior_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v115_nominal_behavior.py"


def test_v115_nominal_matrix_is_exact_and_persistent() -> None:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V115_NOMINAL_BEHAVIOR"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["sha256"] == (
        "91645f353af9b4c962641f52ab15b3826155dc5fc24736841d88204c451592e8"
    )
    assert {row["step"] for row in value["matrix"]["rows"]} == {
        1_003_520,
        2_007_040,
    }
    assert {
        row["command_x_m_s"] for row in value["matrix"]["rows"]
    } == {0.0, 0.074, 0.077, 0.080}
    assert all(row["duration_ticks"] == 600 for row in value["matrix"]["rows"])
    assert value["authority"]["formal_behavior_cells_authorized"] == 16
    assert value["authority"]["full_matrix_authorized"] is False


def test_v115_runner_freezes_preregistration_and_matrix_hashes() -> None:
    spec = importlib.util.spec_from_file_location("winner_v115_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.PREREG_SHA256 == (
        "b185c5bda376a6bedd6b8bba272ea26cd48b1bdbddf4aaad56e52afae2d68a37"
    )
    assert module.MATRIX_SHA256 == (
        "91645f353af9b4c962641f52ab15b3826155dc5fc24736841d88204c451592e8"
    )
