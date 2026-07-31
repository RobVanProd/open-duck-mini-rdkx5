# Ground-Up Nominal Horizon Persistence Audit

status: `PASS_NOMINAL_HORIZON_AUDIT`
decision: `REJECT_SHORT_HORIZON_NOMINAL_PASS`

Both checkpoints remain finite, upright, and walking for all 600 ticks at
x=.074/.077/.080. Neither clears the frozen 0.20 rad pitch-chain tracking
limit over that same 12-second horizon.

| checkpoint | command | 54-tick p95 | 600-tick p95 | 600-tick mean | >.20 fraction | worst joint | first cumulative failure |
|---|---:|---:|---:|---:|---:|---|---:|
| 1M | 0.074 | 0.188775 | 0.222293 | 0.079311 | 0.0983 | `left_knee` | 108 |
| 1M | 0.077 | 0.185018 | 0.213337 | 0.078372 | 0.0833 | `left_knee` | 162 |
| 1M | 0.080 | 0.176786 | 0.223175 | 0.078796 | 0.1050 | `left_knee` | 108 |
| 2M | 0.074 | 0.216165 | 0.229128 | 0.075169 | 0.1067 | `left_knee` | 54 |
| 2M | 0.077 | 0.216935 | 0.231129 | 0.076859 | 0.1167 | `left_knee` | 54 |
| 2M | 0.080 | 0.208165 | 0.225191 | 0.078758 | 0.1167 | `left_knee` | 54 |

## Full-horizon baseline comparison

| policy | command | mean vx | tracking p95 | rate-limit excess | gate status |
|---|---:|---:|---:|---:|---|
| applied-target 1M | 0.074 | 0.095171 | 0.222293 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| applied-target 1M | 0.077 | 0.108691 | 0.213337 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| applied-target 1M | 0.080 | 0.110690 | 0.223175 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| applied-target 2M | 0.074 | 0.092931 | 0.229128 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| applied-target 2M | 0.077 | 0.095330 | 0.231129 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| applied-target 2M | 0.080 | 0.101580 | 0.225191 | 0.000000 | `HOLD_CANDIDATE_TRACKING` |
| BEST_WALK_ONNX_2 | 0.074 | 0.014428 | 0.212933 | 3.610096 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` |
| BEST_WALK_ONNX_2 | 0.077 | 0.015964 | 0.220919 | 3.749103 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` |
| BEST_WALK_ONNX_2 | 0.080 | 0.017491 | 0.223311 | 3.865267 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` |

The ground-up policies move substantially faster than the baseline and have
zero measured rate-limit excess, but none clears full-horizon tracking. The
baseline comparison therefore does not turn either checkpoint into a winner.

## Evidence-driven correction

The prior 54-tick nominal gate covered only 9% of the 600-tick training
episode. It admitted a transient 1M pass that does not persist in time.
Future nominal advancement must evaluate the full 600-tick horizon before
checkpoint-to-checkpoint persistence, x=0, robustness stages, or robot work.
This is a gate-validity correction supported by existing policies; it does
not select a new training recipe or retroactively approve a checkpoint.

No training, Colab, local GPU, RDK-X5, robot, motor, or torque access was used.
