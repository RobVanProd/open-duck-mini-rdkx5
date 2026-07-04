# Phase 2 z=0.0075 Push-Window Recovery Next Step

status: `PRE_REGISTERED_NOT_STARTED`
verdict_source:

- `outputs/analysis/PHASE2_Z0075_SEED5_RESET_SENSITIVITY_DECISION.md`
- `outputs/analysis/PHASE2_Z0075_HOME_SUPPORT_PUSH_TRIAGE_DECISION.md`
- `outputs/analysis/PHASE2_Z0075_HOME_SUPPORT_PUSH_FAILURE_TRACE_DIAGNOSTIC.md`

This is an offline next-step registration. It does not train, SSH, deploy, run robot tests, or change runtime behavior.

## Current Evidence

The Iter10 z=0.0075 spike-local candidate is not baseline rough-terrain limited once reset is aligned:

- `home-support`, rough z=0.0075, no push: targeted failed seeds 0, 2, and 6 pass 15 seconds.
- `home-support`, rough z=0.0075, intermediate push: 5/8 pass, seeds 0, 2, and 6 fail.
- traced failed seeds classify as `PUSH_WINDOW_PITCHOVER`.
- corrected-envelope velocity excess remains zero in the traced push failures.
- seed 5's previous immediate failure is explained by `playground` reset sensitivity.

Therefore the next aligned Phase 2 work is push-window recovery under the corrected bridge, not terrain-height weighting, more feed-forward BC weighting, or another broad scalar PPO retry.

## Closed Branches For This Failure

Do not spend the next run on:

- more rough-terrain/no-push labels
- more pass-control/reverse-oracle feed-forward label weighting
- `reset_settle_ticks` as a fix for Playground reset
- over-envelope recovery maneuvers
- robot-side validation

The reset-contract audit remains open, but it is separate from the push-window recovery problem.

## Next Training Target

Train or relabel only for this mechanism:

```text
condition:
  corrected bridge
  rough_terrain_backlash
  z = 0.0075
  reset_mode = home-support
  command_x = 0.08
  push interval = 1.0-1.5s
  push magnitude curriculum = gentle -> intermediate

failure to fix:
  active push-window pitchover / base-height collapse

must preserve:
  no-push rough z=0.0075 locomotion
  corrected actuator envelope
  x=0.0 command semantics
```

## Stage Gate

A candidate may advance only if all checks pass:

1. `home-support`, rough z=0.0075, no push, x=0.08: 8/8 duration complete.
2. `home-support`, rough z=0.0075, intermediate push, x=0.08: 8/8 duration complete.
3. `home-support`, rough z=0.0075, x=0.0: 8/8 duration complete, near-zero vx.
4. Corrected per-joint velocity excess: zero p95 excess and zero max excess.
5. Push-window trace diagnostic: no `PUSH_WINDOW_PITCHOVER` seeds.
6. Playground reset audit: reported separately, not silently treated as fixed.

## Recommended Implementation Direction

Prefer a data/live-oracle recovery loop over another scalar reward-only run:

1. Use the traced seeds 0, 2, and 6 push failures as the initial recovery-state set.
2. Collect additional on-policy traces only in the active push window and immediate recovery window.
3. Query the corrected source/oracle or a verified pass-control policy only on those visited states.
4. Retrain a deployable student with recovery-window weighting while preserving the no-push/home-support pass behavior.
5. Gate immediately on the six checks above before scaling.

If the implementation path falls back to PPO, keep it bounded and stage the push magnitude; do not launch a broad A100 run until a short CPU/GPU screen shows no-push preservation and at least one repaired failed seed.

## Hard Stop

If the next candidate preserves no-push locomotion but still classifies seeds 0, 2, or 6 as `PUSH_WINDOW_PITCHOVER`, do not add terrain labels. The evidence says the remaining failure is active disturbance recovery.
