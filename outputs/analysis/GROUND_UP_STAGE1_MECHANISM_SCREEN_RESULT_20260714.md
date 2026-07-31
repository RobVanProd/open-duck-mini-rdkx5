# Ground-Up Stage-One Mechanism Screen Result

status: `NO_STAGE1_MECHANISM_WINNER`

## Decision

None of the five preregistered mechanisms qualifies for 12M or second-seed
replication. No checkpoint is a policy candidate and no robot, RDK-X5, or
deployment phase is authorized.

Hard failures were ranked first, followed by full checkpoint passes, finite
x=0 runs, moving passes, and persistence. `M4_SYMCRIT` ranks first but does not
advance: it produced zero full checkpoint passes, zero moving passes, zero
persistent moving seeds, and one hard failure. The preregistration explicitly
forbids advancing an architecture merely because it is least bad.

| rank | mechanism | full checkpoints | zero finite | moving passes | persistent seeds | hard failures | decision |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | `M4_SYMCRIT` | 0 | 4 | 0 | 0 | 1 | eliminate |
| 2 | `M0_UPSTREAM` | 0 | 3 | 0 | 0 | 1 | eliminate |
| 3 | `M1_REFCOND` | 0 | 3 | 1 | 0 | 2 | eliminate |
| 4 | `M2_PHASE_MOE` | 0 | 3 | 0 | 0 | 2 | eliminate |
| 5 | `M3_RECURRENT` | 0 | 2 | 0 | 0 | 4 | eliminate |

## Final M4 evidence

At step 6,021,120 both x=0 runs completed, both x=0.08 runs failed emergence,
and seed 101 terminated with `fall_or_nan`. At step 8,028,160 both x=0 runs
completed and both x=0.08 runs again failed emergence. Positive world
displacement for step-8M seed 101 did not count because mean body-local forward
velocity was not positive.

The M4 artifact completed its training-only contract in 1,381.95 seconds and
was downloaded before the hosted session was stopped:

- archive SHA-256: `fd86aa91e4fc48cc910aeefe6f08612361455dc048190d304502296282b772dc`;
- 6M ONNX SHA-256: `15d71caca7a39ed83864f7c73c2928b9458707f9bac6de2306bedcf826b82e28`;
- 8M ONNX SHA-256: `e40d4c4fc3a429eff090c41532762618687a760b527dbb2bf17647b272afed86`.

## Infrastructure record

Two hosted runtimes lost their `/content` filesystem while the Colab control
plane still reported their executions as busy. Every completed candidate
archive had already been downloaded before each loss. The unfinished candidate
was rerun alone with its exact preregistered recipe; no completed evidence was
repeated and no training value was changed. The final Colab session was stopped
and no Colab sessions remained before local evaluation.

## What the result supports

The scalar screen already rejected learning-rate, entropy, imitation-scale,
discount, and unroll searches around the upstream center. This mechanism screen
now rejects the tested upstream MLP, projected-reference-conditioned MLP,
phase mixture of experts, 64-state recurrent actor, and symmetric-critic
variants under the shared stage-one setup.

The next evidence problem is therefore the shared reference/command curriculum
or objective. A new branch must be preregistered from an audit of the reference
motion, command distribution, reset state, imitation target, and gate outcome.
No additional architecture, scalar combination, longer run, second seed, or
robot test follows from this result.

Training reward was excluded throughout. All behavior evaluation ran on local
CPU with `CUDA_VISIBLE_DEVICES=''` and `JAX_PLATFORMS=cpu`. No local GPU, iGPU,
onboard GPU, RDK-X5, robot, motor, torque, or deployment access occurred.
