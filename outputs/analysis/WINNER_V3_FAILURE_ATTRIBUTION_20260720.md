# Winner-v3 Failure Attribution — 2026-07-20

status: `PASS_WINNER_V3_READ_ONLY_FAILURE_ATTRIBUTION`

decision: `HOLD_TRAINING_PENDING_CURRENT_CONTRACT_CORRECTION_AND_RESPONSE_CONDITIONING_PREREGISTRATION`

## Evidence result

All `1024` committed cells and all `1024` local traces were read, rehashed, and replayed for current/tracking aggregation. Physical pass remains `48/1024`. Removing only the frozen current check for attribution—not reclassification—leaves `753` otherwise-passing cells and `271` cells with at least one other physical failure. `705` cells fail only the current check.

## Current gate provenance and feasibility

The completed gate is unchanged. Its metric is per-joint p95 over every recorded tick of `abs(MuJoCo actuator_force Nm) / 0.784532 Nm/A`; the cell value is the maximum of 14 joint p95 values. The `0.65 A` threshold and `8 kgf.cm/A` conversion first appear together in preregistration commit `58a8a1d`; no older repository source, manufacturer citation, measured torque-current fit, voltage dependence, or uncertainty is supplied.

The manufacturer's STS3215-C001 page reports rated torque `6.5 kg.cm @ 6 V`, peak stall torque `19.5 kg.cm @ 6 V`, and stall current `2.0 A @ 6 V`; it does not report a `0.65 A` rated-current limit or an `8 kg.cm/A` conversion. Runtime's `0.0065 A/count` is a telemetry-register scale, not evidence for a 100-count safety cap. Source: https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear.html

The infeasibility is deterministic: all eight nominal x=0 cells have exact-zero graph actions for all 600 ticks, yet the identical home-hold right-knee p95 is `0.661276083 A`, above `0.65 A`. Training policy weights cannot change that cell while the x=0 deadband, home/reset, model, and threshold remain frozen.

## Temporal ordering

`current_p95` onset is the first tick after which the running per-joint p95 stays above 0.65 A through the recorded end. Direction onset is the first tick after which cumulative mean local vx remains nonpositive. Tracking uses the analogous persistent running-p95 rule. These definitions match final gate populations and avoid choosing an arbitrary window.

- versus `direction`: `comparison_event_absent` 837, `current_after` 107
- versus `saturation`: `comparison_event_absent` 906, `current_before` 38
- versus `tracking_p95`: `comparison_event_absent` 940, `current_before` 4
- versus `early_termination`: `comparison_event_absent` 737, `current_before` 207
- versus `base_height`: `comparison_event_absent` 737, `current_before` 207
- versus `pitch`: `comparison_event_absent` 737, `current_before` 207

## Signed X mechanism

`COM_X_NEG` has `16` cells: `16` terminate early and `12` finish with nonpositive mean vx. `COM_X_POS` has `16` cells: `7` terminate early and `0` finish with nonpositive mean vx. Exact body-2 `trunk_assembly` readback, signed +/−0.05 m X mutation, raw command propagation, and reset state all validate per run.

Negative X produces backward reversal/fall; positive X produces forward overspeed/fall in the recorded traces. The signs follow the static sagittal moment and are not command normalization, wrong-body, reset, or transform-load defects.

## Nominal regression comparison

All `16/16` historical G1/T2 nominal cells and all `16/16` like-for-like winner-v3 nominal cells pass the pre-current behavior gates. Winner-v3 nominal failures are `16/16` current checks only. Mean-vx delta spans `-0.012370001` to `0.025700431 m/s`; worst-tracking delta spans `-0.019454876` to `0.000000000 rad`. Historical traces did not store actuator force/current, so no baseline current regression is claimed.

## Observability and selected next mechanism

The deployable 115-D observation contains IMU, command, joint state, action history, P30 applied-target observer state, contacts, phase, and projected reference action. It contains no torso mass, COM XYZ, inertia tensor, all-link mass scale, actuator-fit identity, delay scalar, or transport-condition identifier. Those quantities can affect dynamic response but are not uniquely identified as physical parameters by the current interface or the frozen automatic response profile.

Broad latent-domain exposure plus a 64-state recurrent adapter therefore tested implicit online adaptation; it did not clear signed X or the full coupled matrix. Repeating blind domain randomization is not selected. The falsifiable follow-up is ordered: (1) prospectively repair the current/torque contract from documented motor limits and measured telemetry without changing this result; (2) freeze and runtime-review an automatic-response-conditioned interface or estimator that uses no manual per-build measurement; (3) only then preregister one training run and the unchanged full behavior matrix.

No new training is authorized by this audit alone. No policy is selected and robot clearance remains false.
