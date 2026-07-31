# Corrected Bridge Campaign Goal

Status: `STEP0_CORRECTED_BRIDGE_PINNED`

## Objective

Produce a deployable policy that walks forward 8/8 seeds in-envelope against
the corrected actuator bridge. That is the prerequisite for the first grounded
hardware test.

No grounded replay, robot deployment, runtime tuning, gain change, offset edit,
IMU remap, phase timing change, action-scale change, or policy overwrite is in
scope until this gate passes in sim.

## Locked Findings

- The left-knee offset correction is validated. The current configured knee
  soft offsets are `left_knee = 0.0371 rad` and `right_knee = 0.0798 rad`.
- Low-speed pitch-chain tracking after the correction passed 0.25, 0.5, and
  1.0 Hz sine sweeps at 0.03 rad amplitude.
- The corrected suspended `x=0.08` replay of `BEST_WALK_ONNX_2` is still not
  dynamically trackable. Pitch-chain sent-target p95 velocities remain about
  `3.14-5.22 rad/s`, while pitch-chain tracking p95 remains about
  `0.125-0.171 rad` after startup filtering.
- Direct deployment of `BEST_WALK_ONNX_2` remains dead. It is evidence, not a
  robot candidate.
- Grounded replay remains blocked until a deployable candidate clears the
  corrected-bridge gate below.

## Canonical Corrected Bridge

The single canonical actuator model for subsequent sim/eval/training work is:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
selection metric: trimmed_rmse_95
source telemetry: corrected suspended x=0.08 dynamic replay
```

The old pre-correction bridge is historical only:

```text
outputs/analysis/actuator_response_fit.json
sha256: 9e0a8e489469b76e3a41bc44fb7e1398b57e13c7da723484a913127b24bc6959
status: deprecated for candidate gates
```

The sine-only corrected fit is a low-speed sanity artifact only. It must not be
used to approve walking:

```text
outputs/analysis/actuator_response_fit_corrected_knee_sine_only.json
```

## Corrected Per-Joint Gate Envelope

Future candidate gates must use the corrected per-joint fitted velocity limits,
not the old global `3.75 rad/s` ceiling.

| joint | delay_ticks | tau_s | fitted velocity limit rad/s |
|---|---:|---:|---:|
| left_hip_pitch | 3 | 0.020 | 2.50 |
| left_knee | 3 | 0.020 | 3.25 |
| left_ankle | 3 | 0.020 | 2.75 |
| right_hip_pitch | 3 | 0.020 | 2.25 |
| right_knee | 3 | 0.020 | 2.75 |
| right_ankle | 3 | 0.020 | 2.00 |

The `tau_s = 0.020` values hit the lower grid bound in the fit. Treat the model
as a practical target-delay / effective-velocity bridge, not as a literal
servo-internal time constant.

## Strict Candidate Gate

Canonical evaluator:

```text
task: flat_terrain_backlash
bridge fit: outputs/analysis/actuator_response_fit_corrected_knee.json
bridge mode: fitted
duration: 15 seconds
seeds: 0-7
```

For `x=0.08`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean track ratio: >= 0.50
pitch-chain sent velocity p95: <= corrected per-joint fitted limits
max pitch-chain tracking p95: <= 0.20 rad
```

For `x=0.0`, all must pass:

```text
duration_complete: 8/8
falls: 0/8
mean |vx|: <= 0.005 m/s
pitch-chain sent velocity p95: <= corrected per-joint fitted limits
```

Promotion requires ONNX export and action fidelity error no greater than
`1e-6`. A smoke-only or old-bridge pass is not promotable.

## Read-Checksum Bias Check

The corrected replay ended with 20 read-checksum errors and 0 write errors.
As a sensitivity check, the fit was rerun after dropping every tick where the
read-error counter incremented plus a +/-2 tick window.

Artifacts:

```text
outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE_EXCLUDE_READ_EVENTS.md
outputs/analysis/actuator_response_fit_corrected_knee_exclude_read_events.json
outputs/analysis/CORRECTED_BRIDGE_READ_ERROR_BIAS_CHECK.md
outputs/analysis/corrected_bridge_read_error_bias_check.json
```

