# Ground-Up Reset-Estimator Post-Install JAX Import Correction Preregistration — 2026-07-15

## Scope

Correct only the proven wrapper import-order defect from the consumed
epsilon-aware launch. No policy, checkpoint, expansion threshold, package,
training, or behavior variable may change.

## Frozen correction and contract

1. Remove `import jax` from the outer `run` function before `module.main()`.
2. Import JAX locally inside `epsilon_aware_expand`, immediately before reading
   `jax.devices()` and only after the original job has completed its pinned
   package installs and invoked the expansion callback.
3. Preserve every other wrapper line and all epsilon-aware validation/reporting
   behavior exactly.
4. Extend the CPU contract with an import-order assertion and a simulated module
   proving no JAX import occurs before `module.main()` enters its expansion
   callback. Repeat every prior pass/fail fixture unchanged.
5. Rebuild and zero-session-contract the wall-only launcher with the corrected
   wrapper hash. Preserve the same 24 assets, session topology, 2,400-second wall,
   120-second stop reserve, `UNMEASURED` compute recording, recovery, and cleanup.

If both contracts pass, the user's continuing authorization permits one new
fresh named T4 launch without another numbers or approval prompt. It is not a
retry/resume of the consumed session: use a new session name and empty remote
state. Any failure again stops without retry.

No local GPU/iGPU, RDK-X5, runtime, robot, deployment, torque, or motor access is
authorized. A recovered artifact remains behavior-unevaluated and may advance
only to the already-frozen local CPU evaluation gate.

