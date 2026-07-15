# Ground-Up Reset-Estimator Post-Install JAX Import Correction Contract — 2026-07-15

## Result

`PASS_POSTINSTALL_JAX_IMPORT_CORRECTION_CONTRACT`

The only wrapper change moves `import jax` from the outer `run` scope into the
expansion callback. A simulated module proves `module.main()` is entered with
JAX not imported; the callback remains fail-closed on the CPU fixture. Every
prior epsilon-aware pass/fail fixture still passes unchanged, including exact
raw-report preservation and the float32-epsilon boundary.

The rebuilt wall-only launcher also passes its zero-session contract with the
new wrapper and contract hashes, the same 24 assets, a fresh session name
`open-duck-reset-estimator-epsilon2-t4`, the unchanged 2,400-second wall and
120-second stop reserve, atomic recovery, `UNMEASURED` compute recording, and
mandatory cleanup.

## Authority

The continuing user authorization permits the one fresh single-use T4 launch
without billing inputs or another approval prompt. It is not a retry or resume
of the consumed session. No local GPU/iGPU, RDK-X5, runtime, or robot action is
authorized; recovered policies remain behavior-unevaluated.

