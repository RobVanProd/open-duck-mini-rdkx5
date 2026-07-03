# Phase 2 Domain Randomization Audit

status: `PASS_PHASE2_READY_TO_DRY_RUN`
playground_path: `/home/lsd/robots/Open_Duck_Playground`

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

A verified PPO step-0 Orbax checkpoint exists for the promoted rate165 candidate. The fidelity report proves the exported checkpoint policy matches the PPO-loc warm-start ONNX at action level before PPO updates.

Artifacts:

- ONNX: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx`
- ONNX exists: `True`
- ONNX sha256: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
- BC MLP NPZ: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate_mlp.npz`
- BC MLP NPZ exists: `True`
- BC MLP NPZ sha256: `08aa820651b20ab43d65dde63382e7e8b7998ae213d4f1bd67eeaa7385d52205`
- restore checkpoint: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint`
- restore checkpoint exists: `True`
- warm-start fidelity status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- warm-start fidelity p95 abs error: `1.1920928955078125e-07`
- warm-start fidelity max abs error: `2.682209014892578e-07`

## Terrain / Contact

- flat XML floor friction: `0.6`
- rough XML floor friction: `1.0`

## Blockers

- none

## Warnings

- none

## Recommendation

Use the verified step-0 PPO checkpoint as the Phase 2 trainable
warm-start. Before the full curriculum, add or configure staged DR
range controls and leg-geometry jitter, then run Stage A and gate it
against the corrected bridge before advancing.
