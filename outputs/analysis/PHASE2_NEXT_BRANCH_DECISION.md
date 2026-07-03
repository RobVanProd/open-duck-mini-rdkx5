# Phase 2 Next Branch Decision

status: `PLAN_PHASE_AWARE_LIVE_ORACLE_SINGLE_SUPPORT_PRESERVATION`

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
