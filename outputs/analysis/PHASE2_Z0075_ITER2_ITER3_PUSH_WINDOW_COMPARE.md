# Phase 2 z=0.0075 Iter2 vs Iter3 Push-Window Compare

status: `PASS_ITER2_ITER3_PUSH_WINDOW_COMPARE_READY`

offline trace comparison only; no robot, SSH, deploy, runtime behavior changes, or training.

## Summary Table

| case | samples | vx | track | pitch_p95 | pitch_max | height_min | pushes | push_success | last_push | last_recovered | final_vx | final_pitch | final_height |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| `iter2_seed0_fail` | 689 | 0.0582 | 0.7277 | 0.2831 | 1.4000 | 0.0182 | 11 | 0.9091 | 670 | `False` | 1.4478 | 1.3897 | 0.0182 |
| `iter2_seed7_pass` | 750 | 0.0300 | 0.3747 | 0.1976 | 0.2518 | 0.1568 | 10 | 0.9000 | 719 | `False` | 0.0920 | 0.0292 | 0.1707 |
| `iter3_seed0_fail` | 647 | 0.0569 | 0.7116 | 0.2329 | 1.3379 | -0.0059 | 10 | 0.9000 | 609 | `False` | 1.4890 | 1.2866 | -0.0059 |
| `iter3_seed7_fail` | 633 | 0.0527 | 0.6591 | 0.2853 | 1.4026 | 0.0024 | 8 | 0.8750 | 575 | `False` | 1.5269 | 1.3423 | 0.0024 |

## Last Push Window

| case | last push vector | magnitude | window ticks | window vx max | window pitch max | window height min |
|---|---|---:|---|---:|---:|---:|
| `iter2_seed0_fail` | `[-0.09415885806083679, -0.061026353389024734]` | 0.1122 | `[650, 688]` | 1.4478 | 1.4000 | 0.0182 |
| `iter2_seed7_pass` | `[0.09944447875022888, -0.05289216339588165]` | 0.1126 | `[699, 749]` | 0.1463 | 0.1421 | 0.1629 |
| `iter3_seed0_fail` | `[0.08693043142557144, -0.05110517144203186]` | 0.1008 | `[589, 646]` | 1.4890 | 1.3379 | -0.0059 |
| `iter3_seed7_fail` | `[-0.05506786331534386, -0.09131201356649399]` | 0.1066 | `[555, 615]` | 0.3312 | 0.4668 | 0.1584 |

## Interpretation

- Iter2 seed 7 is the control: it completed 750 samples with track ratio `0.3747`, pitch p95 `0.1976`, base height min `0.1568`, and push success `0.9000`.
- Iter3 seed 7 regressed to a fall at 633 samples while track ratio rose to `0.6591`; p95/max corrected-envelope excess stayed `0.0000`.
- Iter3 seed 0 also fell earlier than iter2 seed 0: 647 samples vs 689 samples.
- The failure mode is therefore not broad actuator-envelope excess. It is push-window pitch/base-height recovery margin lost after the seed-0 window weighting made the policy more aggressive.

## Next Branch

Stop the one-seed push-window weighting path. The next recovery loop must preserve the iter2 seed-7 pass as an explicit control while targeting seed-0 recovery, or it must change the objective to penalize push-window pitch/base-height collapse without increasing forward lunge aggression.
