# Runtime Formal Recursive-Closure Handoff

Status: `READY_FOR_POLICY_INDEPENDENT_REVIEW`

This is a documentation-only handoff from the native-runtime workstream. It
does not modify policy code, graphs, packages, thresholds, robot clearance, or
any hardware authority.

The runtime repository has now committed the post-preregistration formal
2,400-tick verifier and both full and reduced results after policy
preregistration commit
`182459eb4d5eb422a6936b7744f5730d22a9bb27`.

```text
RUNTIME_REPOSITORY: RobVanProd/open-duck-mini-rdkx5-native-runtime
RUNTIME_BRANCH: agent/measurement-contract-evidence
FORMAL_RUNTIME_COMMIT: f8def264c856db3905301f5473f5eb1775b3eec0
REDUCED_EXPORT_COMMIT: 9c637ec4a161d20b24b06e91dc309a49c46cf981
CORRECTED_POLICY_PACKAGE_COMMIT: e63226eb5b60a9a96cca4bfbb20ef231c0cada64
FULL_RESULT: artifacts/gates/phase_5_policy/winner_v2_runtime_v2_verification_20260719.json
FULL_RESULT_SHA256: e1842ca64e91056b96c297666803bdeec7c5ff2950d4dfe32e27044379049b14
REDUCED_RESULT: artifacts/gates/phase_5_policy/winner_v2_recursive_cross_cpu_closure_20260719.json
REDUCED_RESULT_SHA256: 4d403623eb4822befde4b633425e344d010140316d7a4c1e48f4354e76285ace
FORMAL_DECISION: PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE
```

Selected 512000 evidence:

```text
DIRECT_SAME_INPUT_MAX: 4.76837158203125e-7 <= 1e-6
RECURSIVE_NORMALIZED_MAX_RECORD_ONLY: 2.384185791015625e-6
LOGICAL_TARGET_MAX_RAD: 5.960464477539062e-7
P30_MAX_RAD: 5.602507320290329e-7
FROZEN_HALF_STS_LSB_RAD: 0.0007669903939428206
RAW_STS_MAX_COUNT_DIFFERENCE: 0
RAW_STS_MISMATCH_WORDS: 0 / 16800
CLASSIFICATIONS_UNCHANGED: true
```

The reduced result is emitted by the same deterministic invocation, binds the
full-result SHA-256, and records each cell's platform/provider, tick count,
semantic gates, same-input and recursive maxima, per-joint target/P30/raw
maxima, raw mismatch count, first mismatch, classifications, role, and exact
decision inputs. Runtime CI passed on both push and pull-request events at
commit `9c637ec`; local validation passed 247 tests and the complete reviewed
artifact manifest check.

Requested policy action:

1. Fetch runtime commit `9c637ec`.
2. Verify both result hashes above and the runtime artifact manifest.
3. Independently run or inspect the committed deterministic verifier against
   corrected package commit `e63226e` under the frozen rule.
4. Reconcile the result with policy Linux corroboration commit `de9dba0`.
5. Record the policy-side reviewed decision and remaining blockers without
   broadening authority.

This result closes only the runtime CPU recursive-numeric blocker if accepted.
The powered-off as-built torso-COM packet is still incomplete, policy
`robot_clearance` remains false, X5/AArch64 no-servo equivalence is not run,
Gate 5 is `NOT_RUN`, and no robot, serial, GPIO, I2C, torque, motor, GPU, or
iGPU action is authorized by this handoff.
