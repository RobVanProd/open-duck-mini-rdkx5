# Weight-Transfer Optimizer Plan

Purpose: replace hand-shaped teacher/planner sweeps with an offline
short-horizon optimizer that searches directly for seed-robust low-command
target sequences.

This is offline only. It does not train, deploy, SSH, or touch the robot.

## Why This Branch Exists

The target-source campaign has now bracketed the failure:

```text
aggressive teacher terms:
  forward velocity improves
  lateral impulse exceeds gate

staged balance gates:
  lateral velocity reaches gate
  forward velocity collapses near zero
```

That means another wider grid over roll, swing, push, reach, or gate terms is
unlikely to answer the core question. The next generator should search the
short-horizon trade space directly:

```text
forward displacement
  vs
lateral velocity/base-y
  vs
single-support timing
  vs
pitch/base-height safety
  vs
target velocity envelope
```

## Proposed Optimizer

Use simulator-in-the-loop random shooting or CEM over compact target-sequence
parameters, not full per-tick 14-DOF action sequences.

Candidate parameterization:

```text
period_s
left/right support timing
lateral roll knots
hip-pitch reach knots
knee lift knots
ankle lift/pitch knots
stance push knots
optional pitch target knots
```

The optimizer should produce the same JSONL trace schema as the existing target
tools so `tools/score_target_candidates_objective.py` remains the gate.

## Objective

Optimize a worst-seed score over seeds `0,2` first:

```text
maximize:
  mean_vx
  single_support_pct
  contact_transitions
  done_margin

penalize:
  abs(vy) p95
  abs(base_y) p95
  double_support dwell
  no-support dwell
  body pitch p95
  low base height
  target velocity p95
  action saturation
```

The optimizer is allowed to find non-intuitive target timing, but it is not
allowed to pass by exceeding the measured actuator envelope or by relying on
one lucky seed.

## Stop / Go Rules

Proceed only if an optimized source produces:

```text
100 tick window:
  mean vx >= 0.04 m/s on seeds 0 and 2
  vy_abs_p95 <= 0.12 m/s
  double_support <= 90%
  single_support >= 8%
  each single-support side >= 2%
  no falls inside window

150 tick window:
  same gates preferred before building a target dataset
```

If the optimizer improves forward velocity only by violating lateral or
actuator gates, do not train. That result means the low-command target-source
problem remains unsolved.

If the optimizer meets lateral/contact gates but still cannot produce forward
velocity, document that as stronger evidence that this morphology/controller
needs a state-feedback teacher rather than open-loop target sequences.

## Non-Goals

- Do not train from optimizer traces until 100/150 tick seed-robust gates pass.
- Do not run robot validation.
- Do not relax the measured actuator envelope to force a pass.
- Do not use a single seed as proof.
- Do not keep expanding hand-shaped random grids as a substitute for this
  optimizer.

## First Implementation Slice

Add a tool that can:

```text
1. sample compact target-sequence parameters
2. replay each candidate in the same Open Duck Playground env
3. write JSONL traces with the existing schema
4. compute an inline worst-seed objective
5. emit compact markdown/json optimizer summaries
```

The first run should be small and CPU-safe:

```text
iterations: 2-3
candidates per iteration: 8-16
seeds: 0,2
duration: 2-3 s
```

If this produces no directionally useful candidates, the next branch should be
a closed-loop state-feedback teacher, not more target-shape random search.

## First Small Probe

Artifact:

```text
outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER.md
outputs/analysis/weight_transfer_optimizer.json
```

Run shape:

```text
iterations: 2
candidates_per_iteration: 4
seeds: 0,2
duration: 2.0 s
window: 100 ticks
```

Result:

```text
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
global best seed0 vx: -0.0029 m/s
global best seed2 vx: 0.0022 m/s
global best seed0 / seed2 vy95: 0.1096 / 0.1113 m/s
global best seed0 / seed2 double support: 88% / 92%
```

