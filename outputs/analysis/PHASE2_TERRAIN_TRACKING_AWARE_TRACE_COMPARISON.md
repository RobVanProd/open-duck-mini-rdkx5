# Phase 2 Terrain Tracking-Aware Trace Comparison

status: `PASS_TRACE_DIAGNOSIS_TRANSITION_DAMPED`

This is an offline trace comparison. It did not run robot tests, SSH, deploy,
grounded replay, or change robot runtime behavior.

## Compared Policies

`iter2_live_oracle_bc`:

```text
outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/rollouts_x008/student/seed_*/trace.jsonl
```

`tracking_aware_bc`:

```text
outputs/analysis/phase2_terrain_tracking_aware_bc_gate/tracking_aware_bc/seed_*/trace.jsonl
```

Both were evaluated on:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted bridge
command_x: 0.08
duration: 5 s
seeds: 2,4
```

## Result

| policy | seed | vx | contact 01 | contact 10 | contact 11 | right_knee vel p95 | right_knee tracking p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| iter2_live_oracle_bc | 2 | 0.0397 | 19.6% | 15.6% | 64.8% | 3.8801 | 0.2399 |
| tracking_aware_bc | 2 | 0.0107 | 5.6% | 4.4% | 90.0% | 2.0631 | 0.1504 |
| iter2_live_oracle_bc | 4 | 0.0459 | 18.8% | 11.6% | 69.6% | 3.6814 | 0.2411 |
| tracking_aware_bc | 4 | 0.0105 | 1.2% | 2.8% | 96.0% | 2.0986 | 0.1558 |

The tracking-aware label filter did reduce the right-knee rate/tracking
problem, but it also removed most single-support time. The result is a
double-support gait that stays calmer because it barely steps.

## Interpretation

The terrain plateau is not solved by global label smoothing. The source of
progress in the iter2 student is the double-support preparation into
single-support transition. The global pitch-chain label filter damped that
transition away.

Next work should be transition-preserving:

- keep the oracle's support-transition timing and swing/advance structure,
- enforce the corrected per-joint envelope in closed-loop training/eval,
- penalize only the excess that appears in closed-loop rollout,
- avoid offline label filters that mostly edit double-support preparation ticks,
- require the hard swing gate before any promotion.

Do not promote `tracking_aware_bc`; it is a diagnostic hold.
