# Live-Oracle DAgger Seed 5 Trace Isolation

status: `HOLD_SEED5_ITER1_REVERSE_COLLAPSE`

Offline trace comparison only. No robot, SSH, deployment, or runtime changes were performed.

## Summary Table

| command | iter | samples | done_idx | vx_mean | vx_first48 | vy_abs_p95 | base_min | pitch_abs_p95 | action_abs_p95 | pitch_sent_vel_p95_max | pitch_tracking_p95_max | contacts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| x008 | iter0 | 750 | NA | 0.0458 | 0.0427 | 0.1440 | 0.1462 | 0.1196 | 0.7883 | 3.6536 | 0.2612 | `{'00': 2, '01': 153, '10': 135, '11': 460}` |
| x008 | iter1 | 74 | 73 | -0.2043 | 0.0032 | 0.1595 | 0.0674 | 1.1972 | 0.8170 | 3.2596 | 0.2666 | `{'00': 4, '01': 8, '10': 5, '11': 57}` |
| x0 | iter0 | 750 | NA | 0.0434 | 0.0227 | 0.1423 | 0.1462 | 0.1779 | 0.7851 | 3.7093 | 0.2678 | `{'00': 2, '01': 150, '10': 120, '11': 478}` |
| x0 | iter1 | 48 | 47 | -0.3358 | -0.3358 | 0.2106 | 0.0421 | 1.3717 | 0.2451 | 1.5031 | 0.2330 | `{'00': 3, '01': 3, '10': 4, '11': 38}` |

## Interpretation

- Iteration 0 seed 5 survives at both x=0.08 and x=0.0, but preserves the old forward-drift/tracking-hold behavior.
- Iteration 1 seed 5 reverses immediately and collapses at both commands.
- The regression is not a high target-rate failure: iteration 1 has lower action/target-rate metrics during the collapse than iteration 0.
- The failure is a command-conditioning discontinuity introduced by the zero-action relabeling path, concentrated on seed 5.

## Next Action

Do not continue by increasing zero-action weight. For iteration 2, blend or schedule the x=0.0 zero-action labels so the zero-command fix is preserved without creating a reverse/fall pocket on seed 5.
