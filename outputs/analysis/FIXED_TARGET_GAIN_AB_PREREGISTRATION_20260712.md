# Fixed-target gain A/B preregistration

Date: 2026-07-12

Status: `OFFLINE_READY_NOT_AUTHORIZED`

## Question

The closed-loop P31/34 trial was visually clean but did not pass tracking, and
its IMU state/targets differed from the P30 run. Test whether the gains have any
causal actuator-tracking effect when target sequence and timing are identical.

## Frozen target

Source: the clean candidate-5 P30 suspended x=0.08 run.

```text
source JSONL SHA256: f03f85182c8830762fc9de4643bd49286eaec7907929acc20a2e439f653f2fc4
target artifact SHA256: 3f5fd9c304f0613fd861b7a1922c62c2c2e58d63e0d5fad2f88a3c2d40b50e77
policy SHA256: e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
samples: 747
period: 0.02 s
joints: 14, canonical order
```

The target artifact remains outside Git with raw evidence at
`outputs/first_evidence/20260712T_fixed_target_gain_ab/x008_fixed_targets.json`.

## Fixed A/B

1. Replay the exact 747 targets at normal body/head P 30/8, D 0.
2. Return home, restore gains, torque off, and pause.
3. Replay the identical targets at left hip/knee P 31/34; every other gain is
   unchanged.
4. Restore body/head P 30/8, D 0 and torque off in mandatory cleanup.

No policy is loaded, no IMU input is used, no EEPROM is changed, and ID 13
remains last in the read order. Tracking is calculated exactly as actual current
position versus the previous tick target, matching live telemetry semantics.

## Decision

- Support gain effect only if both left hip and left knee p95 decrease by at
  least 10% and neither any-joint p95 nor max error increases by more than 10%.
- Reject P31/34 otherwise. Do not tune gain values after seeing the result.
- Abort on unexpected motion, oscillation, asymmetry, bus/write error, timing
  failure, or operator concern.

This is approximately 30 seconds of suspended motion in two phases and requires
new explicit approval. It does not authorize x=0.08 policy replay or grounding.
