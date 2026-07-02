# Phase 2 z=0.00245 Source Seed-5 Probe Decision

status: `HOLD_Z00245_NOT_SOURCE`

## Summary

This probe checked whether the Phase A2 gain099 candidate can provide positive source traces just below the z=0.0025 boundary. It cannot. Seed 5 fails within 2 seconds at both x=0.0 and x=0.08 on z=0.00245 rough terrain.

The already-recorded z=0.0024 source rung remains the usable terrain source. Do not mine z=0.00245 or z=0.0025 seed-5 traces as positive labels for support recovery.

## Candidate

- policy: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- policy_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.00245`
- bridge_mode: `fitted`
- seed: `5`
- duration: `2.0 s`
- jax_platform: `cpu`

## Results

| command_x | status | samples | vx m/s | track ratio | base min m | pitch vel p95 | p95 excess | max excess | tracking p95 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | -0.2428 | NA | 0.0643 | 1.1868 | 0.0000 | 0.0000 | 0.1951 |
| 0.08 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.2718 | -3.3981 | 0.0543 | 2.0270 | 0.0000 | 1.1655 | 0.1930 |

## Interpretation

z=0.00245 is not a safe positive source rung for seed 5. The failure is not simply low forward progress; both commands reverse and terminate. The x=0.08 case also records max velocity-limit excess, so it is not suitable as in-envelope source data.

This narrows the terrain cliff:

- z=0.0024 remains the positive source boundary from prior full gates.
- z=0.00245 already fails the Phase A2 gain099 source candidate on seed 5.
- z=0.0025 remains a boundary/gating target, not a positive label source.

## Decision

- Do not use z=0.00245 or z=0.0025 seed-5 traces as positive BC/DAgger labels.
- Use the known z=0.0024 source manifest for positive terrain behavior.
- Any next support-recovery branch must bridge from z=0.0024 source behavior into z>=0.00245 unsupported/partial-contact resets, rather than treating failed z=0.00245 traces as demonstrations.

## Artifact Hashes

- x=0.0 report: `fa394c5e81aa6ccd3cfd8cca0e9981ffb238dafb4eb50a2af5545748f0fcad78`
- x=0.08 report: `4d97f535d3532a463936be974829213feacac64265e484ae22c0744099195f01`
- x=0.0 JSON: `2dc96a270540560226b8d9000aefe45beb5f611c723025d13a6db09bcca53cd9`
- x=0.08 JSON: `4184591232ff52702a54d810db26d85a395497fa31184d2a379c34a3a5fbabac`

No robot tests, SSH, deploy, grounded replay, or training were performed.
