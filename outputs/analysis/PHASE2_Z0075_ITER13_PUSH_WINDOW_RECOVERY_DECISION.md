# Phase 2 z=0.0075 Iter13 Push-Window Recovery Decision

status: `HOLD_ITER13_PUSH_WINDOW_RECOVERY_PARTIAL`

This is offline sim/data work only. It did not SSH, deploy, train PPO, run robot tests, or change runtime behavior.

## Summary

Iter13 tested a bounded data/live-oracle recovery step for the `home-support`, rough z=0.0075, intermediate-push blocker:

1. extract unrecovered active push-window snippets from traced failed seeds 0, 2, and 6
2. relabel those visited states with the corrected z=0.0075 source-VX teacher
3. merge the 175 relabeled samples into the Iter10 spike-local base manifest
4. fit a phase/command-modulated deployable BC student
5. gate only on the known failed seeds before any full promotion test

## Artifacts

- snippets: `outputs/analysis/PHASE2_Z0075_HOME_SUPPORT_PUSH_WINDOW_SNIPPETS.md`
- relabel: `outputs/analysis/PHASE2_Z0075_HOME_SUPPORT_PUSH_WINDOW_RELABEL.md`
- relabel manifest: `outputs/analysis/PHASE2_Z0075_HOME_SUPPORT_PUSH_WINDOW_RELABEL_MANIFEST.md`
- merged manifest: `outputs/analysis/PHASE2_Z0075_ITER13_PUSH_WINDOW_RECOVERY_MERGED_MANIFEST.md`
- student: `outputs/analysis/PHASE2_Z0075_ITER13_PUSH_WINDOW_RECOVERY_RATE150_STUDENT.md`
- candidate: `policy/candidates/phase2_z0075_iter13_push_window_recovery_rate150_20260704/candidate.onnx`

## Fail-Seed Gate

Condition:

- task: `rough_terrain_backlash`
- z scale: `0.0075`
- reset_mode: `home-support`
- command_x: `0.08`
- bridge: corrected fitted bridge
- push interval: `1.0-1.5s`
- push magnitude: `0.075-0.125`
- seeds: `0,2,6`

| seed | status | samples | vx | track | pitch p95 | base min | p95 excess | max excess | tracking p95 | pushes | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 105 | 0.1800 | 2.2503 | 0.9921 | 0.0216 | 0.0000 | 0.0000 | 0.1872 | 1 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0263 | 0.3291 | 0.1747 | 0.1532 | 0.0000 | 0.0000 | 0.1821 | 13 | 0.9231 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0300 | 0.3747 | 0.1652 | 0.1532 | 0.0000 | 0.0000 | 0.1826 | 13 | 0.9231 |

## Preservation Screen

Iter13 seed 0 with the same rough z=0.0075 `home-support` condition but no push passes full duration:

- samples: `750`
- mean vx: `0.0337 m/s`
- track ratio: `0.4207`
- p95 velocity excess: `0.0000`
- max velocity excess: `0.0000`
- max tracking p95: `0.1844 rad`

## Decision

`HOLD_ITER13_PUSH_WINDOW_RECOVERY_PARTIAL`

The push-window relabel path is useful but incomplete. It repairs the late/repeated-push failures on seeds 2 and 6 and preserves seed0 no-push motion, but it does not repair seed0's first-push lunge/pitchover. This is not promotable and should not run a full 8-seed promotion gate yet.

## Next Step

Trace Iter13 seed0 under the same intermediate-push condition and classify the remaining failure. The next recovery pass should be seed0 first-push specific, not another broad relabel or scalar reward run.
