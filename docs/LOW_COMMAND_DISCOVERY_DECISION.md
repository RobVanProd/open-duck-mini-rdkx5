# Low-Command Discovery Decision

Date: 2026-06-24

## Current Decision

The project should stop launching more pure reward-weight variants of the
V5-V18 line. V18 answered the cheap low-command question:

```text
command: x=0.04
dynamics: vanilla, no actuator bridge
restore/anchor: none
training/eval command: same low-command band
```

It still failed to produce coherent forward motion. A corrected reward replay
and analytic reward-signal check then showed the intended V18 reward signal is
active and prefers forward local velocity over standing.

Therefore the current blocker is not:

```text
actuator envelope
x=0.08 being too hard
anchor lineage choice
simple forward/reverse sign bug
inactive command-progress failure
standstill being immediately rewarded above forward motion
```

The current blocker is:

```text
cold-start locomotion discovery / optimization landscape
```

## Evidence

V18 A100 phase-1 gate at `x=0.04`:

```text
seed 0: low forward progress, track ratio 0.0165
seed 1: fall/reverse, track ratio -2.4426
seed 2: low forward progress, track ratio 0.0575
seed 3: low/reverse progress, track ratio -0.1171
```

V18 corrected reward replay with phase reward overrides:

```text
seed 0: command-progress failure at 50 samples, track ratio 0.0845
seed 1: reverse/collapse at 33 samples, track ratio -2.3845
```

Analytic immediate reward signal at `x=0.04`, before terminal failure:

```text
standstill reward: -1.3686
required-speed reward at vx=0.026: 1.6494
command-speed reward at vx=0.040: 2.2800
```

This means a small forward step is rewarded substantially above standing under
the intended V18 reward configuration.

## Stop Condition

Do not launch another large training run whose only purpose is to keep tuning
the same low-command reward weights.

This condition is now met:

```text
forward motion is positively rewarded
standing is not preferred by the immediate reward
PPO still failed to discover forward motion from cold start
```

Any next training run must test a different hypothesis than "slightly better
reward weights."

## Next Decisive Experiment

Run an imitation/reference-gait seed test. This is now represented by the
`movement_bootstrap_v19` staged recipe.

Goal:

```text
determine whether the current setup can refine an existing gait into reliable
low-command forward motion
```

Use either:

```text
1. upstream Open Duck reference-motion / imitation path
2. a hand-scripted toy gait bootstrap
3. a supervised/behavior-cloning seed from any walking trajectory
```

The upstream reference-motion path is available:

```text
reference artifact: playground/open_duck_mini_v2/data/polynomial_coefficients.pkl
nearest reference to x=0.04: 0.074_-0.037_-0.074
reference period: 0.54 s / 27 steps at 50 Hz
```

The active Playground imitation reward uses this reference for leg joint
pose/velocity, base velocity, base angular velocity, and foot-contact terms.
Head/neck dimensions exist in the reference data and runtime action vector, but
the leg-imitation error term excludes head/neck and antenna dimensions.

Important caveat:

```text
requested command: x=0.04, y=0.0, yaw=0.0
nearest reference command: x=0.074, y=-0.037, yaw=-0.074
sampled reference mean velocity: x=0.0772, y=-0.0417
reference lateral velocity p95_abs: 0.2804
```

So V19 tested whether a nearby reference gait could seed motion, but it did not
test a perfectly matched straight `x=0.04` reference. The next reference-path
debugging should account for this command mismatch before concluding that all
imitation/bootstrap approaches are exhausted.

Initial gate:

```text
command: x=0.04
dynamics: vanilla
bridge: disabled
seeds: multi-seed, preferably 0-7
grade metric: coherent forward motion across seeds
```

Outcomes:

```text
PASS_SEEDED_GAIT_REFINES:
  Seeded gait refines into reliable forward motion.
  Conclusion: cold-start discovery was the blocker.
  Next: reintroduce fitted actuator bridge, then expand command range.

HOLD_SEEDED_GAIT_DEGRADES:
  A working gait seed degrades into standstill, reverse, or collapse.
  Conclusion: reward/task landscape is actively hostile to forward gait.
  Next: inspect which reward/state transition destroys the reference behavior.

HOLD_NO_REFERENCE_GAIT_AVAILABLE:
  No usable reference gait can be loaded or scripted.
  Next: build the smallest hand-authored stepping pattern and score it first.
```

## Constraints

```text
no robot tests
no SSH
no deploy
no x=0.08 until x=0.04 passes across seeds
no fitted actuator bridge until coherent low-command motion exists
grade on forward motion distribution, not fall-count alone
use the pinned Colab helper / JAX 0.7.2 stack for GPU training
```

## Artifacts

