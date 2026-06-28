# Phase 2 Domain-Randomized Robustness Training

status: `HOLD_STAGE_C7_GATE_SELECTION_PARTIAL`

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

Stage C clearance instrumentation:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_CLEARANCE_INSTRUMENTATION.md

screen:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_CLEARANCE_SCREEN_CPU.md

status:
  PASS_CLEARANCE_METRICS_ADDED
```

The closed-loop evaluator now reports passive foot-clearance and support
metrics from existing `foot_site_pos_m` and `foot_contacts` records. This does
not change policy stepping, reward, training, or gates.

Focused seed-0 z-scale `0.002` terrain comparison:

```text
a2_gain099:
  tracking p95: 0.2079 rad
  min swing peak lift: 0.0153 m
  single support: 17.6%
  double support: 82.4%

c0_245760:
  tracking p95: 0.2040 rad
  min swing peak lift: 0.0159 m
  single support: 16.8%
  double support: 83.2%

c2_163840:
  tracking p95: 0.2044 rad
  min swing peak lift: 0.0163 m
  single support: 17.2%
  double support: 82.8%
```

The terrain blocker is therefore consistent with a low-clearance shuffle:
mostly double support, very low swing peak, and little true single-support
time. The next Stage C training objective should target swing clearance and
double-support dwell directly while preserving the corrected envelope and the
strict tracking gate.

Stage C3 contact-timing fine-tune:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C3_CONTACT_TIMING_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C3_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C3_CONTACT_TIMING_NOT_ENOUGH
```

C3 warm-started from the best C2 terrain checkpoint and added forward
single-support, double-support dwell, and contact-transition pressure while
keeping the corrected fitted bridge and `z=0.002` rough-terrain screen.
Training completed successfully and restored the temporary terrain XML.

The best screened checkpoint was `c3_245760`:

```text
tracking p95: 0.2046 rad
track ratio: 0.4061
velocity excess: 0.0000 rad/s
min swing peak lift: 0.0165 m
single support: 20.8%
double support: 79.2%
```

This moved support timing in the intended direction, but it did not clear the
strict `0.20 rad` tracking gate and did not materially raise swing height. C3
therefore does not promote a terrain candidate. The next useful Stage C step is
not another contact-timing-only retry; it should add an explicit swing
clearance/feet-height objective or a target-source change that raises the foot
while preserving corrected-envelope compliance and command conditioning.

Stage C4 clearance-reward plumbing:

```text
artifact:
  outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_REWARD_PLUMBING.md

status:
  PASS_CLEARANCE_REWARD_PLUMBING
```

The Playground task now exposes a default-off `forward_swing_clearance` cost
that measures swing peak lift above each foot's last stance height and applies
only under nonzero forward command. This avoids world-height assumptions on
heightfield terrain. The RDK training wrapper forwards the matching
`--forward-swing-clearance-*` flags, and a tiny CPU smoke plus direct one-step
env activation check passed. No candidate was promoted.

The next Stage C run should be a C4 fine-tune from the best C2/C3 terrain
lineage with a mild clearance penalty, not a new contact-timing-only retry.

Stage C4 clearance run:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C4_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C4_CLEARANCE_OVERDRIVES_GAIT
```

C4 warm-started from `c3_245760` and added a clearance cost with target lift
`0.03 m` and scale `-0.05`. Training completed and restored the terrain XML,
but the final checkpoint overcorrected:

```text
c4_245760:
  samples: 33
  termination: fall_or_nan
  tracking p95: 0.4266 rad
  track ratio: -6.0028
  corrected velocity excess: 3.2400 rad/s
  min swing peak lift: 0.0193 m
  single support: 81.8%
  double support: 9.1%
```

The clearance objective has leverage, but this setting destroyed the gait
instead of producing a stable higher-clearance shuffle. A weaker C4b retry was
attempted with scale `-0.005` and target `0.025 m`, but it failed before
training on the local ROCm path with `rocblas_status_internal_error` during JAX
evaluator reset. Treat C4b as a backend hold, not a policy result.

The next terrain attempt should stage the clearance pressure more gently and
preserve the C3 gait with stronger restore-policy/behavior prior pressure or
more frequent checkpoint screening.

Stage C5a clearance-preservation run:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C5A_CLEARANCE_PRESERVE_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C5A_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C5A_RETREATS_TO_DOUBLE_SUPPORT
```

Two immediate follow-up runs after C4 failed before training with local ROCm
`rocblas_status_internal_error` during JAX evaluator reset. A basic JAX ROCm
matmul still passed. Retrying with:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

allowed C5a to train, so use this as the local ROCm workaround for short
training attempts unless a cleaner backend fix is found.

C5a used stronger gait preservation and much weaker clearance pressure:

```text
restore_policy_kl_scale: 2.5
forward_swing_clearance_scale: -0.001
forward_swing_clearance_target_m: 0.022
```

