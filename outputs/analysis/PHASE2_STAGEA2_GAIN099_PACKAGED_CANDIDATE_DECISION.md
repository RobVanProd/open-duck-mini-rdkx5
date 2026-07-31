# Phase 2 Stage-A2 Gain-0.99 Packaged Candidate Decision

status: `PASS_PACKAGED_GAIN099_ROUGH_Z002_PUSH_AND_NOPUSH_SIM_GATES`

## Scope

This is an offline sim/package decision. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## Candidate

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b

source_candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx

source_candidate_sha256:
  d0cec0b9dcc666416f0ecc8383a51367529273013d912b26399339e2c4b1c3e6

transform:
  ONNX final action output scale = 0.99

scale_verify:
  PASS_ONNX_OUTPUT_SCALE_VERIFY
  max_abs_error = 0.0
```

This is a real ONNX candidate with the 0.99 action scale baked into the graph.
It does not depend on evaluator-side `policy_action_gain`.

## Gate Matrix

All gates used:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge_mode: fitted corrected knee bridge
duration: 15 s
seeds: 0-7
policy_action_gain: 1.0
```

| command | push | status | falls | mean vx | mean track ratio | max vel excess | max tracking p95 | mean push success |
|---|---|---|---:|---:|---:|---:|---:|---:|
| x=0.08 | no | PASS 8/8 | 0/8 | 0.0324 | 0.4053 | 0.0000 | 0.1975 | NA |
| x=0.0 | no | PASS 8/8 | 0/8 | 0.0007 | NA | 0.0000 | 0.0663 | NA |
| x=0.08 | gentle | PASS 8/8 | 0/8 | 0.0328 | 0.4104 | 0.0000 | 0.1944 | 0.9704 |
| x=0.0 | gentle | PASS 8/8 | 0/8 | 0.0007 | NA | 0.0000 | 0.0687 | 0.9704 |

Artifacts:

```text
x=0.08 no-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X008_ROUGH_Z002_NOPUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json

x=0.0 no-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X0_ROUGH_Z002_NOPUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json

x=0.08 gentle-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X008_ROUGH_Z002_GENTLE_PUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json

x=0.0 gentle-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X0_ROUGH_Z002_GENTLE_PUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json
```

## Decision

Promote this as the current best offline Phase 2 sim candidate. It preserves
command conditioning, stays inside the corrected actuator envelope, survives
rough `z=0.002`, and recovers gentle pushes in 15-second 8-seed gates.

This still does not approve robot validation. Robot-side suspended validation
requires explicit operator approval for that specific test and a separate
hardware run plan.
