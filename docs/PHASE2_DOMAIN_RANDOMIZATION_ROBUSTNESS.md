# Phase 2 Domain-Randomized Robustness Training

status: `PREPARED_BLOCKED_ON_TRAINABLE_WARMSTART`

## Objective

Harden the corrected-bridge Phase 1 candidate with curriculum domain
randomization while preserving:

- corrected actuator envelope compliance,
- command conditioning,
- `x=0.0` stillness,
- and the slow in-envelope `x=0.08` gait.

Robot validation is out of scope. No SSH, no deploy, no grounded replay.

## Phase 1 Anchor

```text
policy: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
corrected bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
corrected bridge sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
```

The carpet test showed the current policy is actuator-trackable on the ground
but does not lift/clear its feet enough to walk forward on medium carpet. Phase
2 should therefore treat robustness and terrain/contact margin as the target,
not actuator tracking alone.

## Blocking Warm-Start Issue

The user constraint is correct: Phase 2 must warm-start from the Phase 1 gait,
not train from scratch.

The current local Playground PPO runner warm-starts from a Brax/Orbax
checkpoint via `--restore_checkpoint_path`. The Phase 1 candidate is preserved
as ONNX plus a BC MLP NPZ. That is deployable and useful as a behavior prior,
but it is not directly a trainable PPO checkpoint.

Therefore Phase 2 training is blocked until one of these is true:

1. Recover the Orbax checkpoint that exported the Phase 1 candidate.
2. Implement and verify ONNX/NPZ-to-PPO-params conversion.
3. Add a BC-rehydration path that initializes the PPO policy network from the
   Phase 1 BC MLP weights and proves ONNX fidelity before PPO updates.

Do not launch a scratch PPO run and call it Phase 2.

## Existing Playground Hooks

The local Playground already provides most of the requested DR scaffolding:

- friction randomization in `playground/common/randomize.py`
- link mass and torso mass randomization
- torso COM jitter
- frictionloss and armature randomization
- actuator gain/bias scaling
- observation noise for joint position, joint velocity, gyro, accelerometer,
  and gravity
- action delay and IMU delay
- random planar push impulses to the floating base
- rough-terrain hfield scene via `rough_terrain_backlash`
- corrected actuator bridge hooks and runner CLI flags

Missing or partial:

- leg-length / geometry jitter is not implemented
- friction/mass/COM/push/noise ranges are mostly hardcoded, not CLI-staged
- stage advancement is not automated by corrected-bridge gates
- trainable warm-start checkpoint is missing

## Curriculum

Stage A:

- flat terrain
- narrow physics randomization
- no push
- corrected bridge near fitted range
- behavior prior strong enough to preserve gait

Stage B:

- flat terrain
- full physics randomization
- gentle pushes
- same corrected envelope gate

Stage C:

- existing rough hfield terrain
- full physics randomization
- gentle pushes

Stage D:

- rough hfield terrain
- stronger pushes
- still reject any policy exceeding corrected per-joint envelope

## Gate

Every stage must pass before advancing:

```text
x=0.08:
  seeds: 8/8
  falls: 0
  corrected velocity excess: 0.0
  max pitch-chain tracking p95 <= 0.20 rad
  track ratio >= 0.40

x=0.0:
  seeds: 8/8
  falls: 0
  mean |vx| <= 0.005 m/s
```

Additional required reports:

- mean speed / track ratio
- push recovery success rate
- terrain success rate
- foot clearance / swing peak
- action saturation
- per-joint target velocity vs corrected envelope

## References

Verified from arXiv:

- `2512.01996`, *Learning Sim-to-Real Humanoid Locomotion in 15 Minutes*:
  supports the broad recipe of massive parallel humanoid RL, randomized
  dynamics, rough terrain, and push perturbations on Unitree G1 / Booster T1.
- `2502.12152`, *Learning Getting-Up Policies for Real-World Humanoid Robots*:
  supports an easy-to-hard two-phase refinement idea for real-world G1
  deployment under varied terrains and surfaces.

Reference caveat:

- `2511.12390` resolves to neural teleoperation, not the concrete locomotion DR
  range paper described in the prompt.
- `2505.17627` resolves to H2-COMPACT co-manipulation with randomized payloads
  and friction, not a pure per-episode locomotion DR recipe.

The requested numeric ranges are therefore carried as project-configured ranges
for this branch: friction `0.5-1.25`, mass `+/-10%`, small COM perturbations,
control latency, observation noise, push perturbations, and easy-to-hard
terrain. Do not cite `2511.12390` or `2505.17627` as direct support for those
exact locomotion ranges without a later primary-source check.
