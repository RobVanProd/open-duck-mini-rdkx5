# Phase 2 Domain-Randomized Robustness Training

status: `HOLD_STAGE_C_TERRAIN_Z002_TRACKING_MARGIN`

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
- push recovery was not part of the original canonical no-push candidate gate;
  `tools/eval_policy_with_actuator_bridge.py` and
  `tools/run_candidate_seed_sweep.py` now expose explicit default-off
  `--eval-push-enable` controls and recovery metrics
- terrain curriculum now has an eval-only hfield vertical scale override via
  `--terrain-hfield-z-scale`; this creates a temporary scene XML for the worker
  and removes it after env construction, so the Playground checkout is not
  permanently modified
- the training smoke wrapper also accepts `--terrain-hfield-z-scale`; it backs
  up the selected task XML, patches the hfield z scale for the subprocess, and
  restores the original XML in `finally`

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

```text
decision:
  outputs/analysis/PHASE2_STAGE_B_DECISION.md

status:
  HOLD_STAGE_B_PUSH_DR_ERODES_FORWARD_MOTION
```

Two offline Stage B attempts were run from the trainable A2 164k checkpoint:

- `stage_b1_full_flat_gentle_push_from_a2_gpu`: full flat physics
  randomization plus gentle pushes. It completed training but regressed to
  near-standstill at `x=0.08`; best track ratio was `0.0467`.
- `stage_b0_mild_push_from_a2_gpu`: narrow randomization plus mild pushes. It
  completed training and preserved more motion, but still held with best raw
  track ratio `0.1898`. Constant gain wrappers up to `1.20` did not recover a
  passing gait; best gain result was `0.2176`.

Do not advance to rough terrain yet. The current blocker is preserving forward
motion while adding push/randomization robustness on flat terrain.

Push-eval plumbing result:

```text
analysis:
  outputs/analysis/PHASE2_PUSH_EVAL_PLUMBING.md

status:
  PUSH_EVAL_MODE_ADDED
```

The canonical no-push candidate gate remains unchanged. Push perturbations are
now an explicit eval mode with event counts, recovery success rate, applied
velocity impulse magnitude, recovery-window pitch, and recovery-window base
height.

Stage A mild-push CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_PUSH_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_push_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  push interval: 1.0-1.5 s
  push magnitude: 0.05-0.10

result:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  duration_complete: 8/8
  mean track ratio: 0.3533
  max tracking p95: 0.1975 rad
  max velocity excess: 0.0000 rad/s
  mean push recovery success: 0.9704
```

This establishes that the Stage A candidate already tolerates mild push
perturbations in evaluation. The Stage B training holds should be read as
training erosion of forward motion under push/randomization, not as proof that
mild pushes immediately break the Stage A gait. Local ROCm/MJX timed out a
one-second closed-loop push smoke after `600 s`, so local GPU should not be
used for correctness gates until that backend path is fixed.

Stage A moderate-push CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_PUSH_MODERATE_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_push_moderate_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  push interval: 1.0-1.5 s
  push magnitude: 0.10-0.20

result:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  duration_complete: 8/8
  mean track ratio: 0.3467
  max tracking p95: 0.1964 rad
  max velocity excess: 0.0000 rad/s
  mean push recovery success: 0.9704
```

This confirms the promoted Stage A candidate has push margin in evaluation at
least through `0.20` impulse magnitude. The next Stage B training attempt
should focus on preserving this already-present behavior while adding physics
randomization, not on adding push perturbations as a first-order discovery
signal.

- flat terrain
- full physics randomization
- gentle pushes
- same corrected envelope gate

Stage C:

- existing rough hfield terrain
- full physics randomization
- gentle pushes

Stage A rough-terrain CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_ROUGH_TERRAIN_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_rough_terrain_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  task: rough_terrain_backlash
  push: disabled

result:
  HOLD
  falls/terminations: 5/8
  duration_complete: 3/8
  mean track ratio: -0.5120
  max velocity excess: 0.0000 rad/s