It stayed stable and in-envelope, and reduced strict tracking p95 below
`0.20 rad`, but only by retreating into lower forward progress and even less
clearance:

```text
c5a_81920:
  tracking p95: 0.1946 rad
  track ratio: 0.2220
  corrected velocity excess: 0.0000 rad/s
  min swing peak lift: 0.0086 m
  single support: 9.6%
  double support: 90.4%
```

This is not a terrain candidate. It exposes a reward loophole: touchdown
clearance penalties can be avoided by reducing swing/transition behavior. The
next C-stage attempt should keep transition/single-support pressure active
while using very weak clearance pressure and moderate, not overwhelming,
restore-policy KL.

C6 tested that pairing:

```text
artifact: outputs/analysis/PHASE2_STAGE_C6_TRANSITION_CLEARANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C6_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C6_TRANSITION_PRESSURE_RETREATS_TO_DOUBLE_SUPPORT
```

C6 completed a short GPU training run from the best C3 checkpoint using the
local ROCm workaround:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

The recipe used moderate gait preservation, stronger single-support/contact
transition pressure than C3, and very weak clearance pressure:

```text
restore_policy_kl_scale: 1.25
forward_single_support_scale: 0.30
forward_contact_transition_scale: 0.20
forward_swing_clearance_scale: -0.0005
forward_swing_clearance_target_m: 0.020
num_timesteps: 81920
```

The final checkpoint stayed stable and in-envelope, but it regressed further
into a low-clearance double-support shuffle:

```text
c6_81920:
  tracking p95: 0.1654 rad
  track ratio: 0.0985
  corrected velocity excess: 0.0000 rad/s
  min swing peak lift: 0.0072 m
  single support: 4.0%
  double support: 96.0%
```

Decision: do not promote C6. The C-stage evidence now shows that scalar
clearance/contact-timing reward terms are being satisfied by reducing motion
rather than by producing higher-clearance stepping. The next terrain branch
needs gate-selected training or a target/teacher that explicitly contains
higher-clearance steps, not another small scalar PPO tweak.

C7 tested gate-selected terrain training:

```text
artifact: outputs/analysis/PHASE2_STAGE_C7_GATE_SELECTION_DECISION.md
checkpoint screen: outputs/analysis/PHASE2_STAGE_C7_TERRAIN_Z002_SCREEN_CPU.md
8-seed screen: outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_Z002_8SEED_CPU.md
status: HOLD_STAGE_C7_GATE_SELECTION_PARTIAL
```

C7 reused the C6 recipe but exported frequent checkpoints (`ppo_num_evals: 8`)
so terrain metrics could select the best transient checkpoint instead of using
the final reward-selected checkpoint. This worked in a limited sense:
`c7_35120` passed the focused seed-0 `z=0.002` terrain screen while later
checkpoints regressed into low forward progress.

The best transient checkpoint:

```text
checkpoint: c7_35120
sha256: ee0b7013bf588b2aab4b8efe3c7ab10b1d8b901d786282717cda3b18b5c8b5d7
```

Eight-seed `z=0.002` screen:

```text
passes: 5/8
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.2671
mean vx: 0.0214 m/s
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.1918 rad
mean min swing peak lift: 0.0105 m
mean single support: 11.4%
mean double support: 88.45%
```

Decision: gate-selected checkpointing is useful and should remain part of
terrain work, but C7 is not a terrain robustness candidate. It improves
tracking relative to C3 by reducing motion and still produces a low-clearance,
mostly double-support shuffle. The next branch should change the target
manifold: mine or generate higher-clearance stepping demonstrations, or add a
hard step-clearance/step-advance constraint for nonzero command.

Follow-up C7 trace diagnostic:

```text
artifact: outputs/analysis/PHASE2_STAGE_C7_TRACE_AND_SWING_BALANCE_PLUMBING.md
status: PASS_SWING_BALANCE_PLUMBING
```

Comparing a passing C7 seed (`2`) to a low-progress seed (`4`) showed the
failure mechanism directly:

```text
seed 2: 18.8% single support, 33 support transitions, 3 left swing segments, 7 right swing segments
seed 4: 4.0% single support, 13 support transitions, 0 left swing segments, 2 right swing segments
```

The failing seed almost never exits double support and never swings the left
foot. A default-off `forward_swing_balance` hook was added to penalize
one-sided swing usage over a forward-command window, with RDK wrapper and eval
plumbing. A tiny CPU smoke passed. The next C-stage run may test this hook, but
it must still use gate-selected checkpoints and corrected terrain metrics.

C8 tested that hook:

```text
artifact: outputs/analysis/PHASE2_STAGE_C8_SWING_BALANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C8_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C8_SWING_BALANCE_TOO_STRONG
```

