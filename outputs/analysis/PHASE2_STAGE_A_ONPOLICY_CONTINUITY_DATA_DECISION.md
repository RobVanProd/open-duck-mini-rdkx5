# Phase 2 Stage A On-Policy Continuity Data Decision

status: `HOLD_ONPOLICY_CONTINUITY_TEACHER_RATE_MANIFOLD`
generated_at: `2026-07-11`

Offline CPU-only analysis. No training, Colab allocation, deployment, SSH,
local GPU, or robot operation was performed.

## Pre-Registered Question

Does the Stage A step-163840 tracking hold come from small, localized
teacher-action deviations on PPO-visited states, and is the frozen teacher safe
enough to constrain those states directly?

Required data gate:

- full-observation corrected-bridge traces for seeds 0-7
- pitch-chain correction dominance in at least 6/8 seeds
- teacher target-rate p95 <= 1.75 rad/s
- teacher target-rate max <= 2.0 rad/s
- teacher correction max <= 0.25 normalized action

## Evidence

Eight one-second `x=0.08` `flat_terrain_backlash` corrected-bridge traces were
collected from Stage A step 163840 using CPU only.

Compact outcomes:

- tracking holds: seeds 0, 1, 2, 5, 7
- low-forward-progress holds: seeds 3, 6
- pass: seed 4
- falls: 0/8

Teacher-correction results:

- pitch-chain-dominant traces: 7/8 — pass
- correction mean/p95/max: 0.0219 / 0.0580 / 0.1563 normalized action — pass
- teacher target-rate p95: 1.5146 rad/s — pass
- teacher target-rate max: 2.6084 rad/s — **fail**

Per-seed teacher maximums above 2.0 rad/s occurred on seeds 1, 2, 3, 4, 5,
and 6. Seeds 3 and 5 reached approximately 2.61 rad/s.

## Decision

Do not run the joint-weighted behavior-prior PPO smoke. The teacher is close to
the student and the correction is localized primarily to the pitch chain, but
the same teacher exceeds the registered instantaneous target-rate maximum on
most student-visited seeds. Increasing the teacher loss would more strongly
copy a target manifold that already violates the causal data gate.

The next evidence task is offline and pre-training: construct a transition-
preserving, temporally rate-bounded teacher target on these exact visited
observations, then verify that it:

1. caps teacher target rate at 2.0 rad/s without large discontinuities;
2. preserves the teacher's full-gate forward-motion baseline;
3. does not repeat the failed right-ankle-only limiter;
4. retains multi-joint pitch-chain coordination across all eight seeds.

Until that target-manifold gate passes, no additional Colab training is
authorized and the default-off joint-weighted prior wiring must remain unused.

## Artifacts

- pre-registration:
  `outputs/analysis/PHASE2_STAGE_A_ONPOLICY_CONTINUITY_RECIPE.md`
- full-eight trace manifest:
  `outputs/analysis/PHASE2_STAGE_A_RATE175_STEP163840_X008_FULL8_FULLOBS_MANIFEST.md`
- correction analysis:
  `outputs/analysis/PHASE2_STAGE_A_RATE175_STEP163840_ONPOLICY_TEACHER_CORRECTIONS.md`
- per-seed gate:
  `outputs/analysis/PHASE2_STAGE_A_RATE175_STEP163840_X008_SEED1_7_FULLOBS.md`
