# Phase 2 Domain Randomization Audit

status: `PASS_PHASE2_READY_TO_DRY_RUN`
playground_path: `../Open_Duck_Playground`

This is an offline static audit. It did not train, SSH, deploy, or move the robot.

## Existing Hooks

| hook | status | evidence |
|---|---|---|
| `friction_randomization` | `PRESENT` | playground/common/randomize.py mutates model.geom_friction |
| `mass_randomization` | `PRESENT` | playground/common/randomize.py mutates model.body_mass |
| `com_randomization` | `PRESENT` | playground/common/randomize.py jitters torso body_ipos |
| `actuator_gain_randomization` | `PRESENT` | playground/common/randomize.py scales actuator gains/bias |
| `frictionloss_armature_randomization` | `PRESENT` | playground/common/randomize.py scales dof frictionloss and armature |
| `observation_noise` | `PRESENT` | joystick.py default_config and _get_obs add joint/IMU noise |
| `action_delay` | `PRESENT` | joystick.py samples delayed action from action_history |
| `imu_delay` | `PRESENT` | joystick.py samples delayed IMU/gravity history |
| `push_perturbations` | `PRESENT` | joystick.py adds random planar velocity impulse to floating base qvel |
| `rough_terrain` | `PRESENT` | constants.py maps rough_terrain_backlash and XML contains hfield |
| `actuator_bridge` | `PRESENT` | joystick.py bridge model and runner.py bridge CLI flags |
| `domain_randomize_training_hook` | `PRESENT` | BaseRunner passes configured randomization_fn into Brax PPO train |
| `leg_geometry_randomization` | `PRESENT` | playground/common/randomize.py supports default-off leg body_pos scale jitter and runner.py exposes --dr_leg_geometry_jitter_scale |
| `dr_range_cli` | `PRESENT` | runner.py exposes staged DR range CLI for friction, mass, COM, push, noise, actuator gain, qpos jitter, and leg geometry |

## Warm-Start Gate

status: `PASS_TRAINABLE_CHECKPOINT_PRESENT`

A verified phase/context-preserving PPO step-0 Orbax checkpoint exists. The older PPO-loc compression hold is retained as historical evidence but no longer blocks the Phase 2 dry-run gate.

Artifacts:

- ONNX: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- ONNX exists: `True`
- ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- BC MLP NPZ: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate_mlp.npz`
- BC MLP NPZ exists: `True`
- BC MLP NPZ sha256: `1e22aa3c06a451e3ee4da32e58c6b45b881cdf87ea8ed8738c541b6dccb3e9c8`
- restore checkpoint: `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- restore checkpoint exists: `True`
- warm-start fidelity status: `PASS_PHASE_MODULATED_PPO_WARMSTART_STEP0_EXPORT_FIDELITY`
- warm-start fidelity p95 abs error: `0.0`
- warm-start fidelity max abs error: `0.0`
- compression decision: `outputs/analysis/phase2_ppo_loc_compression_seed5_augmentation_decision.json`
- compression decision status: `HOLD_PPO_LOC_COMPRESSION_SEED_TRADEOFF`

## Terrain / Contact

- flat XML floor friction: `0.6`
- rough XML floor friction: `1.0`

## Blockers

- none

## Warnings

- none

## Recommendation

The Phase 2 warm-start dry-run prerequisites are satisfied.
The next aligned work is Stage A domain-randomized PPO from
the verified phase/context-preserving checkpoint, with narrow
randomization first and corrected-bridge gates after the stage.
