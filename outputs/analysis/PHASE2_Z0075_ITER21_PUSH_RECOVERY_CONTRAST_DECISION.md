# Phase 2 z0.0075 Iter21 Push-Recovery Contrast Decision

status: `HOLD_POST_PUSH_RECOVERY_STATE_MISMATCH`

Offline-only analysis. No robot tests, SSH, deploy, grounded replay, runtime
behavior change, policy edit, or training was performed.

## Inputs

- candidate: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- candidate_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- gate_json: `outputs/analysis/phase2_z0075_iter21_resetsettle10_seed0_5_fullobs_push_contrast_gate.json`
- gate_json_sha256: `49f2f621f2657b4728019adfe2cb9a4c801bb8e0bf1d92f2766cefa012b3381d`
- contrast_json: `outputs/analysis/phase2_z0075_iter21_resetsettle10_seed5_push_contrast.json`
- contrast_json_sha256: `5e3ebe82f6e10c1a41c4517acb76939850e108279ebba069afb6dbc004ea40e7`
- contrast_report: `outputs/analysis/PHASE2_Z0075_ITER21_RESETSETTLE10_SEED5_PUSH_CONTRAST.md`

## Gate Reproduction

The focused full-observation rerun reproduced the existing Iter21 reset-settle10
failure split under the same rough/intermediate-push gate:

| seed | status | samples | track_ratio | max_vel_excess | push_success |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3391 | 0.0000 | 0.9167 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 599 | -0.0672 | 0.0000 | 0.9000 |

Both runs stayed inside the corrected per-joint target-velocity envelope. The
remaining failure is therefore not a target-rate violation.

## Contrast Finding

The first push windows are similar enough that the seed5 failure should not be
treated as a simple startup or first-disturbance mismatch:

| seed/window | mean_vx | max_abs_pitch | min_base_height | push_events |
|---|---:|---:|---:|---:|
| seed0 first_push | 0.0207 | 0.1872 | 0.1593 | 2 |
| seed5 first_push | 0.0142 | 0.1890 | 0.1606 | 1 |

The separation appears in the late post-push window:

| seed/window | mean_vx | max_abs_pitch | min_base_height | push_events |
|---|---:|---:|---:|---:|
| seed0 late | 0.0270 | 0.1330 | 0.1635 | 2 |
| seed5 late | -0.2181 | 1.5047 | 0.0630 | 1 |

Top late-window separating channels in the contrast audit include obs `3`, `1`,
`5`, and pitch-chain/history channels. The failure signature is a late
post-push backward/pitch collapse, not an envelope spike or an initial reset
spike.

## Decision

`HOLD_POST_PUSH_RECOVERY_STATE_MISMATCH`

Do not promote this candidate and do not run robot validation.

This closes these fixes for the Iter21 near-miss:

- direct startup spike relabels;
- startup-window relabels;
- global output gain;
- stronger global supervised rate cleanup;
- PPO behavior-prior reward tuning from an older restore point.

The next offline work should target a state-conditioned post-push recovery
mapping:

1. Use the seed5 late post-push failure window as negative/drift coverage.
2. Query or construct recovery labels on those student-visited states without
   changing the stable first-push behavior.
3. Preserve the reset-settle10 convention while testing this branch.
4. Re-gate the full x=0.08 rough/intermediate-push seeds `0-7`, then the x=0.0
   command semantics gate.

The Phase 2 goal remains active and incomplete.