```text
outputs/analysis/A100_V18_PHASE1_LOW_COMMAND_HOLD_SUMMARY.md
outputs/analysis/V18_PHASE1_REWARD_OVERRIDE_REPLAY_SUMMARY.md
outputs/analysis/LOW_COMMAND_REWARD_SIGNAL_V18.md
outputs/analysis/REFERENCE_MOTION_SEED_AUDIT.md
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V19.md
```

## V19 Partial Result

V19 was launched on an A100 through the pinned Colab helper. Phase 1 trained to
completion and entered the x=0.04 multi-seed gate, but the Colab session was
lost before final artifact bundling/download.

Recovered gate evidence:

```text
completed seeds: 0-5
seed 0: fall/termination, track ratio -0.0239
seed 1: reverse/collapse, track ratio -2.2442
seed 2: low progress/fall, track ratio 0.1931
seed 3: reverse/fall, track ratio -0.4032
seed 4: low progress/fall, track ratio 0.1999
seed 5: hard reverse/collapse, track ratio -8.1420
```

This does not support `PASS_SEEDED_GAIT_REFINES`. The reference-imitation reward
did not produce coherent low-command forward motion in the observed seeds.

Next offline question:

```text
Does the environment/reward preserve and reward the upstream reference
trajectory when it is followed, or does the task landscape destroy it?
```

V19 remains non-deployable. Do not run x=0.08, fitted bridge, or robot
validation from this candidate.

Additional artifact:

```text
outputs/analysis/A100_V19_REFERENCE_SEED_PARTIAL_HOLD_SUMMARY.md
```

## Reference Interpolation Finding

The raw nearest reference was command-mismatched, but the grid has enough
structure to synthesize a cleaner straight low-speed reference candidate:

```text
source keys:
  0.0_-0.037_-0.074
  0.0_0.037_-0.074
  0.074_-0.037_-0.074
  0.074_0.037_-0.074
interpolated mean velocity:
  x = 0.0426 m/s
  y = -0.0021 m/s
```

This means the next run should not repeat V19 as-is. Before V20, add explicit
support for a synthesized/interpolated straight `x=0.04` reference artifact or
score that artifact offline against the task rewards.

Artifact:

```text
outputs/analysis/REFERENCE_GRID_INTERPOLATION.md
```

The interpolated reference has also been materialized as a training-only
override:

```text
outputs/analysis/reference_motion_x004_override.pkl
replaced key: 0.074_-0.037_-0.074
validated lookup command: x=0.04, y=0.0, yaw=0.0
validated mean velocity: x=0.0426 m/s, y=-0.0021 m/s
```

V20 now has explicit workflow support for applying this override:

```text
recipe: movement_bootstrap_v20
override: outputs/analysis/reference_motion_x004_override.pkl
wrapper flag: --reference-motion-override
manifest: records source, destination, backup, and sha256 hashes
restore: original Playground reference file restored after the training subprocess
```

This keeps the override explicit and auditable. Do not silently patch the
Playground reference file outside the wrapper.

V20 is still a low-command offline discovery test:

```text
command: x=0.04
dynamics: vanilla
bridge: disabled
gate seeds: 0-7
pass criterion: coherent positive forward motion across seeds
```

Do not run x=0.08, fitted bridge, or robot validation until V20 passes the
x=0.04 vanilla multi-seed gate.

## V20 Matched Reference Result

V20 trained on A100 with the command-matched `x=0.04` reference override and
vanilla dynamics. The override was applied through the wrapper, hash-recorded,
and restored after training.

The A100 training phase completed and produced:

```text
candidate ONNX: 2026_06_25_033305_337920.onnx
reference override sha256: deb8553d72e162331e788ca2b7e3e055b765a2ae01642b15ae316f07afb55601
original reference restored: yes
```

The remote GPU seed gate died during seed 0 without an exit sentinel, so the
candidate was recovered from the partial artifact bundle and evaluated locally
on CPU with per-seed traces.

CPU trace gate at `x=0.04`, vanilla dynamics, seeds `0-7`:

```text
runs: 8
falls/early terminations: 8
duration_complete: 0
mean vx: -0.0539 m/s
mean track ratio: -1.3468
sample range: 33-152 ticks
mean lateral p95_abs velocity: 0.3793 m/s
```

Interpretation:

```text
V20 is HOLD_V20_MATCHED_REFERENCE_NO_LOCK.
The matched reference did not refine into coherent low-command forward motion.
The dominant failure is low/reverse forward progress, with lateral motion as a
tracked contributor but not a standalone explanation.
```

This closes the V19/V20 reference-mismatch branch:

```text
V19 failed with a mismatched raw nearest reference.
V20 corrected the reference command mismatch and still failed across seeds.
```

Next work should debug the imitation/reference-locking mechanism directly:

