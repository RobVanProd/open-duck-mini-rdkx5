# Phase 2 Domain-Randomized Robustness Training

status: `PASS_STAGE_A_GAIN099_READY_FOR_STAGE_B`

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
trainable warm-start checkpoint: outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint
step-0 exported ONNX: outputs/analysis/ppo_bc_command_conditioned_rate175_step0.onnx
warm-start fidelity report: outputs/analysis/ppo_bc_command_conditioned_rate175_step0_export_fidelity.json
```

The carpet test showed the current policy is actuator-trackable on the ground
but does not lift/clear its feet enough to walk forward on medium carpet. Phase
2 should therefore treat robustness and terrain/contact margin as the target,
not actuator tracking alone.

## Trainable Warm-Start

The user constraint is correct: Phase 2 must warm-start from the Phase 1 gait,
not train from scratch.

The local Playground PPO runner warm-starts from a Brax/Orbax checkpoint via
`--restore_checkpoint_path`. A verified step-0 PPO checkpoint now exists for
the Phase 1 `rate175` candidate:

```text
checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint

fidelity:
  status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
  p95 abs error: 1.1920928955078125e-07
  max abs error: 3.2782554626464844e-07
```

This checkpoint was constructed from the Phase 1 BC MLP NPZ, exported through
the PPO ONNX path, and compared against the packaged Phase 1 ONNX before any
PPO updates. Use it as the trainable Phase 2 warm-start. Do not launch a
scratch PPO run and call it Phase 2.

## Existing Playground Hooks

The local Playground now provides the requested DR scaffolding:

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
- staged CLI overrides for friction, mass, COM, qpos jitter, actuator gain,
  push intervals/magnitudes, observation noise, and leg-geometry jitter
- default-off leg-link body-position geometry jitter

Missing or partial:

- stage advancement is not automated by corrected-bridge gates

## Curriculum

Stage A:

- flat terrain
- narrow physics randomization
- no push
- corrected bridge near fitted range
- behavior prior strong enough to preserve gait

Stage A first run result:

```text
training artifact:
  outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push_gpu/smoke_20260628T015607Z_gpu

decision:
  outputs/analysis/PHASE2_STAGE_A_DECISION.md

status:
  HOLD_STAGE_A_LOW_FORWARD_PROGRESS
```

The first Stage A run completed successfully as an offline GPU training job but
regressed command-conditioned walking. It passed `x=0.0` standing 8/8 and stayed
inside the corrected velocity envelope, but the final export held on `x=0.08`
forward progress across all 8 seeds. The PPO step-0 warm-start export still
matches the packaged Phase 1 candidate in closed-loop rollout, so the regression
comes from the Stage A PPO/DR update rather than a broken trainable checkpoint.

Do not advance to Stage B from this run. The next Stage A retry should preserve
the Phase 1 behavior more tightly before widening robustness:

- stronger restore-policy KL,
- lower learning rate,
- shorter horizon or more frequent checkpointing,
- stronger behavior prior or teacher-action continuity.

Stage A2 retry result:

```text
decision:
  outputs/analysis/PHASE2_STAGE_A2_DECISION.md

status:
  PASS_STAGE_A_GAIN099_PROMOTED_FOR_STAGE_B
```

A2 improved the failure mode. The 164k checkpoint completed `x=0.08` 8/8 with
no falls and no envelope excess, and passed `x=0.0` 8/8, but missed strict
tracking by `0.0004 rad` on one seed. A minimal 0.99 action-gain ONNX wrapper
fixed that tracking miss while preserving command conditioning:

```text
candidate:
  policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx

candidate_sha256:
  a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4

x=0.08:
  PASS_CANDIDATE_SIM_GATE 8/8
  mean track ratio: 0.3542
  max tracking p95: 0.1984 rad

x=0.0:
  PASS_CANDIDATE_SIM_GATE 8/8
  mean vx: 0.0004 m/s
```

This is a Stage A sim promotion, not robot approval. Stage B may proceed
offline from this lineage.

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
