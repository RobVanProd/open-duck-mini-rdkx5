# Movement Bootstrap V10 Plan

status: `PLANNED_OFFLINE_ONLY`

V10 is not approved for robot testing. This plan is for the next offline
training/evaluation iteration only.

## Baseline To Beat

The current V7/V9 lineage baseline is:

```text
outputs/analysis/V7_V9_MULTI_SEED_STABILITY_BASELINE.md
```

At `command_x=0.08` with the fitted actuator bridge:

```text
V7: 5/8 falls, 3/8 standstill completions, mean samples 311.75
V9: 5/8 falls, 3/8 standstill completions, mean samples 312.00
```

V9 did not materially improve the distribution versus V7.

## Failure Surfaces

Representative V9 traces are recorded in:

```text
outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/V9_FOUR_SURFACE_ONSET_COMPARISON.md
```

The failures branch within the first few ticks:

```text
seeds 0 and 6: lunge / pitch-over
seed 5: reverse or negative local velocity failure
seeds 1 and 7: early base-height/contact-support collapse
seeds 2, 3, 4: low-forward-progress standstill
```

This is not one lunge defect with several endings. It is a seed-dependent
behavior fragmentation problem.

## V10 Objective

V10 should optimize behavioral consistency across seeds before optimizing fine
stability margin.

Required behavior:

```text
same forward-moving gait family across seeds
no lunge / command overshoot regime
no reverse local velocity regime
no early support/contact collapse regime
no stable standstill exploit
target velocity remains within fitted actuator envelope
action saturation remains low
```

## Training Design Direction

Use the moving checkpoint lineage one more time, but do not blindly anchor the
full action vector. The teacher/continuity term should preserve gait shape while
allowing the new policy to reduce commitment/aggression.

Preferred structure:

- teacher or trust-region term against a moving checkpoint,
- lower weight on uniform action cloning than on gait phase/shape consistency,
- forward-direction consistency penalty when command_x is positive,
- explicit penalty for negative local-base-x velocity under positive command,
- forward overshoot penalty,
- pitch and pitch-rate damping,
- base-height collapse penalty,
- contact/support timing penalty for early one-foot-only or no-foot support,
- fitted actuator bridge and velocity envelope active throughout.

Avoid:

- a pure action-cloning anchor that preserves the lunge,
- a pure stability objective that falls back to standstill,
- more small scalar target-velocity-envelope tweaks,
- declaring success from one seed or a one-second sweep.

## Evaluation Gate

Run the same multi-seed gate after training:

```bash
python3 tools/run_candidate_seed_sweep.py \
  --policies path/to/v10_candidate.onnx \
  --seeds 0-7 \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --run \
  --output-dir outputs/analysis/movement_bootstrap_v10_seed_sweep_x008_fitted
```

V10 is useful only if it shifts the distribution:

```text
fall count < 5/8
mean samples > 312
standstill completions < 3/8
more seeds with useful positive forward tracking
lower pitch on lunge seeds
higher base height on collapse seeds
no reverse local-velocity seed
```

Then run full candidate gates at `x=0.0` and `x=0.08` before any robot-side
consideration.

## Exit Rule

If V10 starts from the same lineage and still lands near:

```text
about 5/8 falls
about 3/8 standstill completions
mean samples around 312
same four failure surfaces
```

then stop iterating V11/V12 down the same anchor path. Treat the phase-1/V7/V9
lineage as exhausted and switch to a structurally different bootstrap, such as:

- a different moving phase-1 seed,
- fresh training with consistency and support terms active from phase 1,
- a gait-shape teacher distilled from multiple moving seeds rather than one
  fragile checkpoint,
- separate motion prior that rewards coherent phase/contact structure before
  high forward velocity.

The phase-1 result still proves in-envelope motion exists, but the current
lineage has not produced a stable, consistent gait distribution.