C8 used the same C7-style gate-selected terrain recipe with:

```text
forward_swing_balance_scale: -0.05
forward_swing_balance_grace_steps: 20
```

It completed training, but all trained checkpoints held for low forward
progress on the focused seed-0 screen. The best trained checkpoint was worse
than C7's early transient:

```text
c7_35120 seed 0: track ratio 0.2606, single support 11.2%, min swing peak 0.0104 m
c8_35120 seed 0: track ratio 0.1819, single support 6.8%, min swing peak 0.0084 m
```

Decision: do not promote C8. The hook has leverage, but this balance pressure
pushes the policy toward lower motion rather than balanced stepping. Do not
increase this scalar pressure. Use it only with a target that first preserves
motion, or with a much weaker value after a higher-clearance target source is
available.

After C8, the evaluator was extended with passive swing-excursion metrics:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SWING_EXCURSION_METRICS.md
status: PASS_SWING_EXCURSION_METRICS_ADDED
```

The standard seed-sweep report now includes:

```text
min_swing_segments
min_rel_x_range_p95
```

The corrected C7 pass/fail trace comparison now reads:

```text
seed 2 pass: min_swing_segments 3, min_rel_x_range_p95 0.0059 m, track ratio 0.3577
seed 4 hold: min_swing_segments 0, min_rel_x_range_p95 0.0000 m, track ratio 0.1918
```

Future terrain gates should treat these as first-class diagnostics. A policy
that passes tracking by keeping one foot effectively planted is still a terrain
hold, even if actuator tracking p95 is below threshold.

The seed-sweep tool now also supports default-off hard terrain swing gates:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SWING_HARD_GATE_PLUMBING.md
status: PASS_TERRAIN_SWING_HARD_GATE_PLUMBING
flags:
  --min-swing-segments-per-foot
  --min-swing-rel-x-range-p95-m
  --min-swing-peak-lift-m
```

When these flags are set, a nominal `PASS_CANDIDATE_SIM_GATE` can be downgraded
to `HOLD_CANDIDATE_TERRAIN_SWING`. A downgrade-path validation intentionally
set `min_swing_peak_lift_m=0.02` and correctly downgraded C7 seed 2 from a
nominal pass to `HOLD_CANDIDATE_TERRAIN_SWING`.

Action-gain terrain diagnostic:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_ACTION_GAIN_DIAGNOSTIC.md
status: HOLD_ACTION_GAIN_NOT_TERRAIN_FIX
tested gains: 1.05, 1.10
```

Small global action-gain increases on C7 `35120` do not fix the terrain/carpet
failure. At gain `1.05`, seed 2 still passed but seed 4 stayed planted with
`0` min swing segments, `0.0000 m` min relative-x swing range, `0.0016 m` min
swing peak lift, `0.8%` single support, and `99.2%` double support. At gain
`1.10`, even seed 2 regressed to low forward progress. Both tests stayed inside
the corrected velocity envelope, so the issue is stance/swing structure rather
than insufficient global action amplitude.

Forward swing-advance plumbing:

```text
artifact: outputs/analysis/PHASE2_FORWARD_SWING_ADVANCE_PLUMBING.md
status: PASS_FORWARD_SWING_ADVANCE_PLUMBING
```

The Playground and RDK training wrapper now expose a default-off
`forward_swing_advance` cost. It tracks each foot's forward position in the
body/IMU frame at stance and penalizes touchdown if the swing foot did not
advance at least the configured target distance in the commanded direction. A
tiny CPU smoke on `rough_terrain_backlash --terrain-hfield-z-scale 0.002`
passed with `forward_swing_advance_scale=-0.001`,
`forward_swing_advance_target_m=0.005`, and
`forward_swing_advance_huber_delta=0.002`.

Use this as a direct step-advance pressure in the next C-stage terrain branch,
with gate-selected checkpoints and the hard terrain swing gate enabled. Do not
increase global action gain as the terrain fix.

C9 tested the hook:

```text
artifact: outputs/analysis/PHASE2_STAGE_C9_SWING_ADVANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C9_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C9_SWING_ADVANCE_RETREATS_TO_LOW_PROGRESS
```

C9 warm-started from C7 `35120` and added
`forward_swing_advance_scale=-0.01`, target `0.005 m`, and Huber delta
`0.002`. Training completed on local GPU and preserved corrected-envelope
compliance, but all trained checkpoints regressed the pass-like seed 2 to low
forward progress and never recovered the planted-foot seed 4. Seed 4 stayed at
`0` min swing segments for every checkpoint.

Decision: keep the hook, but do not promote C9 and do not simply increase
scalar swing-advance pressure. The next terrain branch needs a
higher-clearance alternating-step target source or a hard step-advance
constraint that cannot be satisfied by retreating into double support.

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
- per-foot swing segment count and relative-foot excursion
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
