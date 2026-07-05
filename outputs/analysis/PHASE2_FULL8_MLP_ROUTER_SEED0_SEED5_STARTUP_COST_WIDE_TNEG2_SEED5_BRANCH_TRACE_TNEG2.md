# MLP Router Branch Trace

status: `HOLD_ROUTER_BRANCH_B_DOMINATES_FAILED_TRACE`

Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- trace: `outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_candidate_seed5_trace/full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2/seed_005/trace.jsonl`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz`
- threshold: `-2.0`
- direction: `ge`
- samples: `750`
- termination: `duration_complete`

## Branch Selection

| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |
|---|---:|---:|---:|---:|---:|
| all | 750 | 79.60000000000001 | -9.389074178880085 | 4.183938484195867 | 11.969522498565423 |
| first_ticks | 80 | 56.25 | -3.314586826474498 | -1.7802878506928725 | 1.7656500340522632 |
| tail_ticks | 80 | 78.75 | -5.189048307415527 | 2.999706005396873 | 8.349323190501472 |
| push_ticks | 13 | 69.23076923076923 | -5.14855804754642 | 5.809372804149465 | 11.345609349931442 |
| single_support | 193 | 75.64766839378238 | -11.96840640259599 | 4.007865742590934 | 10.64116079978678 |
| double_support | 557 | 80.96947935368043 | -7.198189840068522 | 4.287143140895925 | 12.186897644593593 |
| reverse_vx | 167 | 75.44910179640718 | -10.490852566329094 | 4.503075115089548 | 11.13134103161626 |

## Outcome

- mean_vx_m_s: `0.0316`
- base_height_min_m: `0.1580`
- body_pitch_abs_p95_rad: `0.1724`

## Decision

The failed trace spends most ticks on branch B. Tighten or cost-train the MLP gate so the seed-5 branch is not selected on this seed-0-like trajectory.
