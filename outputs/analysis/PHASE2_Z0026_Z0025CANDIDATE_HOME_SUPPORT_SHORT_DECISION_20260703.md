# Phase 2 z=0.0026 z=0.0025-Candidate Home-Support Short Decision

status: `PASS_Z0026_HOME_SUPPORT_SHORT_STABILITY_SLOW`

This was an offline short-screen diagnostic only. It did not SSH, deploy, run
robot tests, change robot runtime behavior, train, or run grounded replay.

## Candidate

```text
outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx
```

This is the current z=0.0025 corrected-bridge candidate. The diagnostic tested
whether its previous z=0.0026 seed-5 hold was caused by the broad randomized
reset contract rather than by the policy itself.

## x=0.08 Short Screen

Artifact:

```text
outputs/analysis/PHASE2_Z0026_Z0025CANDIDATE_HOME_SUPPORT_X008_SHORT.md
```

Result:

```text
duration:             2.0 s
seeds:                0-7
reset_mode:           home-support
falls:                0/8
duration_complete:    8/8
status:               PASS_CANDIDATE_SIM_GATE on all seeds
mean_vx:              0.0223 m/s
track_ratio:          0.2784
max_pitch_vel_p95:    1.8717 rad/s
p95_vel_excess:       0.0000
max_tracking_p95:     0.1868 rad
single_support:       4.0 %
double_support:       96.0 %
```

## x=0.0 Short Screen

Artifact:

```text
outputs/analysis/PHASE2_Z0026_Z0025CANDIDATE_HOME_SUPPORT_X000_SHORT.md
```

Result:

```text
duration:             2.0 s
seeds:                0-7
reset_mode:           home-support
falls:                0/8
duration_complete:    8/8
status:               PASS_CANDIDATE_SIM_GATE on all seeds
mean_vx:              0.0033 m/s
max_pitch_vel_p95:    2.7472 rad/s
p95_vel_excess:       0.0000
max_tracking_p95:     0.1901 rad
double_support:       100.0 %
```

## Decision

Under the grounded-home reset contract, the z=0.0025 candidate survives z=0.0026
short screens at both `x=0.08` and `x=0.0`, including seed 5. This supports the
reset-artifact diagnosis for the previous seed-5 z=0.0026 collapse.

This is not a deployable approval. The moving-command behavior is very slow and
double-support dominant (`track_ratio=0.2784`, `double_support=96%`). The next
candidate work should keep the explicit grounded reset contract and improve
single-support/forward progress without violating the corrected bridge envelope.

Before any robot validation, the candidate still needs the full-duration
corrected-bridge gate under the selected reset contract.
