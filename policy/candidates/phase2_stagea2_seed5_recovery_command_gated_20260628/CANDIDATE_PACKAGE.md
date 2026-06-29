# Phase 2 Stage-A2 / Seed5-Recovery Command-Gated Candidate

status: `PASS_ROUGH_TERRAIN_NO_PUSH_HOLD_GENTLE_PUSH_ENVELOPE`

This candidate is a deployable-shape ONNX wrapper:

```text
obs[1,101] -> continuous_actions[1,14]
```

It is an offline sim candidate only. It is not approved for robot validation.

## Artifact

```text
candidate: policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx
sha256: d0cec0b9dcc666416f0ecc8383a51367529273013d912b26399339e2c4b1c3e6
```

## Branches

```text
low command branch:
  policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
  sha256: a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4

high command branch:
  outputs/analysis/phase2_seed5_neighbor_recovery_contactphase_bc_student/candidate.onnx
  sha256: dbabaa9f6f364a3beb39166f803babac83d575c157046ef3736c76422db78d9c

gate:
  abs(obs[6]) <= 0.02 -> low branch
  abs(obs[6]) > 0.02  -> high branch
```

ONNX verification:

```text
outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_verify.json
status: PASS_ONNX_GATE_VERIFY
max action error: 0.0
```

## Gates

Corrected bridge:

```text
outputs/analysis/actuator_response_fit_corrected_knee.json
```

No-push rough terrain, `rough_terrain_backlash`, hfield `z=0.002`, 5 s:

```text
x=0.08: PASS_CANDIDATE_SIM_GATE 8/8
  mean vx: 0.0332 m/s
  mean track ratio: 0.4150
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1984 rad

x=0.0: PASS_CANDIDATE_SIM_GATE 8/8
  mean vx: 0.0024 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1056 rad
```

Gentle-push rough terrain, interval `1.0-1.5 s`, magnitude `0.05-0.10`:

```text
x=0.08: HOLD_CANDIDATE_TARGET_VELOCITY
  falls: 0/8
  mean push recovery success: 0.9062
  max velocity excess: 0.0212 rad/s

x=0.0: PASS_CANDIDATE_SIM_GATE 8/8
```

## Decision

The candidate is useful as the next Phase 2 offline warm start because it is
the first deployable-shape rough-terrain no-push pass in this branch.

It is not robot-approved. The next offline task is to recover the small
high-command envelope margin under gentle pushes without losing the no-push
rough-terrain pass.
