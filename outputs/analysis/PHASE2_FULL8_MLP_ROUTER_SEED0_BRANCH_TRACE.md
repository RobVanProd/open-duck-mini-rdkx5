# MLP Router Branch Trace

status: `HOLD_ROUTER_STARTUP_BRANCH_B_ON_FAILED_TRACE`

Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- trace: `outputs/analysis/phase2_full8_mlp_router_candidate_seed0_trace/full8_mlp_router/seed_000/trace.jsonl`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate/gate_mlp.npz`
- samples: `321`
- termination: `fall_or_nan`

## Branch Selection

| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |
|---|---:|---:|---:|---:|---:|
| all | 321 | 47.35202492211838 | -21.44446952662981 | -2.350044005201868 | 13.086851741746063 |
| first_ticks | 80 | 100.0 | 4.622459848143316 | 9.242988783627835 | 16.40700134774936 |
| tail_ticks | 80 | 3.75 | -34.366346547974594 | -13.680693168252876 | -1.0819940921052917 |
| push_ticks | 5 | 40.0 | -19.157465550537445 | -9.742024061247514 | 6.818652970705363 |
| single_support | 60 | 46.666666666666664 | -18.874993444776717 | -5.198091975500395 | 10.906680920103152 |
| double_support | 261 | 47.509578544061306 | -22.834656918332534 | -1.9225962144391406 | 13.258020004250813 |
| reverse_vx | 144 | 31.25 | -31.109623368909126 | -8.08451406716733 | 10.14166865942029 |

## Outcome

- mean_vx_m_s: `-0.0352`
- base_height_min_m: `0.0705`
- body_pitch_abs_p95_rad: `0.4680`

## Decision

The failed trace starts on branch B for most of the startup window, then flips away late. Train the gate with a seed-0 startup cost or prefix validation pressure before composing another router.
