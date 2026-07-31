from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
ATTRIBUTION = (
    ROOT / "outputs" / "analysis" / "t20_two_rate_mismatch_attribution.json"
)
COMPOSED = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "t21_two_rate_test_module",
        MODULE,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_and_external_rate_vectors_are_exact_and_distinct() -> None:
    module = load_module()
    source = np.asarray(
        [
            1.0,
            0.75,
            1.4736209064722061,
            1.4300791546702385,
            1.3976470567286015,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.75,
            1.25,
            1.0,
            1.2215287424623966,
        ],
        dtype=np.float32,
    )
    external = np.asarray(
        [
            1.0,
            0.75,
            1.5,
            1.5,
            1.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.75,
            1.25,
            1.0,
            1.25,
        ],
        dtype=np.float32,
    )
    assert np.array_equal(module.SOURCE_RATE_LIMITS_RAD_S, source)
    assert np.array_equal(module.RATE_LIMITS_RAD_S, external)
    assert np.array_equal(
        np.flatnonzero(source != external),
        np.asarray([2, 3, 4, 13]),
    )
    assert np.all(source <= external)
    assert np.array_equal(
        module.SOURCE_MAX_ACTION_DELTA,
        source * np.float32(0.02) / np.float32(0.25),
    )
    assert np.array_equal(
        module.MAX_ACTION_DELTA,
        external * np.float32(0.02) / np.float32(0.25),
    )


def test_patch_routes_source_and_external_limits_separately() -> None:
    text = PATCH.read_text(encoding="utf-8")
    assert "SOURCE_RATE_LIMITS_RAD_S" in text
    assert "expected_limits = jp.asarray(" in text
    assert "external_velocity_limits = jp.asarray(" in text
    assert "t19.RATE_LIMITS_RAD_S, dtype=jp.float32" in text
    assert (
        "state.info[\"motor_targets\"]\n"
        "+                - external_velocity_limits * self.dt"
    ) in text
    assert "T19 trained source rate vector changed" in text


def test_prefix_diagnostic_exposes_both_target_histories() -> None:
    text = MODULE.read_text(encoding="utf-8")
    assert "def prefix_diagnostic(" in text
    assert '"motor_targets": motor_targets' in text
    assert '"source_motor_targets": source_motor_targets' in text
    assert "length=CALIBRATION_TICKS" in text


def test_prefix_initializes_source_coordinates_from_external_home() -> None:
    text = MODULE.read_text(encoding="utf-8")
    assert "def _prepare_prefix_initial(" in text
    assert "source_action = inverse_action(" in text
    assert 'info["t19_source_motor_targets"] = (' in text
    assert "initial = self._prepare_prefix_initial(initial)" in text
    assert text.count("initial = self._prepare_prefix_initial(initial)") == 2


def test_composed_v6_manifest_and_changed_file_scope() -> None:
    manifest_path = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "open_duck.t19_composed_source.v1"
    composed_module = (
        COMPOSED / "playground" / "common" / "t19_support_trainthrough.py"
    )
    assert composed_module.read_bytes() == MODULE.read_bytes()


def test_t20_attribution_preregisters_only_two_rate_cpu_correction() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T20_TWO_RATE_MISMATCH_ATTRIBUTION"
    assert value["decision"] == "PREREGISTER_T21_TWO_RATE_SEPARATION"
    assert value["failed_checks"] == []
    assert value["attribution"]["new_optimizer_steps_authorized"] == 0
    assert value["attribution"]["hosted_compute_units"] == 0
    assert value["attribution"]["robot_or_rdk_access"] == 0
