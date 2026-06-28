# Corrected Bridge Cmd-Conditioned Rate-175 Candidate

Status: `READY_FOR_STAND_SUSPENDED_TELEMETRY_REVIEW`

This directory preserves the current corrected-bridge sim-side deployment
candidate. It is the first ONNX in this campaign to pass both corrected
actuator-bridge seed gates:

- `x=0.08`, 8/8 seeds, 15 seconds, fitted corrected bridge
- `x=0.0`, 8/8 seeds, 15 seconds, fitted corrected bridge

It is not approved for grounded replay.

## Files

- `candidate.onnx`
- `policy_metadata.json`
- `POLICY_PACKAGE.md`
- `training_manifest.json`

## Policy Hash

```text
63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
```

## Contract

```text
obs[1,101] -> continuous_actions[1,14]
```

The joint/action order is the deployed 14-action Open Duck Mini v2 contract,
including head/neck joints.

## Corrected Bridge

Canonical corrected actuator bridge:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
```

The corrected bridge uses per-joint pitch-chain velocity limits. The old global
`3.75 rad/s` gate and old asymmetric-knee bridge are historical only.

## Sim Evidence

Decision and package artifacts:

```text
outputs/analysis/CORRECTED_BRIDGE_DEPLOYABLE_CANDIDATE_DECISION.md
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_CANDIDATE_PACKAGE.md
```

Corrected `x=0.08` gate:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_FULL_GATE.md
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
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_X0_GATE.md
passes: 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0003 m/s
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.0748 rad
```

Interpretation: this is a slow in-envelope forward walker. It does not fully
track the `x=0.08` speed command, but it moves forward across all eight seeds
while staying inside the corrected actuator envelope.

## Robot Gate

Only stand/suspended telemetry validation is in scope after review.

Operator handoff packets:

```text
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X0_HANDOFF.md
outputs/analysis/CORRECTED_BRIDGE_CMD_CONDITIONED_HW_X008_HANDOFF.md
```

Stand/suspended transfer evidence:

```text
outputs/analysis/CORRECTED_CANDIDATE_STAND_TRANSFER_DECISION.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X0_STAND_ANALYSIS.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_STAND_ANALYSIS.md
outputs/analysis/CORRECTED_CANDIDATE_HW_X008_TARGET_VELOCITY.md
```

Current hardware result:

```text
x=0.0 stand: 747 samples, max pitch-chain tracking p95 0.0145 rad
x=0.08 stand: 747 samples, WARN_PROCEED_WITH_CAUTION
x=0.08 max pitch-chain sent velocity p95: 0.4065 rad/s
x=0.08 max pitch-chain tracking p95: 0.0222 rad
x=0.08 action saturation: 0%
x=0.08 write errors: 0
```

Validation order:

1. stand/suspended `x=0.0` telemetry
2. stand/suspended `x=0.08` telemetry
3. grounded replay only after reviewed suspended telemetry clears

Hard constraints for hardware validation:

- operator physically present
- robot supported on stand/catch rig
- corrected knee config hash recorded
- no tuning during the run
- no gains, offsets, remaps, action-scale, phase, policy, or config changes
- log sent target, actual position, policy action, read/write/CRC counters,
  contacts/base state if available
- torque off / stop after telemetry

Grounded replay remains blocked.
