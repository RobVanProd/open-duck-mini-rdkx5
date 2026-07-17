# Winner v2 Runtime Integration Preregistration

Status: `PREREGISTERED_BEFORE_IMPLEMENTATION_OUTCOMES`

## Question

Can a default-off CPU runtime adapter implement the composite winner's exact
115-D observation and stateful ONNX ABI without changing the legacy 101-D
runtime path or selecting an actuator fit for hardware?

## Frozen authority boundary

This is an offline implementation and replay contract only. It authorizes no
robot, RDK-X5, motor, deployment, Gate 5, GPU/iGPU, hosted allocation, training,
hardware actuator-fit selection, policy overwrite, or behavior claim.

The existing legacy path remains the default. Winner-v2 mode must be explicitly
requested and must fail closed unless every required artifact and setting is
supplied and validated. Supporting both measured fits does not choose either
fit for hardware.

## Frozen artifacts

- Policies:
  - `T2_EQUAL_512000.onnx`, SHA-256
    `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`
  - `T2_EQUAL_1024000.onnx`, SHA-256
    `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece`
- Projected reference table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- P30 fit SHA-256:
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`
- P31/34 fit SHA-256:
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`
- Legacy golden vector SHA-256:
  `0ac018d25a8c3ccb7959670830acce510a98bfda5d614a7aa5be4c242ea0d2d6`
- Pre-change legacy runtime script SHA-256:
  `49d41d58f9852962b866b8700816628da3a88c580b0cd30adaceda052bcc1c49`
- Pre-change legacy ONNX runner SHA-256:
  `33fdd29001d398d8538b3c1a0a302c69c3149094a3f6343df6a5a10e254445ce`

## Frozen winner-v2 ABI

1. Start from the canonical legacy observation fields and order.
2. Replace only `obs[83:97]` with the bridge observer's value for the previous
   completed transition.
3. Append the 14-D projected reference at `obs[101:115]`. Select the table row
   by minimum L1 distance to command `[x, y, yaw]`, then the current integer
   phase index modulo 27. For command norm at or below 0.01, append exact zeros.
4. Observe the current phase before advancing it. Advance exactly one integer
   table phase per 0.02-second policy tick. Non-unit phase offsets and optional
   action filtering are outside this v2 contract and must fail closed.
5. ONNX inputs are `obs [1,115]` and `previous_action [1,14]`; outputs are
   `continuous_actions [1,14]` and `previous_action_out [1,14]`. Initialize
   state to exact zeros and feed each state output into the next policy call.
6. Initialize the bridge observer at the frozen home target. After a target is
   sent, advance the observer exactly once with dt=0.02 seconds; expose that
   result in the next observation.
7. Winner-v2 commands are limited to zero or the already-gated forward band
   0.074 through 0.080 m/s, with all other six command components exactly zero.
   External head overlays are forbidden in v2 mode because they were not in the
   frozen training/evaluation contract.

## Implementation boundary

Add isolated runtime components for:

- the exact fitted bridge forward observer;
- projected-reference lookup and 101-to-115 observation composition;
- strict stateful winner ONNX inference; and
- an explicit, default-off winner-v2 mode in the runtime entrypoint.

The implementation must require an explicit fit path and reference-table path,
validate their hashes, validate one of the two policy hashes, validate CPU ONNX
execution, and record the selected checkpoint and fit in telemetry. It must not
embed a default hardware fit.

## Frozen CPU checks

1. **Legacy default-off:** the existing C3 adjacent-tick golden vector still
   passes exactly; default CLI values select the legacy runner; its 101-D
   observation builder remains unchanged.
2. **Reference construction:** across every available frozen 115-D replay row,
   the new lookup reproduces `obs[101:115]` within `1e-7`, including exact zero
   command behavior.
3. **Applied-target timing:** on those rows after tick zero, `obs[83:97]`
   matches the preceding row's applied target within `1e-7`.
4. **Observer equivalence:** the runtime observer and analysis observer match
   each other exactly and reproduce all 9,600 frozen composite bridge targets
   within `1e-12` rad for both fits and both checkpoints.
5. **Stateful ABI:** both protected policies have exactly the frozen IO names,
   shapes and float types. On deterministic 115-D input sequences, the runtime
   runner's actions and state match direct CPU ONNX Runtime calls exactly.
6. **Fail-closed negatives:** wrong policy/table/fit hashes, absent fit/table,
   nonzero lateral/yaw/head commands, out-of-band forward commands, non-unit
   phase advance, action filtering, wrong observation shape, and nonfinite
   values are rejected before an action can be produced.
7. **CPU boundary:** tests run with GPU visibility disabled and ONNX Runtime
   reports only `CPUExecutionProvider` for formal sessions.

## Pass rule and artifacts

Pass only if every check above passes with no exception waiver. Write:

- `winner_v2_runtime_contract.json`
- `WINNER_V2_RUNTIME_CONTRACT_20260717.md`
- `winner_v2_runtime_contract_cells.json`

Decision token on pass:
`PASS_WINNER_V2_RUNTIME_OFFLINE_CONTRACT_HOLD_HARDWARE_FIT_SELECTION`.

On any failure, decision token:
`HOLD_WINNER_V2_RUNTIME_INTEGRATION`.

No closest result is promoted and no tolerance or interface changes are
allowed after formal outcomes are read.