```text
1. verify phase alignment between policy rollout and reference clock
2. score a forced/reference-following rollout under the task rewards
3. inspect whether early command-progress termination prevents reference lock
4. consider behavior-cloning or supervised pretraining before PPO
5. do not launch another reward-weight-only variant
```

Artifacts:

```text
outputs/analysis/V20_MANUAL_SEED_GATE_CPU_TRACE_FULL.md
outputs/analysis/V20_MATCHED_REFERENCE_TRACE_SUMMARY.md
outputs/analysis/v20_matched_reference_trace_summary.json
```

## Reference Lock Signal

An analytic score of the V20 matched reference itself passes:

```text
status: PASS_REFERENCE_SIGNAL_COHERENT
linvel_x_mean: 0.0426 m/s
linvel_y_mean: -0.0021 m/s
linvel_y_abs_p95: 0.2350 m/s
progress_ratio over 70 ticks: 1.0512
command-progress failure floor: 0.2000
forward required ratio: 0.5500
ideal imitation raw reward: 6.0
ideal imitation scaled reward: 24.0
pre-terminal unclipped reward sum mean: 50.8050
```

This means:

```text
the matched reference kinematics satisfy the low-command progress signal
PPO still failed to lock onto or preserve it
```

The next branch is not reward-weight tuning. It is reference-locking and
reference/action-contract debugging:

```text
1. behavior-cloning / supervised action pretraining from the reference
2. phase-clock and reset alignment checks
3. controlled relaxation of early command-progress termination only while
   testing reference acquisition
4. lateral-sway handling, because the matched reference still has high
   lateral p95_abs velocity
```

Artifact:
`outputs/analysis/REFERENCE_LOCK_SIGNAL_V20.md`.

## Reference-Target Rollout

A direct reference-target rollout was added to test the next mechanism below
PPO. It replaces the ONNX policy with actions derived from the matched
reference joint targets while still respecting the runtime-style contract:

```text
target = home + action * action_scale
max_motor_velocity rate limit remains active
no teleporting qpos to the reference trajectory
```

Result at `x=0.04`, vanilla dynamics, seeds `0-7`:

```text
status: HOLD_REFERENCE_TARGET_TERMINATES
runs: 8
falls/early terminations: 8
duration_complete: 0
mean vx: -0.0105 m/s
mean track ratio: -0.2614
mean lateral p95_abs velocity: 0.3918 m/s
mean action saturation: 6.4967%
mean target clip p95: 0.0314 rad
mean sent target velocity p95: about 4.85 rad/s
mean joint tracking p95: 0.1876 rad
```

Pitch-chain details:

```text
left_hip_pitch action saturation: 23.1496%, sent velocity p95: 3.9927 rad/s
left_knee action saturation: 15.2756%, sent velocity p95: 5.2400 rad/s
left_ankle action saturation: 12.1260%, sent velocity p95: 3.9546 rad/s
right_hip_pitch action saturation: 18.7402%, sent velocity p95: 5.1082 rad/s
right_knee action saturation: 15.7480%, sent velocity p95: 5.2400 rad/s
right_ankle action saturation: 5.9843%, sent velocity p95: 5.1066 rad/s
```

Interpretation:

```text
The matched reference is coherent as a kinematic/reward signal, but direct
reference-derived actions do not produce a stable rollout through the current
action-scale and target-rate contract. This is no longer just a PPO discovery
problem. Before behavior cloning, inspect reference-to-action conversion,
phase/reset alignment, target-rate demand, lateral sway, and contact timing.
```

Additional artifact:
`outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20.md`.

## Reference Action Envelope

The direct rollout failure was then checked without simulation by comparing the
matched reference cycle against the deployed action contract:

```text
action = (reference_target - home) / action_scale
action_scale = 0.25
target velocity budget = 5.24 rad/s
```

Result:

```text
status: HOLD_REFERENCE_EXCEEDS_ACTION_ENVELOPE
closest phases to home: phases 5, 19, 6, 20, 18 have 0 saturated joints
left_knee target velocity p95/max: 8.0846 / 8.6417 rad/s
right_knee target velocity p95/max: 9.8963 / 13.2122 rad/s
right_hip_pitch target velocity p95/max: 5.4889 / 6.0116 rad/s
right_ankle target velocity p95/max: 4.8676 / 7.6140 rad/s
right_knee max_abs_action: 2.2704
right_hip_pitch max_abs_action: 1.9062
```

Interpretation:

```text
The V20 reference is not merely hard for PPO to discover. Raw reference joint
positions exceed the policy action envelope and target-rate envelope. A BC or
reference-lock phase should not train directly against raw polynomial joint
targets. The next reference path must first project/filter the reference into
the deployable action envelope or learn from realized stable targets.
```

Additional artifact:
`outputs/analysis/REFERENCE_ACTION_ENVELOPE_V20.md`.
