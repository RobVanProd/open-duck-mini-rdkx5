# Ground-Up Reference-Conditioned CPU Contract Check

status: `PASS_CPU_ONLY_NOT_A_POLICY_CANDIDATE`

## Scope

This check verifies that the reference-conditioned family can be constructed,
stepped, trained, checkpointed, and exported without using a local GPU or the
robot. It does not evaluate learned behavior and does not clear anything for
hardware use.

## Frozen inputs

- Playground commit: `b9be205ac64488c23504ca42e5ec790337adeec3`
- prerequisite patch: `patches/ground_up_search_runner.patch`
- family patch: `patches/ground_up_reference_conditioned.patch`
- projected reference table:
  `outputs/analysis/ground_up_projected_reference_feature_table.npz`
- projected reference table SHA256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- dependency environment: `/home/lsd/robots/envs/ground-up-control`
- execution boundary: `CUDA_VISIBLE_DEVICES=''`, `JAX_PLATFORMS=cpu`

Both patches applied cleanly in order to a detached worktree at the frozen
commit. `py_compile` and `git diff --check` passed.

## Environment contract

JIT reset and one zero-action step produced:

- policy state: `(115,)` = canonical state `(101,)` plus projected reference
  action `(14,)`;
- privileged critic state: `(226,)`;
- action size: `14`;
- state and privileged state finite after reset and step: `true`.

The projected feature is appended inside the observation. The actor still
emits the final 14-action vector; there is no post-policy action composition.
When the command norm is at or below `0.01`, the appended projected reference
feature is zero.

## PPO/export contract

A deliberately tiny CPU smoke run completed with four environments, 1,024
requested timesteps, two evaluations, unroll length four, and one update per
batch. It emitted step-0 and step-1,024 Orbax checkpoints and ONNX models.

Final ONNX:

- file:
  `outputs/ground_up_reference_conditioned_cpu_smoke/2026_07_12_194846_1024.onnx`
- SHA256:
  `832f8b9b8f159cfe7fe0c8fdbc3ee67668d0e8c49d35ccdf8ded2b25820348e1`
- input: `obs`, `[1,115]`
- output: `continuous_actions`, `[1,14]`

The duplicate step-1,024 export has the same SHA256. The exporter log records
zero eligible GPUs.

## Non-blocking host warning

JAX logged repeated CPU AOT feature warnings for
`prefer-no-scatter`/`prefer-no-gather`. Despite those warnings, the strict
pipeline completed and produced valid checkpoints and ONNX files. This is a
host CPU/XLA warning, not evidence of policy quality. Accelerator jobs must use
fresh job-local caches so CPU artifacts are never reused across machines.

## Decision

The reference-conditioned mechanism passes its CPU implementation and export
contract. It may enter the preregistered offline search after the shared recipe
search and remaining family contract checks are frozen. This smoke model is
not a candidate, is not behavior evidence, and is not authorized for RDK
installation or motor tests.
