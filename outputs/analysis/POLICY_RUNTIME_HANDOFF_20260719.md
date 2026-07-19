# Policy Runtime Handoff

Status: `BLOCKED_REQUIRES_REVIEWED_115_RUNTIME_V2`

Disposition: `REQUIRES_REVIEWED_115_RUNTIME_V2`

Robot clearance: `NO`

The policy-side response to native-runtime `Comms.md` is complete and committed
as a hash-bound package at
`artifacts/runtime_handoff/rdkx5_native_20260719/`. The request was read from
runtime branch `agent/measurement-contract-evidence`, request commit
`c18114c`, against reviewed runtime commit
`a6f62b25b5960987e3955bd327ac95ddbf25a336`.

## Disposition

The protected winner is not compatible with the frozen legacy 101-D runtime
contract. Both persistent graphs have mandatory static float32 inputs
`obs [1,115]` and `previous_action [1,14]`, and outputs
`continuous_actions [1,14]` and `previous_action_out [1,14]`.

No single deployment checkpoint is selected. The frozen policy evidence uses
both 512000 and 1024000 as persistence checkpoints and contains no authority to
choose one post hoc. Therefore `SELECTED_ONNX_SHA256` is `NOT_READY`; both exact
candidate binaries and their hashes are included for runtime review.

## Package checks

The deterministic trace generator was rerun cleanly after it was added; all
four cells again reproduced the frozen trace fields at zero error. See
`outputs/analysis/winner_v2_runtime_handoff_trace_generation_20260719.json`.

- Manifest SHA-256: `ba7143f5c653c0bb2f3f27930a7997dd5a2b90e3258bca516b7240bd0f21abd7`
- Package files hashed: 21, plus 13 external source artifacts.
- CPU smoke: `PASS_CPU_HANDOFF_INSPECTION_BLOCKED_FOR_RUNTIME_REVIEW`.
- Both ONNX graphs: exact names, shapes, dtypes, IR 10, opset 12, 40 nodes,
  24 initializers.
- Chained golden action error: 0.
- Chained golden recurrent-state error: 0.
- Incoming-state chain error: 0.
- Nonfinite inputs: rejected before inference.
- x=0: action and recurrent output are bit-exact zero for all 600 ticks at both
  checkpoints.
- Fresh CPU full-observation traces reproduce all four frozen P30 traces with
  zero error in action, sent target, applied target, actual position, and
  `obs[0:6]` over 600/600 rows each.
- P30 host observer equals the P30 simulated applied target at zero error over
  all 2400 packaged rows.
- The inherited 5.24 rad/s host limiter is an exact no-op over all 2400 rows;
  any nonzero change is a v2 contract failure.
- Independent CPU JAX replay from the final ONNX initializers differs from
  ONNX Runtime by at most `8.344650268554688e-7`, below the package's `1e-6`
  tolerance. This is not represented as an Orbax checkpoint-restore test.

The complete 600-tick traces are losslessly archived for both checkpoints at
x=0 and x=.080. Adjacent ticks 0–4 are also provided in text. The binary golden
packs separate raw actor action, hard-vector output, guarded output, final
action/state, target before the inherited limiter, sent target, applied target,
observer value, actual position, phase before/after, and raw/normalized command.

## Resolved semantic differences

Training `obs[83:97]` is the bridge-realized applied target from the preceding
transition, not the preceding commanded target and not current measured joint
position. A legacy commanded-target substitution first changes moving output
at tick 1:

- checkpoint 512000: maximum action difference `0.03518424555659294`;
- checkpoint 1024000: maximum action difference `0.029209673404693604`.

The passing phase order is observe current phase, infer, then advance once for
the next tick. This matches the native runtime's current order. An erroneous
advanced-first phase/reference substitution changes moving output at tick 0:

- checkpoint 512000: maximum action difference `0.10399797558784485`;
- checkpoint 1024000: maximum action difference `0.11153934895992279`.

The policy graph already owns reference-residual composition, normalization,
the stateful measured hard-vector projection, actual-centered pitch guard,
exact x=0 deadband, and conservative left-ankle constant. The P30 delay/tau
forward observer remains host code. The final ONNX output is the authoritative
normalized action. No head overlay, extra filter, second projection, or
non-identity limiter is compatible with the evidence.

## Remaining blockers

1. No single deployment checkpoint has been selected.
2. The reviewed native runtime remains the frozen 101-D v1 implementation; a
   reviewed 115-D v2 implementation has not passed its own contract.
3. The real-build torso COM/inertia input audit still has exactly 46 missing
   fields and reports no numerical estimate. Policy-side robot clearance is
   therefore NO.

Passing this offline handoff can unblock a native-runtime v2 design/review, but
cannot change Gate 5 from `NOT_RUN`, select a robot binary, or clear the robot.

## Relay fields

```text
POLICY_HANDOFF_STATUS: BLOCKED
DISPOSITION: REQUIRES_REVIEWED_115_RUNTIME_V2
POLICY_REPO_COMMIT: <full handoff commit reported after commit>
ARTIFACT_ROOT: artifacts/runtime_handoff/rdkx5_native_20260719
HANDOFF_MANIFEST_SHA256: ba7143f5c653c0bb2f3f27930a7997dd5a2b90e3258bca516b7240bd0f21abd7
SELECTED_ONNX_SHA256: NOT_READY
INPUT_CONTRACT: obs float32[1,115] + previous_action float32[1,14] -> continuous_actions float32[1,14] + previous_action_out float32[1,14]
ROBOT_CLEARANCE_IN_POLICY_REPO: false
UNRESOLVED_BLOCKERS: no single deployment checkpoint selected; reviewed native runtime is 101-D v1, not stateful 115-D v2; real-build torso COM/inertia audit has 46 missing inputs and no numerical estimate
```
