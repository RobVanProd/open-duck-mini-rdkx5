# Full-8 Router Source Recurrent H128 S64 Rate2p0 Decision

status: `HOLD_FULL8_RECURRENT_BC_REVERSES_AND_SATURATES`

The full-8 selected source was fit with a stateful recurrent BC student to test
whether explicit hidden state preserves the branch behavior that the static
rich-context parent lost. It did not. The recurrent student failed all screened
seeds quickly, reversed, and drove pitch-chain targets to the simulator slew
ceiling.

This is offline diagnostic evidence. It did not train PPO/DR, deploy, SSH, run
robot tests, grounded replay, or change runtime behavior.

## Inputs

- source_manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- train_report: `outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0.json`
- candidate_onnx: `outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0/candidate.onnx`
- candidate_onnx_sha256: `6fe1713ab1de5c4480a964b4a2e9b3d119f9b905f235c97806a8298e6b8a6b56`
- candidate_npz_sha256: `9e88a21272d6621522eec6ed93595a7411cc24cbc13a88ce234c1bff50721765`
- gate: `outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0_x008_seed0_5_7_gate.json`

## Fit

- fit_status: `PASS_RECURRENT_BC_FIT_SMOKE`
- samples: `6000`
- hidden_dim: `128`
- sequence_length: `64`
- MAE: `0.009001`
- p95_abs_error: `0.022976`
- target_rate_p95_rad_s: `1.4556`
- target_rate_max_rad_s: `2.3151`
- ONNX max_action_error: `0.00000056`
- ONNX max_hidden_error: `0.00000124`

## Gate Result

- seeds: `[0, 5, 7]`
- pass_count: `0/3`
- falls: `3`
- samples: `63` for every seed
- mean_vx_m_s: `-0.2468`
- mean_track_ratio: `-3.0849`
- max_p95_velocity_excess_rad_s: `3.2400`
- max_instant_velocity_excess_rad_s: `3.2400`

| seed | status | samples | termination | vx | track_ratio | pitch_p95 | base_min | p95_excess | max_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2476 | -3.0944 | 0.0417 | 0.0761 | 3.2400 | 3.2400 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2461 | -3.0761 | 0.0417 | 0.0780 | 3.2400 | 3.2400 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2467 | -3.0841 | 0.0417 | 0.0767 | 3.2400 | 3.2400 |

## Decision

Do not promote this recurrent student and do not launch Phase 2 domain
randomization from it. Plain recurrent BC on the selected full-8 source is not
the missing branch-preservation mechanism; it regresses harder than the static
rich-context parent and leaves the corrected envelope.

## Next Recommendation

Move to an explicit branch-preserving wrapper/router or trainable
mixture-of-experts objective with closed-loop validation pressure. Do not spend
another run on supervised-only recurrent compression of this source.