```

This separates the next blocker cleanly: the promoted Stage A candidate has
flat-terrain push margin, but the existing rough hfield terrain breaks the gait
without requiring any target-velocity envelope violation. Terrain should
therefore enter through a gentler curriculum than the stock rough task, or via
training that preserves the Stage A flat gait while increasing foot clearance
and contact margin.

Scaled-terrain plumbing smoke:

```text
command:
  --task rough_terrain_backlash
  --terrain-hfield-z-scale 0.002

result:
  worker loaded the temporary scaled XML and removed it after env construction
```

Use this knob to measure a terrain-feasibility curve before training:

```text
flat terrain
rough_terrain_backlash --terrain-hfield-z-scale 0.002
rough_terrain_backlash --terrain-hfield-z-scale 0.005
stock rough_terrain_backlash       # hfield z scale 0.01
```

Training wrapper terrain override smoke:

```text
tool:
  tools/run_actuator_bridge_training_smoke.py --terrain-hfield-z-scale 0.002

artifact:
  outputs/analysis/terrain_training_override_smoke/

result:
  PASS_SMOKE_RUN
  destination_sha256_before == destination_sha256_restored
  Playground XML restored to stock hfield size 10 10 .01 0.1
```

Stage A z-scale `0.002` terrain gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z002_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_terrain_z002_gate_cpu.json

result:
  NEAR_PASS
  duration_complete: 8/8
  falls: 0/8
  pass: 7/8
  one tracking miss: seed 7 max tracking p95 0.2001 rad
  mean track ratio: 0.4033
  max velocity excess: 0.0000 rad/s
```

This is the first useful terrain curriculum rung: it is stable across all
seeds and only misses the strict gate by `0.0001 rad` on one seed. Treat it as
the starting point for terrain hardening, not as a robot-ready terrain pass.

Stage A z-scale `0.005` terrain gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z005_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_terrain_z005_gate_cpu.json

result:
  HOLD
  duration_complete: 7/8
  falls/terminations: 1/8
  pass: 2/8
  tracking holds: 5/8
  mean track ratio: -0.0485
  max velocity excess: 0.0000 rad/s
```

The terrain curve is now bracketed:

```text
flat: pass
z=0.002: near-pass, 8/8 upright, one 0.0001 rad tracking miss
z=0.005: hold, one fall and multiple tracking holds
z=0.010 stock rough: hard hold, 5/8 terminations
```

The next terrain-training rung should target z-scale `0.002` first, not `0.005`
or the stock rough hfield.

Stage C z-scale `0.002` terrain-training attempts:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_DECISION.md

status:
  HOLD_STAGE_C_TERRAIN_Z002_TRACKING_MARGIN
```

Three narrow terrain fine-tunes were run offline on local ROCm and screened on
the same two-seed, five-second `z=0.002` terrain benchmark:

- `stage_c0_terrain_z002_preserve_from_a2_gpu`: terrain fine-tune with narrow
  DR and strong gait preservation.
- `stage_c1_terrain_z002_tracking_from_c0_gpu`: C0 warm-start with an
  actuator bridge tracking penalty.
- `stage_c2_terrain_z002_targetrate_from_c1_gpu`: C1 warm-start with target
  rate penalty.

All three training runs completed successfully and restored the temporary
terrain XML. None produced a promotable terrain candidate.

Best short-screen result:

```text
policy: c0_245760
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2040 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1965 rad
mean track ratio: 0.3965
mean vx: 0.0317 m/s
velocity excess: 0.0000 rad/s
```

C2's best tracking result was similar but still held:

```text
policy: c2_163840
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2044 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1941 rad
mean track ratio: 0.4070
mean vx: 0.0326 m/s
velocity excess: 0.0000 rad/s
```

Inspection shows the remaining miss is not falling, saturation, or corrected
velocity-envelope excess. It is a small terrain-induced joint-target tracking
margin, dominated on the screen by seed 0 and the left knee. Bridge tracking is
lower than the strict gate miss, so simply increasing the bridge tracking
penalty is not the right lever.

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
