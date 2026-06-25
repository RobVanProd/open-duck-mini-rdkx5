# Target Objective Generator Spec

Date: 2026-06-25

## Purpose

Define the next offline target-generation step after the primitive-grid searches
found forward-motion snippets that are not seed robust.

This is not a training plan and not a robot-test plan.

## Current Finding

The target generator can produce low-command forward windows:

```text
command_x: 0.04
25-sample curated windows: up to 45
50-sample curated windows: up to 23
target velocity: inside envelope
tracking: inside curation gate
```

But all curated windows are from `seed_000`. Seed 2 repeatedly produces
review-only near misses:

```text
robust modes across seed_000 and seed_002: 0
seed0-curated / seed2-review near misses: 12
seed2 single_contact_pattern_dominates count: 64
seed2 high_lateral_velocity count: 40
```

The next generator should therefore optimize seed robustness, not merely sample
more primitive combinations.

## Objective

For each candidate primitive, evaluate all required seeds and score the worst
seed. A candidate should only be considered useful if every seed stays close to
the target envelope.

Primary score terms:

```text
forward_score:
  reward mean_vx near command_x
  reject mean_vx < 0.04 over the target window

lateral_penalty:
  penalize max(0, vy_abs_p95 - 0.12)
  seed2 near misses are often around 0.16-0.18 m/s

contact_penalty:
  penalize max(0, contact_dominance_pct - 95)
  seed2 near misses often hit 100% dominance

posture_penalty:
  penalize pitch_abs_p95 > 0.35
  penalize base_height_min < 0.145

actuator_penalty:
  penalize sent_target_velocity_p95 > 2.5 rad/s
  penalize joint_tracking_p95 > 0.12 rad

diversity_gate:
  require at least two source seeds with curated windows
```

The generator should rank by:

```text
min_seed_score = min(score(seed_i))
```

not by aggregate mean velocity.

## Candidate Space

Keep the current useful family as the center:

```text
period_s: 0.50-0.70
hip_roll_bias: -0.01 to +0.01
hip_pitch_bias: 0.04-0.08
hip_pitch_amp: 0.03-0.05
knee_bias: 0.03-0.06
knee_amp: 0.08-0.12
ankle_bias: 0.04-0.08
ankle_amp scale: -0.3 to +0.3 of hip amplitude
phase_offset: 0.0-0.7854
```

Then add targeted corrections:

```text
reduce lateral velocity:
  smaller hip_roll_bias
  symmetric left/right roll bias around zero
  phase offsets that reduce side impulse on seed2

reduce contact dominance:
  slightly larger knee/ankle lift during swing
  cadence/phase offsets that create at least one safe contact transition
  reject windows that remain double-support dominated
```

## Required Gate

Do not build a supervised/imitation dataset until:

```text
50-sample curated windows >= 8
curated source files >= 2
at least one primitive/mode has curated windows on seed_000 and seed_002
seed2 vy_abs_p95 <= 0.12
seed2 contact_dominance_pct <= 95
```

## Non-Goals

```text
do not run robot tests
do not deploy
do not train PPO
do not train BC from single-seed curated windows
do not relax the curation gates to make seed2 pass
do not treat short 25-sample snippets as sufficient temporal coverage
```

## Next Tooling Step

Add an objective-driven primitive search or scorer that computes the terms above
for every candidate and reports:

```text
best worst-seed candidates
seed0 metrics
seed2 metrics
failure term by seed
whether any mode passes both seeds
```

Only after that should the project rebuild a longer-window target manifest.

## Implemented Scorer

The first scorer implementation is:

```text
tools/score_target_candidates_objective.py
```

Current result on the latest seed2-balance traces:

```text
status: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
best near-pass:
  primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927
  seed0: pass, vx=0.0565 m/s
  seed2: vx=0.0515 m/s, vy95=0.0507 m/s, contact_dominance=98%
  remaining failure: single_contact_pattern_dominates
```

The next generator change should focus on contact alternation for this family:
one additional safe contact transition is likely enough to move seed2 from
`98%` dominance to the `<=95%` gate, provided forward and lateral metrics are
preserved.
