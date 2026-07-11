# Phase 2 Stage A Early-Warning Held-Out Result

Date: 2026-07-11

Status: **RANKING REPLICATED; NO THRESHOLD OR RECOVERY ACTION AUTHORIZED**

This was an unmodified, CPU-only baseline replication. No training, action
intervention, robot access, deployment, GPU, or Colab allocation was performed.

## Held-out baseline seeds 24-39

- runs: 16
- falls/terminations: 2 (12.5%; Wilson 95% interval 3.50%-36.02%)
- duration complete: 14
- passes: 2
- low-forward-progress holds: 9
- tracking holds: 3
- mean velocity: -0.0135 m/s

The discovery and held-out seed blocks together (8-39) produced:

- falls: 7/32 (21.88%; Wilson 95% interval 11.02%-38.75%)
- passes: 3/32

This establishes that the original rate175 policy is not robust to the canonical
randomized reset distribution even at a one-second horizon.

## Frozen held-out metrics

| metric | discovery seeds 8-23 | held-out seeds 24-39 |
|---|---:|---:|
| failures / traces | 5 / 16 | 2 / 16 |
| primary: first-10-tick p95 disagreement ROC AUC | 0.909 | 1.000 |
| primary failure mean | 0.08815 | 0.11041 |
| primary completed mean | 0.07410 | 0.06761 |
| secondary: first-20-tick mean disagreement ROC AUC | 0.891 | 1.000 |
| secondary failure mean | 0.03386 | 0.03967 |
| secondary completed mean | 0.02685 | 0.02506 |

The direction and ranking replicate. The held-out block has only two positive
falls, so the perfect AUC is high-uncertainty evidence and does not justify an
operating threshold.

## Interpretation

The frozen behavior teacher is useful as an offline disagreement detector: its
action mismatch rises before failure. It remains rejected as an action target
because prior corrections were not outcome-aligned and exceeded the safe target
rate envelope on failure traces.

The evidence hierarchy is now:

1. canonical reset robustness is the immediate failure;
2. short temporal disagreement can rank impending falls;
3. a global phase or behavior-prior correction is not a valid recovery action;
4. safe reset/settling contracts should be compared on the exact recurrent
   failure seeds before any more learning work.

No threshold fitting, runtime monitor, reset change, training, or robot-side
action is authorized by this result.

## Subsequent offline threshold-transfer audit

The later saved-JSON-only audit fit the first-10-tick p95 cutoff on each seed
block and tested it on the other. Discovery to held-out transfer was perfect,
but held-out to discovery transfer detected only 1/5 failures (sensitivity
0.20; balanced accuracy 0.555). This asymmetry confirms that the current data
do not support a stable universal start-paused threshold. No runtime gate was
implemented or authorized.

- `outputs/analysis/PHASE2_STAGE_A_EARLY_WARNING_THRESHOLD_TRANSFER.md`
- `outputs/analysis/phase2_stage_a_early_warning_threshold_transfer.json`

Primary artifacts:

- `outputs/analysis/PHASE2_STAGE_A_EARLY_WARNING_HELDOUT_SEED24_39.md`
- `outputs/analysis/PHASE2_STAGE_A_TEACHER_CORRECTION_EARLY_WARNING_HELDOUT_SEED24_39.md`
- `outputs/analysis/phase2_stage_a_early_warning_heldout_seed24_39.json`
- `outputs/analysis/phase2_stage_a_teacher_correction_early_warning_heldout_seed24_39.json`
