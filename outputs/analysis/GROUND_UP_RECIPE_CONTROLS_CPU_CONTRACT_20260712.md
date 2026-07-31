# Ground-Up Recipe Controls CPU Contract

status: `PASS_ARGUMENT_AND_EXPORT_CONTRACT_CPU_ONLY`

## Scope

This check verifies that every variable in the preregistered PPO recipe screen
is an explicit reproducible runner input. It is not a behavior evaluation.

## Patch order

Starting from Playground commit
`b9be205ac64488c23504ca42e5ec790337adeec3`, the following patches applied
cleanly in order:

1. `patches/ground_up_search_runner.patch`
2. `patches/ground_up_reference_conditioned.patch`
3. `patches/ground_up_recipe_search.patch`

The final sources passed `py_compile`. The CLI exposes seed, learning rate,
discount, entropy cost, unroll length, and imitation scale.

## Propagation check

A CPU-only invocation supplied:

- seed `103`;
- learning rate `0.0001`;
- discount `0.99`;
- entropy cost `0.001`;
- unroll length `4` for the reduced smoke geometry;
- imitation scale `0.5`.

The resolved Brax PPO parameter record contained each exact supplied value and
retained clipping epsilon `0.2`. The canonical 101-input policy initialized,
checkpointed at step 0, and exported ONNX successfully. The deliberately tiny
256-step request did not contain a complete PPO training epoch and is therefore
not presented as a training-completion check.

Execution forced `CUDA_VISIBLE_DEVICES=''` and `JAX_PLATFORMS=cpu`. No robot,
RDK, local iGPU, or onboard GPU was accessed.

## Decision

The recipe-control plumbing is suitable for reproducible offline search jobs.
Candidate job generation must still emit a frozen per-run manifest and verify
the resolved parameter record before accelerator training begins.
