# Corrected Bridge Deployable Candidate Decision

status: `PASS_CORRECTED_BRIDGE_SIM_CANDIDATE`

## Candidate

```text
policy: outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate.onnx
sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
bridge_sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
task: flat_terrain_backlash
bridge_mode: fitted
platform: CPU JAX/MJX correctness path
```

This is the first ONNX candidate that clears the corrected actuator bridge
sim-side gate on both commanded motion and zero-command hold.

Package artifact:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_CANDIDATE_PACKAGE.md
outputs/analysis/corrected_bridge_cmd_conditioned_candidate_package.json
package status: READY_FOR_SIM_GATE_REVIEW
contract: obs[1,101] -> continuous_actions[1,14]
candidate gates: x=0.0 8/8, x=0.08 8/8
```

## Corrected x=0.08 Gate

Artifact:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_FULL_GATE.md
outputs/analysis/corrected_bridge_cmd_conditioned_full_gate.json
json_sha256: 533e48e30851c73896d009347eeb882c66e645bb533c4db11b612a7af982f680
```

Result:

```text
duration: 15 s
seeds: 0-7
passes: 8/8
falls: 0/8
duration_complete: 8/8
mean local vx: 0.0339 m/s
mean track ratio: 0.4238
mean body pitch p95: 0.1203 rad
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.1973 rad
```

Interpretation: the candidate moves forward consistently, stays inside the
corrected per-joint pitch-chain velocity envelope, and breaks the previous
tracking plateau by keeping every seed below `0.20 rad` pitch-chain tracking
p95. It is a slow walker, not a full `x=0.08` speed tracker.

## Corrected x=0.0 Gate

Artifact:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_X0_GATE.md
outputs/analysis/corrected_bridge_cmd_conditioned_x0_gate.json
json_sha256: 42e9958fd7f21c19ec2dab4b15404039b755b9f30db81e9dd93daefa9e4fff62
```

Result:

```text
duration: 15 s
seeds: 0-7
passes: 8/8
falls: 0/8
duration_complete: 8/8
mean local vx: 0.0003 m/s
mean body pitch p95: 0.0197 rad
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.0748 rad
```

Interpretation: zero-command semantics are preserved in sim. The candidate does
not drift forward when commanded to stand.

## Short Existing-Candidate Screen

Artifact:

```text
outputs/analysis/CORRECTED_BRIDGE_EXISTING_CANDIDATE_SCREEN.md
outputs/analysis/corrected_bridge_existing_candidate_screen.json
```

The short 2-seed, 3-second screen found the `cmd_conditioned` candidate as the
only checked existing ONNX that stayed inside the corrected velocity envelope
and below `0.20 rad` tracking p95. Other checked candidates held on tracking,
low progress, action saturation, or fall/termination.

## Decision

This candidate is promoted as the current corrected-bridge sim-side deployment
candidate for suspended hardware validation only.

Grounded replay remains blocked until the operator reviews this result and the
candidate passes a stand/suspended hardware telemetry gate. The first hardware
run should be low-risk telemetry capture, not autonomous grounded walking:

- robot on stand or catch rig,
- no grounded replay,
- no tuning during the run,
- log sent target, actual position, read/write errors, contacts if available,
  base pitch/height if available,
- torque off / stop after telemetry.

Prepared operator handoff packets:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X0_HANDOFF.md
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X008_HANDOFF.md
```

These packets were generated with `tools/instrumented_lowcmd_hw_eval.py plan`.
That tool does not SSH, deploy, command motors, or run a policy. The packets
only document the telemetry fields, corrected-knee hash requirement, and
post-run analysis command for an operator-approved stand/suspended procedure.

## Caveats

- The candidate tracks only about `42%` of the requested `x=0.08` command in
  sim. It should be described as a slow in-envelope forward walker.
- The result uses the corrected actuator bridge, not the old asymmetric bridge.
- No robot test, SSH, deploy, runtime behavior change, or training was
  performed while producing this decision artifact.
