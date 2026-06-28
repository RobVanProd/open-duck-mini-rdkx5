# Phase 2 Domain Randomization Audit

status: `HOLD_PHASE2_NOT_READY`
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
| `domain_randomize_training_hook` | `PRESENT` | BaseRunner passes randomization_fn into Brax PPO train |
| `leg_geometry_randomization` | `MISSING` | No body geom/site length scale jitter hook found in static audit |
| `dr_range_cli` | `PARTIAL` | runner.py exposes actuator bridge ranges but not friction/mass/COM/push/noise/terrain-ramp ranges as CLI arguments |

## Warm-Start Gate

status: `HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING`

Current Playground PPO warm-start path uses --restore_checkpoint_path for an Orbax checkpoint. The Phase 1 deployable artifact is ONNX plus BC MLP NPZ, which is useful as a behavior prior or conversion source but is not directly a PPO trainable checkpoint.

Artifacts:

- ONNX: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- ONNX exists: `True`
- ONNX sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- BC MLP NPZ: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- BC MLP NPZ exists: `True`
- BC MLP NPZ sha256: `312f1ef0ba758af5fdeae900ce0a34dab659fe348a9f389988ddaaaa15659497`

## Terrain / Contact

- flat XML floor friction: `0.6`
- rough XML floor friction: `1.0`

## Blockers

- `HOLD_TRAINABLE_WARMSTART_CHECKPOINT_MISSING`
- `HOLD_LEG_GEOMETRY_JITTER_NOT_IMPLEMENTED`
- `WARN_DR_RANGES_NOT_CLI_CONFIGURABLE`

## Recommendation

Do not launch Phase 2 PPO as a scratch run. First create or recover a
trainable checkpoint equivalent to the Phase 1 candidate, or implement
a verified conversion/BC-rehydration path. Then add/configure DR range
controls and run the staged curriculum.
