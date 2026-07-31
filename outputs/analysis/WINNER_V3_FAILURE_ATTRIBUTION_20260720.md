# Winner-v3 Failure Attribution — 2026-07-20 (corrected primary-source audit)

status: `PASS_WINNER_V3_READ_ONLY_FAILURE_ATTRIBUTION_CORRECTED`

decision: `HOLD_TRAINING_PENDING_CURRENT_GATE_APPLICATION_CONTRACT_AND_RESPONSE_CONDITIONING_PREREGISTRATION`

Correction: the first published audit consulted the current Feetech product page but missed Feetech's 2024 catalog, which explicitly lists `650 mA` rated current at `7.4 V`. This version supersedes the current-provenance interpretation only. It does not change any cell, metric, threshold, or the completed winner-v3 result.

## Evidence result

All `1024` committed cells and all `1024` local traces were read, rehashed, and replayed for current/tracking aggregation. Physical pass remains `48/1024`. Removing only the frozen current check for attribution—not reclassification—leaves `753` otherwise-passing cells and `271` cells with at least one other physical failure. `705` cells fail only the current check.

## Current gate provenance and feasibility

The completed gate is unchanged. Its metric is per-joint p95 over every recorded tick of `abs(MuJoCo actuator_force Nm) / 0.784532 Nm/A`; the cell value is the maximum of 14 joint p95 values. The `0.65 A` threshold and `8 kgf.cm/A` conversion first appear together in preregistration commit `58a8a1d`; no older repository source, manufacturer citation, measured torque-current fit, voltage dependence, or uncertainty is supplied.

Feetech's 2024 catalog reports rated torque `5 kg.cm @ 7.4 V`, rated current `0.65 A @ 7.4 V`, peak stall torque `19.5 kg.cm @ 7.4 V`, and stall current `2.5 A @ 7.4 V`. Thus `0.65 A` has primary-source support as a rated operating point. The catalog does not specify a p95-over-600-ticks safety rule, a duty/thermal population, or the repository's `8 kg.cm/A` conversion. The rated-point quotient is `0.754357692 N.m/A`; the repository uses `0.784532 N.m/A`, exactly 4% higher. Runtime's `0.0065 A/count` correctly makes `0.65 A` equal 100 telemetry counts, but that scale alone does not define a p95 safety contract. Catalog: https://www.feetechrc.com/Data/feetechrc/upload/file/20240706/2024%E9%A3%9E%E7%89%B9%E5%AE%A3%E4%BC%A0%E5%86%8C.pdf

Feetech's current product page separately reports the 6 V operating point (`6.5 kg.cm` rated torque, `19.5 kg.cm` peak stall torque, `2.0 A` stall current) but no rated current. These sources are voltage-specific rather than interchangeable. Product page: https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear.html

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

Broad latent-domain exposure plus a 64-state recurrent adapter therefore tested implicit online adaptation; it did not clear signed X or the full coupled matrix. Repeating blind domain randomization is not selected. The falsifiable follow-up is ordered: (1) prospectively define the current/torque gate application from documented motor limits, duty/aggregation semantics, and measured telemetry without changing this result; (2) freeze and runtime-review an automatic-response-conditioned interface or estimator that uses no manual per-build measurement; (3) only then preregister one training run and the unchanged full behavior matrix.

No new training is authorized by this audit alone. No policy is selected and robot clearance remains false.
