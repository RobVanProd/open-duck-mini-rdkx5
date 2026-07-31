# Independent Disagreement Validation Result

Date: 2026-07-11

Status: **RANKING REPLICATED; FIXED CUTOFF REJECTED AS SAFETY GATE**

The preregistered seeds 40-71 baseline block ran sequentially on CPU with the
unchanged original rate175 step-163,840 policy, corrected fitted bridge,
x=0.08 command, one-second horizon, and 2.0 rad/s pitch-chain action-rate
limit. No training, intervention, runtime gate, robot access, GPU, or Colab was
used.

## Baseline outcomes

- runs: 32
- falls/terminations: 11/32 (34.38%; Wilson 95% 20.41%-51.69%)
- duration complete: 21/32
- candidate passes: 4/32
- execution errors: 0

Across independent reset seeds 8-71, the same baseline now has 18/64 one-second
falls (28.12%; Wilson 95% 18.59%-40.13%) and only 7/64 passes. The policy is not
robust to the canonical reset distribution.

## Frozen detector results

- first-10-tick p95 teacher-disagreement ROC AUC: 0.823
- failure score mean: 0.09689
- duration-complete score mean: 0.07674
- preregistered fixed cutoff: 0.08247255; it was not refit
- TP/FN/TN/FP: 9/2/16/5
- sensitivity: 0.818 (Wilson 95% 0.523-0.949)
- specificity: 0.762 (Wilson 95% 0.549-0.894)
- balanced accuracy: 0.790

The primary ranking remained above the preregistered rejection boundary of
AUC 0.5, so temporal teacher disagreement remains a useful offline diagnostic.
The fixed cutoff missed seeds 42 and 63 and falsely flagged five completed
runs. It is therefore rejected as a safety gate and must not control simulator
or robot behavior.

## Evidence decision

1. Stop threshold calibration from this teacher disagreement alone. Three
   independent seed blocks show ranking information, but the fixed cutoff does
   not meet a defensible safety standard and its sensitivity interval remains
   wide.
2. Do not add reset-neighborhood features post hoc; that preregistered route
   already reduced transfer performance.
3. Do not use the teacher action as recovery; prior evidence found the action
   corrections outcome-unaligned and outside the safe target rate envelope.
4. The next useful evidence must identify an outcome-aligned active recovery
   target for the recurrent fall trajectories, or revise the policy objective
   under a separately preregistered training experiment. More threshold-only
   seed collection is not the bottleneck.

Primary artifacts:

- `outputs/analysis/phase2_stage_a_disagreement_independent_seed40_71.json`
- `outputs/analysis/PHASE2_STAGE_A_TEACHER_CORRECTION_EARLY_WARNING_INDEPENDENT_SEED40_71.md`
- `outputs/analysis/phase2_stage_a_teacher_correction_early_warning_independent_seed40_71.json`
- `outputs/analysis/PHASE2_STAGE_A_FIXED_DISAGREEMENT_CUTOFF_INDEPENDENT_SEED40_71.md`
- `outputs/analysis/phase2_stage_a_fixed_disagreement_cutoff_independent_seed40_71.json`
