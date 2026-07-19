# Winner-v2 Recursive Cross-CPU Closure Preregistration — 2026-07-19

Status: `PREREGISTERED_BEFORE_FORMAL_RECURSIVE_RERUN`

Robot clearance: `NO`

## Question

Does the selected original 512000-step winner-v2 graph preserve the reviewed
115-D controller semantics when a second CPU closes both recurrent feedback
paths for the full 600-tick package horizon?

The direct replay contract remains `1e-6` normalized units on identical input
tensors. This study does not retroactively reinterpret or widen that boundary.
It adds a separate physical-space closure rule for the different, fully
recursive trajectory produced when normal float32 cross-CPU differences are
fed back through both `previous_action` and the `t-2/t-3/t-4` observation
history.

The values previously summarized by the runtime agent in `Comms.md` motivated
this preregistration but have no formal outcome weight. The formal result must
come from a new invocation after the commit containing this document.

## Frozen identities

- policy repository branch: `codex/torso-com-decode-probe`;
- corrected policy package commit:
  `e63226eb5b60a9a96cca4bfbb20ef231c0cada64`;
- package schema: `winner_v2_rdkx5_native_handoff.v1.1`;
- package manifest SHA-256:
  `d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5`;
- selected original 512000-step ONNX SHA-256:
  `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`;
- audit-only 1024000-step sibling SHA-256:
  `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece`;
- selected x=0 golden pack SHA-256:
  `aa84f0cbd4e885f9dcc36c553c43e17030f32d0304dff2a7bf06f1f41c4cbe2e`;
- selected x=.080 golden pack SHA-256:
  `0cfd9e99bf499028b5b7f285fa1964f65248795592cf9d072c4bc5aa1a56fb1c`;
- P30 fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`;
- packaged observer/assembler source SHA-256:
  `5c90994a24aa223c94f3a51927228e97000f6118c927561a87a3f2684dcf4889`;
- runtime evidence baseline commit:
  `a1f3e527608c43dfefae84f1d283529e7a686b27`;
- runtime STS3215 conversion source SHA-256:
  `a52b5a1551dce7940aadbd1b6446b91a796d279875d77ee247e4ef1cd43b4aa8`;
- runtime constants source SHA-256:
  `80ff38cd4a4436b445754051f1de608797f051f1886b142a29bf4f5f8b2f2ca3`;
- preserved physical-offset snapshot SHA-256:
  `298753fb30c658321161df50f668ad7ab25121a1958c4b7bbdb1c543caf06bff`.

The selected graph remains the one chosen prospectively by the native-input
representation matrix. The 1024000 sibling is reported as a persistence audit
only; it cannot select, replace, or veto the selected graph in this numeric
closure study.

## Frozen replay

Run only ONNX Runtime `CPUExecutionProvider`. For each packaged cell, begin
with the exact reset values and process exactly 600 ticks in order.

At tick `t`:

1. Copy the packaged exogenous sensor, command, contact, phase and projected-
   reference fields for tick `t`.
2. Reconstruct `obs[41:55]`, `obs[55:69]`, and `obs[69:83]` from this replay's
   final actions at `t-2`, `t-3`, and `t-4`.
3. Reconstruct `obs[83:97]` from this replay's P30 observer state.
4. Supply this replay's final action at `t-1` through the separate
   `previous_action` input.
5. Run the unchanged selected ONNX once, use both returned tensors, calculate
   `logical_target = HOME_RAD + final_action * 0.25`, assert the inherited
   5.24 rad/s limiter is an identity, and advance P30 exactly once after the
   confirmed logical target.
6. Add the 14 preserved soft offsets and apply the runtime's unchanged wire
   conversion exactly:

   `raw = int(4096 * (pi + physical_target_rad) / (2*pi))`.

No rounding, quantizer, output projection, action repair, altered provider
option, shortened horizon, reset change, or substituted field is permitted.

The formal selected matrix is exactly two cells: 512000 at command x=0 and
x=.080. The same two 1024000 cells must be reported under the identical method
but are non-gating audit cells.

## Unchanged semantic gates

Every selected cell must satisfy all of the following:

- exactly 600 ordered ticks and 14 joints;
- all package, graph, runtime-source, offset and golden identities exact;
- finite observation, state, action, target and observer values at every tick;
- corrected action history exactly `t-2/t-3/t-4` and separate recurrent input
  exactly `t-1`;
- exogenous fields, phase, command and contact copied exactly from the golden
  pack;
- same-input ONNX action and recurrent-output error `<=1e-6` at every tick;
- teacher-forced assembled observation error exactly zero;
- inherited 5.24 rad/s limiter changes zero targets;
- saturation, measured-rate-excess and conservative-envelope pass/fail flags
  do not change from the golden pack;
- x=0 action, recurrent state, logical target and P30 state are bit-exact to
  the golden pack for all 600 ticks.

## Native-resolution recursive metric

The runtime's deployed STS3215 command has 4096 counts per revolution, so one
position count is exactly:

`STS_LSB_RAD = 2*pi/4096 = 0.0015339807878856412 rad`.

The prospective recursive physical-space boundary is half of that native
command quantum:

`STS_HALF_LSB_RAD = pi/4096 = 0.0007669903939428206 rad`.

This boundary comes only from the frozen bus conversion and actuator
representation. The rule also checks the actual integer command rather than
claiming that a sub-LSB float difference is necessarily byte-identical near a
truncation boundary.

For each selected cell require:

- maximum absolute recursive logical-target difference
  `<=STS_HALF_LSB_RAD`;
- maximum absolute recursive P30 observer-state difference
  `<=STS_HALF_LSB_RAD`;
- maximum absolute raw STS3215 goal-position difference `<=1` count;
- no raw target outside the unchanged signed multi-turn range;
- unchanged limiter/saturation/rate/envelope classifications.

Record, but do not use for selection, the normalized action/state maximum,
per-joint maxima, raw one-count mismatch count, first mismatch tick/joint,
and maximum error in units of STS counts. A result with a one-count difference
is `native-resolution equivalent`, not byte-identical.

## Frozen decisions

- `PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE` if every selected semantic and
  native-resolution gate passes and all selected raw goal words are exact.
- `PASS_RECURSIVE_NATIVE_RESOLUTION_CLOSURE` if every selected gate passes,
  at least one selected raw word differs, and every raw difference is at most
  one count.
- `HOLD_RECURSIVE_NUMERIC_CLOSURE` if the study is valid but either selected
  cell fails any gate.
- `INVALID_RECURSIVE_CROSS_CPU_STUDY` for any provenance, method, schema,
  matrix, tick-count, provider or completeness failure.

Either PASS token closes only the reviewed CPU recursive-numeric blocker for
the selected 115-D runtime-v2 path. It does not establish real-time timing,
sensor freshness, real-build COM compatibility, X5/AArch64 equivalence, Gate
5, deployment, or robot clearance. A later X5 CPU-only preflight must apply the
same frozen metric before any motor-capable gate. A HOLD may localize the
failure but may not promote the 1024000 sibling or tune a tolerance.

## Required committed result

The runtime repository must commit a deterministic verifier and a reduced JSON
result containing, for every cell, provenance, platform/provider, 600-tick
completeness, all semantic gates, all recursive maxima, raw mismatch counts,
first mismatch location and decision inputs. The verifier must be rerunnable
against the corrected package and must calculate raw words from the frozen
offsets and exact `rad_to_raw_position` source. The policy repository will
independently rerun that verifier and record the final decision.

No robot, RDK-X5, motor, torque, deployment, hosted allocation, training,
local GPU or iGPU action is authorized.
