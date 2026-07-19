# Winner-v2 Runtime Selected-Binary Relay

Status: `READY_FOR_REVIEWED_115_RUNTIME_V2_ACCEPTANCE`

Policy-side robot clearance: `NO`

The prospective native-representation screen selected the original 512000-step
G1/T2 composite graph for runtime-v2 review:

- filename: `artifacts/runtime_handoff/rdkx5_native_20260719/policies/T2_EQUAL_512000.onnx`
- SHA-256: `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`
- policy evidence commit: `e0badd7aa79ff791212b8d3822f9eefdc4c162e0`
- formal result SHA-256: `38b7fc13522844fc3fe7be848f50d68d5cb26064ddb391dbf5e17ff6f31d284f`
- handoff manifest SHA-256: `d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5`

The replacement manifest is the preregistered metadata-only correction of the
action-history labels: the observation carries final actions `t-2/t-3/t-4`,
and the separate recurrent input carries `t-1`. All 2,400 packaged rows pass
both exact checks. The selected ONNX and all golden traces are byte-identical
to the prior manifest chain.

Both persistent checkpoints passed all eight frozen cells. The preregistered
first ranking criterion selected 512000 because its worst pitch tracking p95
was `0.18092596530914307` rad versus `0.181829959154129` rad at 1024000. The
second criterion was therefore not reached. Training and simulator reward had
no selection weight.

The complete formal run contains 16/16 passing cells and 9,600/9,600 audited
trace rows. Every cell completed 600 ticks on CPU with zero saturation, zero
native measured-rate excess, zero conservative-envelope excess, bilateral gait
for moving commands, and the frozen x=0 stand behavior. Finite native register
quantization changed only the BNO055 gyro/acceleration and STS3215
position/velocity slices; all other observation slices were bit-exact.

The selected identity is the original ONNX above. The native-quantized wrapper
was evaluation-only and must not be deployed; the native runtime supplies the
register-quantized inputs.

This relay removes only the prior `SELECTED_ONNX_SHA256=NOT_READY` blocker. It
does not assert that the native runtime has accepted the binary. In the formal
result, `runtime_v2_acceptance_of_selected_binary: true` means the selected
binary is eligible to be submitted to the reviewed runtime-v2 acceptance
process; acceptance remains pending in the runtime repository.

Remaining blockers are unchanged in authority:

1. The native runtime must independently implement/review the stateful 115-D
   v2 contract and reproduce the selected graph's packaged golden vectors.
2. The real-build torso COM/inertia packet still has exactly 46 missing
   source-backed physical inputs and no numerical estimate.
3. Gate 5 is `NOT_RUN` and unauthorized. Robot, RDK-X5, motors, torque, local
   GPU, and iGPU access remain prohibited by the policy repository.

## Compact relay

```text
POLICY_HANDOFF_STATUS: BLOCKED
DISPOSITION: REQUIRES_REVIEWED_115_RUNTIME_V2
POLICY_REPO_COMMIT: e0badd7aa79ff791212b8d3822f9eefdc4c162e0
ARTIFACT_ROOT: artifacts/runtime_handoff/rdkx5_native_20260719
HANDOFF_MANIFEST_SHA256: d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5
SELECTED_CHECKPOINT_STEP: 512000
SELECTED_ONNX: artifacts/runtime_handoff/rdkx5_native_20260719/policies/T2_EQUAL_512000.onnx
SELECTED_ONNX_SHA256: 99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de
INPUT_CONTRACT: obs float32[1,115] + previous_action float32[1,14] -> continuous_actions float32[1,14] + previous_action_out float32[1,14]
ROBOT_CLEARANCE_IN_POLICY_REPO: false
UNRESOLVED_BLOCKERS: reviewed native runtime v2 acceptance incomplete; real-build torso COM/inertia audit has 46 missing inputs and no numerical estimate; Gate 5 NOT_RUN and unauthorized
```
