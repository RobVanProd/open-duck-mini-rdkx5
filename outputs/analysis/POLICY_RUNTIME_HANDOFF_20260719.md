# Policy Runtime Handoff

Status: `BLOCKED_FOR_COM_CLEARANCE_AND_X5_CPU_PREFLIGHT`

Disposition: `CPU_RUNTIME_V2_ACCEPTED_BLOCKED_FOR_COM_AND_X5`

Robot clearance: `NO`

## 2026-07-19 action-history correction addendum

The runtime's independent assembler audit found that the original package
metadata was one tick too recent for each embedded action-history slice. The
golden traces and evaluator source are authoritative: `obs[41:55]`,
`obs[55:69]`, and `obs[69:83]` contain final actions `t-2`, `t-3`, and `t-4`,
while the separate recurrent `previous_action[t]` input remains final action
`t-1`. A preregistered metadata/hash-chain correction now verifies both rules
exactly over all 2,400 packaged ticks. It changes no ONNX, golden trace, P30
fit, reference, behavior result, or authority boundary.

The corrected package schema is `winner_v2_rdkx5_native_handoff.v1.1`; its
replacement manifest SHA-256 is
`d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5`.
The selected 512000-step ONNX remains byte-identical at
`99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`.
See `WINNER_V2_ACTION_HISTORY_SEMANTICS_CORRECTION_CONTRACT_20260719.md`.

The fully recursive cross-CPU question has a separate
prospective contract in
`WINNER_V2_RECURSIVE_CROSS_CPU_CLOSURE_PREREGISTRATION_20260719.md`.
It preserves the direct `1e-6` same-input limit and judges recursive drift at
the native STS3215 target representation. Its pre-outcome contract passed, the
formal post-commit runtime result passed on Windows CPU, and policy independently
reproduced the same decision on Linux CPU. Both selected cells have zero raw
STS goal mismatches over 16,800 words. Decision is
`PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE`.

## 2026-07-19 selected-binary addendum

The later prospective native-representation study removes the first blocker
listed in this document. Both checkpoints passed all eight frozen sibling
cells, and the preregistered first criterion selected the original 512000-step
graph. `SELECTED_ONNX_SHA256` is now
`99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`.
See `WINNER_V2_RUNTIME_SELECTED_BINARY_RELAY_20260719.md` for the exact relay.
The reviewed CPU runtime-v2 recursive closure is now accepted. The powered-off
direct-reaction real-build COM measurement, reviewed frozen asset set and X5
CPU-only replay remain incomplete, so robot clearance does not change.

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

The original package includes both 512000 and 1024000 persistence checkpoints
because its source behavior tables contained no authority to choose one post
hoc. The later prospective native-representation screen selected 512000 under
a criterion frozen before its outcomes. Both exact binaries remain in the
package for audit, but only
`T2_EQUAL_512000.onnx` (`99d3afce...304de`) is the selected runtime-v2 review
candidate.

## Package checks

The deterministic trace generator was rerun cleanly after it was added; all
four cells again reproduced the frozen trace fields at zero error. See
`outputs/analysis/winner_v2_runtime_handoff_trace_generation_20260719.json`.

- Manifest SHA-256: `d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5`
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

1. Complete the 15-value powered-off direct-reaction torso-COM packet and pass
   the frozen asymmetric COM interval check. The 46-field component ledger
   remains a fallback, not a concurrent requirement.
2. Freeze and review the exact runtime, selected policy and configuration asset
   set.
3. Run the same native-resolution verifier on the X5 CPU with no servo access.

The CPU runtime-v2 contract and selected binary are resolved offline. They do
not change Gate 5 from `NOT_RUN`, deploy an asset, or clear the robot.

## Relay fields

```text
POLICY_HANDOFF_STATUS: BLOCKED
DISPOSITION: CPU_RUNTIME_V2_ACCEPTED_BLOCKED_FOR_COM_AND_X5
POLICY_REPO_COMMIT: e0badd7aa79ff791212b8d3822f9eefdc4c162e0
ARTIFACT_ROOT: artifacts/runtime_handoff/rdkx5_native_20260719
HANDOFF_MANIFEST_SHA256: d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5
SELECTED_CHECKPOINT_STEP: 512000
SELECTED_ONNX_SHA256: 99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de
INPUT_CONTRACT: obs float32[1,115] + previous_action float32[1,14] -> continuous_actions float32[1,14] + previous_action_out float32[1,14]
ROBOT_CLEARANCE_IN_POLICY_REPO: false
UNRESOLVED_BLOCKERS: powered-off direct COM packet incomplete; reviewed frozen asset set incomplete; X5 CPU-only native-resolution replay not run; Gate 5 NOT_RUN and unauthorized
```
