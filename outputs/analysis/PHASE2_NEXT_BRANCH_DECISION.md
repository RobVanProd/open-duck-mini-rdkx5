# Phase 2 Next Branch Decision

status: `PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY`

## Summary

The corrected rate165 candidate remains the current offline baseline, but the
Phase 2 PPO/DR path is currently blocked by standstill regression:

- the full Stage A A100 narrow flat/no-push run collapsed to planted double
  support after `4,587,520` steps.
- the tiny CPU2240 motion-preservation smoke also collapsed to planted double
  support at `x=0.08`.

Both failures were in-envelope and stable. That is the problem: scalar PPO/DR
is preserving safety by deleting the single-support walking behavior.

## Current Baseline

Candidate:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx
```

Hash:

```text
e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
```

Corrected gate evidence:

```text
outputs/analysis/PHASE2_CORRECTED_LIVE_ORACLE_ITER1_RATE165_CANDIDATE_DECISION_20260703.md
outputs/analysis/PHASE2_CURRENT_STATUS.md
```

Baseline gate:

- `x=0.08`, `z=0.0026`, corrected bridge: `8/8` pass, track ratio `0.3400`,
  single support `22.53%`, max tracking p95 `0.1827 rad`, zero corrected
  velocity excess.
- `x=0.0`, `z=0.0026`, corrected bridge: `8/8` pass, near-zero vx, zero
  corrected velocity excess.

## Rejected Paths

Do not repeat or scale these without a new pre-registered reason:

- Stage A scalar PPO/DR from the rate165 PPO-loc checkpoint.
- The CPU2240 motion-preservation PPO recipe.
- Any longer A100 run that uses the same scalar objective and only changes
  duration, environment count, or minor reward weights.

These recipes have already shown the same failure surface: stable,
in-envelope, double-support standstill.

## Required Next Branch

Next offline work must make single support an explicit invariant before domain
randomization resumes.

Preferred branch:

```text
PHASE_AWARE_LIVE_ORACLE_SINGLE_SUPPORT_PRESERVATION
```

Dry-run command plan:

```text
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_iteration.json
```

Required properties:

- warm-start from the corrected rate165 candidate or its rate165 PPO-loc
  checkpoint.
- keep the corrected bridge and per-joint corrected velocity limits
  authoritative.
- collect or relabel on-policy states under the canonical corrected evaluator.
- include phase/contact conditioning or short history sufficient to preserve
  stance transitions.
- gate early on `x=0.08`, `z=0.0026`, `home-support` with:
  - nonzero forward progress,
  - nonzero single support,
  - zero corrected velocity excess,
  - max tracking p95 at or below the current baseline range.
- preserve `x=0.0` stillness.

## Iter2 Result

The live-oracle iteration-2 plan has now been run.

Artifacts:

```text
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json
outputs/analysis/PHASE2_RATE165_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_DECISION.md
```

Result:

- data status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY`
- aggregate samples: `28500`
- student fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- x=0.08 gate: `HOLD_CANDIDATE_TARGET_VELOCITY`
- x=0.08 mean vx: `0.0324 m/s`
- x=0.08 track ratio: `0.4047`
- x=0.08 single support: `27.2000%`
- x=0.08 corrected p95 velocity excess: `0.0000`
- x=0.08 corrected max velocity excess: `0.0149`
- x=0.0 spot gate: `PASS_CANDIDATE_SIM_GATE`

Interpretation:

- Iter2 moved in the right behavioral direction: more forward progress and
  more single support than the current rate165 baseline.
- It is still rejected because the strict corrected gate allows no corrected
  max velocity excess.
- The next attempt should refit from the iter2 aggregate manifest with tighter
  max-rate control or an explicit max-velocity guard. Do not resume scalar
  PPO/domain randomization yet.

## Rate160 Follow-Up

The first follow-up tested a lower scalar supervised target-rate limit:

```text
outputs/analysis/PHASE2_RATE160_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_DECISION.md
```

Result:

- fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- x=0.08 seed-0 screen: `HOLD_CANDIDATE_TARGET_VELOCITY`
- mean vx: `0.0323 m/s`
- track ratio: `0.4031`
- single support: `26.2667%`
- p95 velocity excess: `0.0000`
- max velocity excess: `0.2730`

Interpretation:

- Lowering the scalar target-rate setting from `1.65` to `1.60 rad/s` is not
  the fix.
- The next attempt should implement or use an explicit instantaneous
  max-velocity/spike guard; do not keep lowering the scalar rate knob as the
  primary strategy.

## Limit198 Promotion

The explicit right-ankle max-spike guard was implemented as a surgical
right-ankle label clamp at `1.98 rad/s`.

Decision artifact:

```text
outputs/analysis/PHASE2_ITER2_RIGHT_ANKLE_LIMIT198_RATE165_CANDIDATE_DECISION.md
```

Promoted candidate:

```text
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx
```

Result:

- x=0.08 gate: `PASS_CANDIDATE_SIM_GATE`
- x=0.08 pass seeds: `8/8`
- x=0.08 mean vx: `0.0262 m/s`
- x=0.08 track ratio: `0.3269`
- x=0.08 single support: `25.2000%`
- x=0.08 corrected max velocity excess: `0.0000`
- x=0.0 gate: `PASS_CANDIDATE_SIM_GATE`
- x=0.0 pass seeds: `8/8`
- x=0.0 mean vx: `0.0001 m/s`
- x=0.0 corrected max velocity excess: `0.0000`

This becomes the current offline corrected-bridge Phase 2 baseline. The next
branch can resume domain-randomization robustness from this candidate, but must
preserve zero corrected velocity excess and x=0.0 stillness.

Only after this branch preserves single-support walking should Phase 2 resume
domain randomization:

1. flat/no-push weak randomization,
2. full flat physics randomization,
3. gentle pushes,
4. terrain widening.

## Stop Conditions

- If a candidate is stable but single support returns to `0%`, reject it even
  if fall count is zero.
- If a candidate preserves single support but exceeds the corrected per-joint
  velocity envelope, reject it.
- If `x=0.0` drifts or walks, reject it.
- If a recipe only improves fall count by lowering target velocity and deleting
  forward progress, reject it.

## Scope

Offline only. This decision does not authorize robot tests, SSH, deployment,
grounded replay, or runtime behavior changes.