Result:

- Delay remained `3 ticks` for every pitch-chain joint.
- Most velocity limits remained close to the full corrected fit.
- The left-knee exclusion fit hit the `6.0 rad/s` upper grid bound, so it is not
  suitable as a looser candidate envelope.

Decision: keep the full corrected dynamic fit as the conservative canonical
bridge. The checksum sensitivity is logged as a warning, not as permission to
loosen the gate. A later cleaner replay may replace the canonical bridge only
after the same documentation and hash-pinning process.

## Step 1 Decision Gate

Teacher data and selectors built against the old asymmetric bridge are suspect.
Re-establish feasibility against the corrected bridge:

1. Re-roll `BEST_WALK_ONNX_2` in sim through the corrected bridge.
2. Re-mine moving, single-support, in-envelope windows using the corrected
   per-joint limits above.
3. Test whether the earlier one-sided left-stance / right-knee behavior was an
   artifact of the old knee asymmetry.
4. If the corrected mined windows are naturally balanced across both stance
   sides, drop the old right-knee-cap relabel workaround from the new campaign.

Do not proceed to deployable-student work until this corrected-bridge
feasibility gate is explicitly reported.

Step 1 result:

```text
status: HOLD_OLD_TEACHER_SOURCE_NOT_CORRECTED_BRIDGE_FEASIBLE
reroll artifact: outputs/analysis/CORRECTED_BRIDGE_BEST_WALK_REROLL_X008.md
window artifact: outputs/analysis/CORRECTED_BRIDGE_TEACHER_WINDOWS_X008.md
decision artifact: outputs/analysis/CORRECTED_BRIDGE_STEP1_FEASIBILITY_DECISION.md
```

The corrected bridge reroll found `0/8` candidate passes for
`BEST_WALK_ONNX_2` at `x=0.08`. Window mining found only `1/1030` corrected
in-envelope short windows, and that window was double-support-centered rather
than a balanced left/right stance source. The old source-VX teacher data and
old right-knee relabel hack must be treated as historical diagnostics, not as
the current deployable-policy path.

## Existing Candidate Screen And Promotion

A short corrected-bridge screen checked selected existing ONNX candidates:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_EXISTING_CANDIDATE_SCREEN.md
duration: 3 s
seeds: 0, 1
```

Only `cmd_conditioned` passed the short screen inside the corrected per-joint
velocity envelope and below `0.20 rad` pitch-chain tracking p95. It was then
run through the full corrected gate:

```text
decision artifact: outputs/analysis/CORRECTED_BRIDGE_DEPLOYABLE_CANDIDATE_DECISION.md
stable candidate package: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/
candidate: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
candidate sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
```

Corrected `x=0.08` gate:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_FULL_GATE.md
duration: 15 s
seeds: 0-7
passes: 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0339 m/s
mean track ratio: 0.4238
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.1973 rad
```

Corrected `x=0.0` gate:

```text
artifact: outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_X0_GATE.md
duration: 15 s
seeds: 0-7
passes: 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0003 m/s
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.0748 rad
```

Decision: `cmd_conditioned` is the current corrected-bridge sim-side deployment
candidate for stand/suspended hardware telemetry validation only. It is a slow
in-envelope forward walker, not a full-speed `x=0.08` tracker. Grounded replay
remains blocked until reviewed stand/suspended telemetry clears.

## Falsifiers

Stop the branch and write a decision artifact if:

- no corrected-bridge in-envelope moving windows can be mined from the current
  policy evidence,
- corrected-bridge windows remain one-sided and still require the old
  right-knee-cap relabel hack,
- all deployable students hold above `0.24 rad` tracking p95 after the
  corrected bridge is pinned and the corrected windows are re-mined,
- the candidate improves fall count by freezing rather than producing coherent
  forward motion.

In all falsifier cases, do not reopen old global-blend, old-bridge, or
runtime-smoothing branches without a new written decision.
