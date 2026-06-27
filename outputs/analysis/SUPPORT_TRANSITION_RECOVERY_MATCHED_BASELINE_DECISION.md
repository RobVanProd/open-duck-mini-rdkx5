# Support-Transition Recovery Matched Baseline Decision

status: `HOLD_SUPPORT_TRANSITION_SMOKE_REGRESSES_X008`

Purpose: compare the tiny support-transition recovery smoke against the
command-conditioned pitch-rate-limited step-0 warm start on the same canonical
gate:

```text
task: flat_terrain_backlash
bridge: fitted actuator bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
```

No robot test, deploy, SSH, runtime behavior change, or training was performed.

## Compared Artifacts

Warm-start baseline:

```text
outputs/analysis/CMD_PITCH_RL_2P25_STEP0_BACKLASH_X008_FITTED_15S.md
```

Support-transition smoke:

```text
outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_BACKLASH_X008_FITTED_15S.md
```

## Result

| policy | duration complete | falls | mean vx | mean track ratio | mean body pitch p95 | failure mode |
|---|---:|---:|---:|---:|---:|---|
| `cmd_pitch_rl_2p25_step0` | 8 / 8 | 0 | 0.0348 | 0.4344 | 0.1183 | tracking hold |
| `support_transition_smoke` | 7 / 8 | 1 | -0.0284 | -0.3549 | 0.0545 | low/reverse progress + seed 3 fall |

The support-transition smoke preserves canonical x=0 hard-seed standing, but
it is worse than the warm-start baseline at x=0.08:

```text
- introduces one fall/termination
- loses forward progress
- produces negative mean vx and negative mean track ratio
- improves posture only by suppressing useful movement
```

## Decision

Do not scale this exact support-transition reward mix to A100.

The next offline run should not be another scalar adjustment of the same
recipe. It needs a stronger behavior-preservation or closed-loop recovery
mechanism that keeps the warm start's forward motion while reducing fitted
tracking error.

Robot validation remains blocked.
