from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v25_directional_support_control_diagnostic.py"
DOMAIN = ROOT / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v25_directional_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_population_and_counts_are_frozen() -> None:
    module = load()
    assert module.CANDIDATES == (("half", 150), ("final", 200))
    assert module.SOURCE_UPDATE == 100
    assert len(module.CONFIGURATION_IDS) == 10
    assert module.BASE_PREFIX_TICKS == 20
    assert module.FORK_HORIZON_TICKS == 5
    assert module.EXPECTED_BASE_TRAJECTORIES == 20
    assert module.EXPECTED_FORK_POINTS == 800
    assert module.EXPECTED_SHORT_HORIZON_ROLLOUTS == 1600
    assert module.DESTABILIZING_FRACTION_THRESHOLD == 0.75


def test_all_selected_configurations_are_negative_x() -> None:
    module = load()
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    lookup = module.exact_configurations(domain)
    assert all(
        float(lookup[name]["torso_com_offset_m"][0]) < 0.0
        for name in module.CONFIGURATION_IDS
    )


def test_array_hash_binds_dtype_shape_and_bytes() -> None:
    module = load()
    value = np.arange(6, dtype=np.float32).reshape(2, 3)
    assert module.array_sha256(value) == module.array_sha256(value.copy())
    assert module.array_sha256(value) != module.array_sha256(value.astype(np.float64))
    assert module.array_sha256(value) != module.array_sha256(value.reshape(3, 2))


def test_mujoco_integration_snapshot_repeats_exactly() -> None:
    import mujoco

    module = load()
    model = mujoco.MjModel.from_xml_string(
        """
        <mujoco>
          <option timestep="0.002"/>
          <worldbody>
            <body>
              <joint name="hinge" type="hinge"/>
              <geom type="capsule" size="0.02 0.1"/>
            </body>
          </worldbody>
          <actuator><motor joint="hinge"/></actuator>
        </mujoco>
        """
    )
    data = mujoco.MjData(model)
    data.qpos[0] = 0.2
    data.qvel[0] = -0.1
    data.ctrl[0] = 0.3
    mujoco.mj_forward(model, data)
    episode = SimpleNamespace(
        model=model,
        data=data,
        bridge=SimpleNamespace(value=np.array([0.1], dtype=np.float64)),
        observer=SimpleNamespace(value=np.array([0.2], dtype=np.float64)),
        history=[np.array([index], dtype=np.float64) for index in range(4)],
        overcurrent_streak=np.array([0], dtype=np.int64),
        gyro_xy_norms=[0.0],
        valid_ticks=3,
        maximum_abs_tilt=0.1,
        minimum_base_z=0.2,
        maximum_torque_nm=0.3,
        maximum_current_a=0.4,
        maximum_observer_physical_separation_rad=0.5,
    )
    snapshot = module.capture_episode(mujoco, episode)

    def branch() -> np.ndarray:
        module.restore_episode(mujoco, episode, snapshot)
        episode.data.ctrl[0] = 0.4
        for _ in range(5):
            mujoco.mj_step(model, episode.data)
        specification = mujoco.mjtState.mjSTATE_INTEGRATION
        state = np.empty(mujoco.mj_stateSize(model, specification), dtype=np.float64)
        mujoco.mj_getState(model, episode.data, state, specification)
        return state

    assert np.array_equal(branch(), branch())


def test_runner_is_zero_update_cpu_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_steps": 0' in source
    assert "training.adam_step(" not in source
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
    assert "mjSTATE_INTEGRATION" in source
    assert "same_input_observation_sha256" in source
    assert "abs_pitch_delta_rad" in source