Interpretation: the first optimizer slice validates the tooling but not a
target source. It again finds the conservative basin: lateral velocity is near
gate, actuator target velocity is low, but forward displacement is nearly zero.
The next optimizer revision needs a less restrictive parameterization or a
stronger terminal forward-displacement term; simply iterating this small search
is unlikely to solve the target-source problem.

## Gate-Mode Probe

The optimizer was extended to sample planner step-gate modes:

```text
0: hard gate
1: soft gate
2: ungated step phase
```

Artifact:

```text
outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_GATE_MODE.md
outputs/analysis/weight_transfer_optimizer_gate_mode.json
```

Result:

```text
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
global best seed0 vx: -0.0036 m/s
global best seed2 vx: 0.0043 m/s
global best seed0 / seed2 vy95: 0.1065 / 0.1106 m/s
```

The best candidate used soft gating. Relaxing the hard gate did not restore
forward displacement in this compact parameterization. The next useful change
is not more gate-mode sampling; it is an objective/parameterization change that
explicitly pays for terminal forward displacement while preserving the lateral
and support gates.

## Displacement-Weighted Probe

The scorer was extended with optional local-frame forward displacement metrics:

```text
--min-forward-displacement-m
--forward-displacement-weight
```

Artifact:

```text
outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_DISPLACEMENT.md
outputs/analysis/weight_transfer_optimizer_displacement.json
```

Result:

```text
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
best seed0 vx / dx: -0.0035 m/s / -0.0070 m
best seed2 vx / dx: 0.0015 m/s / 0.0030 m
```

All eight sampled candidates failed the forward-displacement gate. This makes
the conservative-basin diagnosis stronger: even when terminal local forward
progress is priced directly, the current compact planner parameterization does
not discover a useful forward step.

Important correction: this gate uses integrated local `vx`, not world-frame
`base_x`. Earlier world-x reporting was misleading when candidates yawed or
moved laterally.

## Forward-Intent Teacher Probe

The closed-loop teacher was extended with:

```text
--min-forward-scales
--feedforward-pushes
```

Artifact:

```text
outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT.md
outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT_SCORE_100.md
outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT_SCORE_150.md
```

Result:

```text
status: HOLD_NO_SEED_ROBUST_TARGETS
top aggregate rollout mean vx: 0.0320 m/s
100-tick top local dx seed0 / seed2: 0.0518 / 0.0420 m
100-tick top vy95 seed0 / seed2: 0.1917 / 0.1859 m/s
150-tick top local dx seed0 / seed2: 0.0757 / 0.0648 m
150-tick top vy95 seed0 / seed2: 0.2578 / 0.2530 m/s
```

Interpretation: forcing minimum forward intent does escape the no-displacement
basin, but only by recreating the lateral-impulse failure. This confirms the
core tradeoff with a corrected local-frame displacement metric:

```text
enough forward displacement -> lateral velocity too high
lateral velocity acceptable -> forward displacement too low
```

The next branch needs to control lateral momentum while preserving forward
displacement, not merely increase forward push.

## Lateral-Refine Confirmation

A focused lateral-refine teacher search was run after the forward-intent probe:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LATERAL_REFINE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The best objective-ranked windows became conservative and missed the forward
displacement gate, while the highest-displacement windows still violated the
lateral gate:

```text
100-tick top scored dx seed0 / seed2: 0.0261 / 0.0371 m
150-tick top scored dx seed0 / seed2: 0.0411 / 0.0372 m
best individual 100-tick dx: 0.0850 m with vy95 0.3083 m/s
best individual 150-tick dx: 0.0912 m with vy95 0.2634 m/s
```

This confirms that the current hand-shaped teacher/planner family has hit the
same Pareto surface:

```text
enough forward displacement -> excessive lateral impulse
lateral/contact gates -> too little forward displacement
```

The next optimizer/controller should explicitly model lateral momentum and
support transfer as state variables. Do not spend the next iteration on another
nearby parameter sweep over the same periodic teacher terms.
