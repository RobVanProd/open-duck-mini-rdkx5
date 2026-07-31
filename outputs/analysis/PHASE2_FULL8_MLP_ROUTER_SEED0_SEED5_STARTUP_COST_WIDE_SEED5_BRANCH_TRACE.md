# MLP Router Branch Trace

status: `PASS_ROUTER_BRANCH_B_NOT_DOMINANT`

Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- trace: `outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_candidate_seed5_trace/full8_mlp_router_seed0_seed5_startup_cost_wide/seed_005/trace.jsonl`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz`
- samples: `161`
- termination: `fall_or_nan`

## Branch Selection

| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |
|---|---:|---:|---:|---:|---:|
| all | 161 | 44.099378881987576 | -5.670388682879957 | -0.4188089189183497 | 27.600497813709847 |
| first_ticks | 80 | 21.25 | -3.876220981724429 | -1.2589026768131748 | 1.633681815350721 |
| tail_ticks | 80 | 67.5 | -5.824450191527986 | 3.321044313461399 | 46.08308589385476 |
| push_ticks | 2 | 50.0 | -3.330316334159205 | 1.3722376670431835 | 6.074791668245571 |
| single_support | 17 | 35.294117647058826 | -10.470987592306608 | -2.759944890989045 | 47.66844283521779 |
| double_support | 141 | 43.97163120567376 | -4.142196145435507 | -0.3955881218271089 | 9.753233778752877 |
| reverse_vx | 21 | 9.523809523809524 | -3.657470434051452 | -2.3486399727969243 | 2.3240160428740797 |

## Outcome

- mean_vx_m_s: `0.1296`
- base_height_min_m: `0.0132`
- body_pitch_abs_p95_rad: `0.8511`

## Decision

The failed trace is not dominated by branch B selection; debug the branch-A policy dynamics or mixed transition instead.
