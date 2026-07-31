# Ground-Up Phase-MoE CPU Contract

status: `PASS_CPU_TRAIN_EXPORT_NOT_A_POLICY_CANDIDATE`

## Architecture

The `phase_moe_final_action` family is implemented by
`patches/ground_up_phase_moe.patch`, applied after the frozen control,
reference-conditioned, and recipe-control patches.

- canonical policy input: `obs[1,101]`;
- raw smooth-router features: command x/y/yaw at indices `6,7,8` and phase
  cosine/sine at indices `99,100`;
- shared Swish trunk: `[512,256,128]`;
- expert heads: four independently learned 28-logit distribution heads;
- routing: one learned four-way softmax, continuously weighted;
- deterministic export: weighted location logits followed by tanh;
- final output: `continuous_actions[1,14]`.

There are no separately trained policies, hard phase switches, post-policy
blends, runtime gates, or action wrappers.

## Clean construction

Patch order from Playground commit
`b9be205ac64488c23504ca42e5ec790337adeec3`:

1. `patches/ground_up_search_runner.patch`
2. `patches/ground_up_reference_conditioned.patch`
3. `patches/ground_up_recipe_search.patch`
4. `patches/ground_up_phase_moe.patch`

The phase patch SHA256 is
`3faabd86aa160fe6399aa9281a0a126be01a0144916d362c0f5d94499ce41873`.
It applies cleanly in this order and the resulting sources pass
`py_compile`.

## PPO CPU smoke

A CPU-only Brax PPO smoke used seed `104`, four environments, 1,024 requested
timesteps, and reduced smoke geometry. It completed step 1,024, wrote step-0
and final Orbax checkpoints, and exported both ONNX policies.

Final artifact:

- ONNX:
  `outputs/ground_up_phase_moe_cpu_smoke/2026_07_13_201947_1024.onnx`
- SHA256:
  `338688798311add82f0007e9dc3e730a69e3d1d631d34e9b3ffcb045b08b5cd0`
- input: `obs[1,101]`
- output: `continuous_actions[1,14]`
- ONNX graph nodes: `33`
- trained JAX-versus-ONNX max action error on deterministic verification
  input: `5.662441253662109e-07`

Training reward is not reported as advancement evidence. The 1,024-step model
is immature and is not a candidate.

## Boundary

Execution forced CPU via `CUDA_VISIBLE_DEVICES=''` and `JAX_PLATFORMS=cpu`.
No Colab units, local iGPU, onboard GPU, RDK, robot, deployment, torque, or
motor activity was used. This contract permits the architecture to enter the
offline family search only.
