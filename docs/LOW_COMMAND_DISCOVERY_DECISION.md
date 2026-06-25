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
