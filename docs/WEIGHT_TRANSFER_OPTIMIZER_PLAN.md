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
