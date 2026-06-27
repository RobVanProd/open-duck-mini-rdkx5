# PPO BC Warm-Start Step-0 Export Fidelity

status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`

This is an offline PPO-param construction and export check. It did not
run PPO updates, SSH, deploy, run robot tests, or change robot runtime
behavior.

## Inputs

- BC NPZ: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz`
- reference ONNX: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate.onnx`
- manifest: `outputs/analysis/ppo_swish_cmd_conditioned_pitch_ratelimit_2p25_manifest.json`

## Outputs

- checkpoint: `outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint`
- exported ONNX: `outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx`

## Mapping

```text
BC w0/b0 -> policy hidden_0
BC w1/b1 -> policy hidden_1
BC w2/b2 -> policy hidden_2
BC w3/b3 -> policy hidden_3 columns 0:14 (loc)
scale logits -> policy hidden_3 columns 14:28
value network -> fresh PPO initialization
```

scale_logit: `-2.0`
initial std after softplus/min_std: `0.127928`

## Fidelity

- samples checked: `2048`
- MAE: `0.00000003`
- p95 abs error: `0.00000009`
- max abs error: `0.00000027`

## Decision

If this passes, the exported PPO step-0 policy reproduces the PPO-loc BC
ONNX at the action level. The next gate is the standard task-matched
fitted closed-loop candidate sweep using this exported PPO ONNX, still
before any PPO training updates.
