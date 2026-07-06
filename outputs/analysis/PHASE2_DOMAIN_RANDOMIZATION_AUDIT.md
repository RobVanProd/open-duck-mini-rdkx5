# Phase 2 Domain Randomization Audit

status: `HOLD_PHASE2_NOT_READY`
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

status: `HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING`

The current deployable parent is phase/context-conditioned and passes the corrected-bridge gates, but the standard PPO-loc compression path is rejected by the latest seed-tradeoff decision. A phase/context-preserving restorable PPO actor is required before Phase 2 DR can launch.

Artifacts:

- ONNX: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- ONNX exists: `True`
- ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- BC MLP NPZ: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate_mlp.npz`
- BC MLP NPZ exists: `True`
- BC MLP NPZ sha256: `1e22aa3c06a451e3ee4da32e58c6b45b881cdf87ea8ed8738c541b6dccb3e9c8`
- restore checkpoint: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- restore checkpoint exists: `False`
- warm-start fidelity status: `None`
- warm-start fidelity p95 abs error: `None`
- warm-start fidelity max abs error: `None`
- compression decision: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_ppo_loc_compression_seed5_augmentation_decision.json`
- compression decision status: `HOLD_PPO_LOC_COMPRESSION_SEED_TRADEOFF`

## Terrain / Contact

- flat XML floor friction: `0.6`
- rough XML floor friction: `1.0`

## Blockers

- `HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING`

## Warnings

- none

## Recommendation

Do not launch Stage A DR until the passing phase/context-conditioned
parent is available as a restorable PPO checkpoint. The next aligned
work is a phase/context-preserving PPO actor/export path, followed by
the same corrected-bridge x=0.08 and x=0.0 full8 gates.
