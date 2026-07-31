# Ground-Up Recurrent PPO CPU Contract

Status: `PASS_PLUMBING_ONLY`

This evidence clears the recurrent family for controlled search jobs. It does
not establish gait emergence, policy quality, or robot readiness.

## Implementation

- Patch: `patches/ground_up_recurrent_ppo.patch`
- Patch SHA-256: `7d65884265808254f84011ecda99570913f8e568a565240abe1c4d23881d398f`
- Actor observation: 101 canonical features
- Recurrent state: 64 float values
- ONNX inputs: `obs[1,101]`, `h_in[1,64]`
- ONNX outputs: `continuous_actions[1,14]`, `h_out[1,64]`
- Collector behavior: carries `h_out` into the next policy call and zeros it
  independently for terminated environments.

The PPO update uses hidden states recorded by the actual rollout collector.
This is stateful, truncated recurrence; it is not full sequence
backpropagation through time and must not be described as such.

## CPU smoke

- Platform controls: `CUDA_VISIBLE_DEVICES=''`, `JAX_PLATFORMS=cpu`
- Seed: 105
- Environments: 4
- Timesteps completed: 1024
- Final checkpoint: `outputs/ground_up_recurrent_cpu_smoke/2026_07_13_202727_1024`
- Final ONNX SHA-256: `0c28942be29d65a459559b9994d9db84e5b21b2d15feb36c3a4f6ac8cf6a393b`
- Eight-step trained JAX/ONNX maximum action error: `1.1920928955078125e-07`
- Eight-step trained JAX/ONNX maximum hidden-state error: `0.0`
- Synthetic two-environment collector check: nonterminal hidden value advanced
  from 2 to 3; terminated hidden value reset from 4 to 0; transition next
  observation matched the state passed to the following actor call.

The step-1024 reward is not used for selection or gait claims.

## Evaluator contract

`tools/evaluate_ground_up_policy.py` now passes named recurrent state pairs to
the existing stateful closed-loop evaluator. A 0.1-second CPU contract run
with `h_in -> h_out` completed and recorded `policy_io.stateful=true` in:

`outputs/analysis/ground_up_recurrent_evaluator_contract.json`

Its result is correctly `HOLD_GAIT_NOT_EMERGED`: the run is shorter than the
frozen 1.08-second gait-classification window and contains only x=0. This is a
wire-format test, not behavior evidence.

## Patch-order validation

The recurrent patch applied cleanly after the preregistered search,
reference-conditioned, recipe-control, and phase-MoE patches. No robot or RDK
access and no local accelerator were used.
