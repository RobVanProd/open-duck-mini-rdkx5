# Phase 2 Terrain Swing-Excursion Metrics

status: `PASS_SWING_EXCURSION_METRICS_ADDED`

## Scope

Offline evaluator/tooling only. No robot, SSH, deploy, grounded replay, runtime
behavior change, training run, or policy overwrite was performed.

## Why

C7/C8 showed that scalar terrain rewards can reduce tracking error while the
gait retreats into double support. A C7 pass/fail trace comparison also showed
that the low-progress seed never swung the left foot. Before adding another
training objective, the evaluator needs to report this failure directly.

## Added Metrics

`tools/closed_loop_sim_eval.py` now summarizes per-foot swing segments from
existing rollout records:

```text
swing_segment_count
swing_segment_rel_x_delta_m
swing_segment_rel_x_range_m
swing_segment_peak_lift_over_stance_m
```

The relative-x metrics use foot site x relative to base x. They are passive
analysis metrics only.

`tools/run_candidate_seed_sweep.py` now includes compact gate columns:

```text
min_swing_segments
min_rel_x_range_p95
```

If a foot never swings, its relative-x range is treated as `0.0` rather than
being omitted from the minimum.

## C7 Pass/Fail Recheck

Artifact:

```text
outputs/analysis/PHASE2_STAGE_C7_35120_TRACE_PASS_FAIL_V3_CPU.md
outputs/analysis/phase2_stage_c7_35120_trace_pass_fail_v3_cpu.json
```

Focused comparison:

| seed | status | track ratio | min swing peak | min swing segments | min rel-x range p95 | single support | double support |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.3577 | 0.0096 m | 3 | 0.0059 m | 18.8% | 81.2% |
| 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1918 | 0.0015 m | 0 | 0.0000 m | 4.0% | 96.0% |

## Interpretation

The terrain blocker is now directly measurable in the standard seed-sweep
report:

```text
low-progress terrain seed = no swing segments on at least one foot
                           + no relative-foot excursion
                           + near-total double support
```

This is a better target than tracking p95 alone. It also explains why C8 failed:
penalizing swing imbalance without first preserving motion made the policy
reduce motion further.

## Next

Do not launch another C-stage PPO run that only changes scalar weights.

The next offline branch should first create a target source or hard gate around:

```text
min_swing_segments > 0 on both feet
min_rel_x_range_p95 above a small threshold
min_swing_peak_lift above a small threshold
track ratio preserved
corrected actuator envelope preserved
```

Then use gate-selected checkpointing to test whether those metrics improve.
