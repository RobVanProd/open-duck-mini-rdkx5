# Phase 2 Stage A Phase-Delta Causal Screen Result

Date: 2026-07-11

Status: **HOLD — global phase delta rejected**

This was a matched, offline CPU-only diagnostic. It did not train, allocate
Colab, use a local GPU, access the robot, deploy, or export a policy.

## Contract checks

- x=0 seed-0 correction samples: 50
- maximum absolute phase correction at x=0: 0
- maximum base-policy versus corrected-raw-action delta at x=0: 0
- matched control and intervention both used the same 2.0 rad/s pitch-chain
  policy-action limiter
- both arms completed 8/8 one-second x=0.08 runs with zero falls and zero
  saturation

The matched control exactly reproduced the previously saved full-observation
seed outcomes, so the comparison is paired and deterministic at the evaluator
level.

## Paired forward result

| seed | cohort | control vx | phase-delta vx | delta vx | control ratio | phase-delta ratio | result |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | middle | 0.03460 | 0.03430 | -0.00030 | 0.4326 | 0.4288 | neutral/slight regression |
| 1 | low | 0.02572 | 0.03326 | +0.00755 | 0.3214 | 0.4158 | improved |
| 2 | high | 0.05173 | 0.04993 | -0.00180 | 0.6466 | 0.6242 | regressed |
| 3 | low/reverse | -0.04549 | -0.03045 | +0.01504 | -0.5686 | -0.3806 | improved but still failed |
| 4 | high | 0.05436 | 0.04774 | -0.00662 | 0.6795 | 0.5967 | regressed |
| 5 | high | 0.05828 | 0.05274 | -0.00553 | 0.7285 | 0.6593 | regressed |
| 6 | low | 0.01138 | 0.00125 | -0.01013 | 0.1422 | 0.0157 | sharply regressed |
| 7 | middle | 0.03579 | 0.02373 | -0.01206 | 0.4474 | 0.2966 | sharply regressed |

## Distribution effects

| metric | matched control | phase delta | change |
|---|---:|---:|---:|
| mean vx (m/s) | 0.02830 | 0.02656 | -0.00173 |
| mean tracking ratio | 0.35370 | 0.33204 | -0.02166 |
| mean worst tracking p95 (rad) | 0.21175 | 0.21290 | +0.00115 |
| mean body-pitch p95 (rad) | 0.10277 | 0.08471 | -0.01806 |
| single support | 24.75% | 17.75% | -7.00 pp |
| double support | 74.00% | 81.00% | +7.00 pp |

The intervention improved posture but reduced useful motion and increased double
support. Within the pre-defined low cohort, mean vx improved by 0.00415 m/s only
because seeds 1 and 3 improved; seed 6 moved in the opposite direction. All
three high-cohort seeds regressed (mean change -0.00465 m/s).

## Decision

The pre-registered stop rule was triggered: forward behavior did not improve
consistently across the low cohort. The global phase delta is a real causal
signal for seeds 1 and 3, but it is not a valid general teacher target.

Therefore:

1. close this route;
2. do not tune the phase-delta scale;
3. do not extend duration or train from it;
4. retain the paired traces to distinguish reverse-progress, low-positive, and
   tracking-limited failure modes before considering a state-conditioned target.

Primary artifacts:

- `outputs/analysis/PHASE2_STAGE_A_PHASE_DELTA_MATCHED_CONTROL_X008_1S.md`
- `outputs/analysis/PHASE2_STAGE_A_PHASE_DELTA_INTERVENTION_X008_1S.md`
- `outputs/analysis/phase2_stage_a_phase_delta_matched_control_x008_1s.json`
- `outputs/analysis/phase2_stage_a_phase_delta_intervention_x008_1s.json`
