# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- samples: `67219`
- weighted samples: `199278.6562`
- pairs: `67100`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.007050`
- p95 abs error: `0.025748`
- max abs error: `0.577244`
- target-rate p95: `1.375196` rad/s
- target-rate max: `3.861276` rad/s
- sample weight p50/p95/max: `3.0000` / `5.0000` / `8.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.149838 |
| 500 | 0.000450 |
| 1000 | 0.000653 |
| 1500 | 0.000419 |
| 2000 | 0.000381 |
| 2500 | 0.000549 |
| 3000 | 0.000666 |
| 3500 | 0.000366 |
| 4000 | 0.005847 |
| 4500 | 0.002066 |
| 5000 | 0.000627 |
| 5500 | 0.000308 |
| 6000 | 0.000270 |
| 6500 | 0.000362 |
| 7000 | 0.000586 |
| 7500 | 0.000722 |
| 8000 | 0.000396 |
| 8500 | 0.000345 |
| 9000 | 0.000208 |
| 9500 | 0.000258 |
| 10000 | 0.000356 |
| 10500 | 0.000273 |
| 11000 | 0.000300 |
| 11500 | 0.000200 |
| 12000 | 0.000180 |
| 12500 | 0.000203 |
| 13000 | 0.000238 |
| 13500 | 0.000459 |
| 14000 | 0.000257 |
| 14500 | 0.000201 |
| 15000 | 0.000264 |
| 15500 | 0.000278 |
| 16000 | 0.000225 |
| 16500 | 0.000329 |
| 17000 | 0.000301 |
| 17500 | 0.000279 |
| 18000 | 0.000212 |
| 18500 | 0.000292 |
| 19000 | 0.000210 |
| 19500 | 0.000208 |
| 20000 | 0.000210 |
| 20500 | 0.000256 |
| 21000 | 0.000210 |
| 21500 | 0.000198 |
| 22000 | 0.000184 |
| 22500 | 0.000351 |
| 23000 | 0.000297 |
| 23500 | 0.000207 |
| 24000 | 0.000242 |
| 24500 | 0.000162 |
| 25000 | 0.000189 |
| 25500 | 0.000247 |
| 26000 | 0.000298 |
| 26500 | 0.000169 |
| 27000 | 0.000205 |
| 27500 | 0.000196 |
| 28000 | 0.000311 |
| 28500 | 0.000142 |
| 29000 | 0.000129 |
| 29500 | 0.000199 |
| 30000 | 0.000189 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000031`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
