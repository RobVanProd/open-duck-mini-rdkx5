# Hardware-Vector Bridge Constrained PPO Result

status: `REJECT_CLOSE_PENALTY_PPO`

The preregistered 245,760-step T4 job completed and the Colab session was
stopped after download. Archive SHA256:
`26ec13eee280fdb66d846086bfb450d02e3c56f092ee63a48b9fc4084f66d509`.
No local GPU, robot, deployment, or grounded action was used.

All three scheduled checkpoints complete 15 seconds and eliminate measured
velocity excess, but collapse to double-support standing on the unchanged
fixed-target bridge x=.08 seed-0 screen:

| step | vx m/s | ratio | single support | p95/max excess |
|---:|---:|---:|---:|---:|
| 81,920 | 0.0002 | 0.0021 | 0.0% | 0 / 0 |
| 163,840 | 0.0003 | 0.0036 | 0.0% | 0 / 0 |
| 245,760 | 0.0003 | 0.0040 | 0.0% | 0 / 0 |

Each misses the frozen vx `0.0257`, ratio `0.3213`, and single-support `20%`
floors by large margins. Since the failure is already present at the first
checkpoint and persists, further seeds cannot rescue the objective. Close the
exact calibrated penalty-PPO route without scale, reward, length, or checkpoint
tuning. Preserve rate165 unchanged and do not allocate another Colab job from
this result.

