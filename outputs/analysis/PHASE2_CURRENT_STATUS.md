# Phase 2 Current Status

status: `HOLD_PHASE2_TERRAIN_Z005_NOT_CLEARED`
generated_at: `2026-06-29T18:03:12Z`

## Candidate

- name: `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629`
- path: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- contract: `PASS_POLICY_CONTRACT` obs=101 action=14
- transform: `onnx_output_action_scale` scale=0.99 verify=PASS_ONNX_OUTPUT_SCALE_VERIFY

## Gate Matrix

| gate | status | pass/total | x | z | push | track ratio mean | vx mean | max tracking p95 | max pitch vel p95 | max vel excess |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| z002_x008_nopush | `PASS_GATE_8SEED` | 8/8 | 0.080 | 0.002 | no | 0.405 | 0.0324 | 0.1975 | 2.3978 | 0.0000 |
| z002_x000_nopush | `PASS_GATE_8SEED` | 8/8 | 0.000 | 0.002 | no | NA | 0.0007 | 0.0663 | 0.3997 | 0.0000 |
| z002_x008_gentle_push | `PASS_GATE_8SEED` | 8/8 | 0.080 | 0.002 | yes | 0.410 | 0.0328 | 0.1944 | 2.3950 | 0.0000 |
| z002_x000_gentle_push | `PASS_GATE_8SEED` | 8/8 | 0.000 | 0.002 | yes | NA | 0.0007 | 0.0687 | 0.3906 | 0.0000 |
| z005_x008_nopush | `HOLD_GATE` | 7/8 | 0.080 | 0.005 | no | -0.069 | -0.0055 | 0.1968 | 2.4032 | 0.0000 |
| z005_x000_nopush | `HOLD_GATE` | 7/8 | 0.000 | 0.005 | no | NA | -0.0322 | 0.1953 | 1.2575 | 0.0000 |

## Blocking Gate Detail

- gate: `z005_x008_nopush`
  - first failing seed: `5`
  - status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
  - termination: `fall_or_nan`
  - track_ratio: `-3.3180`
  - mean_local_vx_m_s: `-0.2654`
  - base_height_min_m: `0.0677`
- gate: `z005_x000_nopush`
  - first failing seed: `5`
  - status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
  - termination: `fall_or_nan`
  - track_ratio: `NA`
  - mean_local_vx_m_s: `-0.2589`
  - base_height_min_m: `0.0512`

## Backend

| artifact | status | robot | ssh | deploy | note |
|---|---|---|---|---|---|
| local_rocm_hold | `HOLD_FULL_LOCAL_ROCM_COMPILE_NO_PROGRESS` | False | False | False | Local ROCm can run basic JAX GPU arithmetic and a tiny no-override training smoke. The gfx override causes immediate context failure, while the no-override full-shape run did not reach first checkpoint in bounded time. This is not a policy or recipe result. |
| local_rocm_command_buffer | `HOLD_LOCAL_8ENV_LOW_FORWARD_PROGRESS` | False | False | False | The reduced local ROCm candidate is not a deployable or robot-test candidate. The backend workaround is useful; the policy result is a low-forward-progress hold. |

## z=0.005 Seed-5 Diagnostic

- status: `HOLD_Z005_SEED5_SUPPORT_COLLAPSE_DIAGNOSED`
- artifact: `outputs/analysis/phase2_z005_seed5_failure_diagnostic.json`
- robot_touched: `False`
- ssh_used: `False`
- deploy_performed: `False`
- training_started: `False`

- seed 5 collapses vertically on z=0.005 in both command modes
- failure is backward-biased even at zero command
- failure is not caused by corrected-envelope velocity excess
- support pattern is double-support dominated before collapse

recommendation: The next z=0.005 support recipe should target seed-5 terrain support and base-height margin while preserving the z=0.002 gait. Do not treat this as an actuator-envelope or action-saturation problem.

## Decision

- next_status: `HOLD_PHASE2_TERRAIN_Z005_NOT_CLEARED`
- next_action: Current packaged candidate is robust at z=0.002 including gentle push, but z=0.005 terrain is not cleared. Continue Phase 2 z=0.005 support training from the corrected-bridge candidate.

No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this report.
