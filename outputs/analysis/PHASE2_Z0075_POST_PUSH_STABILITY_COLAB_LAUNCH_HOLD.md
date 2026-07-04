# Phase 2 z=0.0075 Post-Push Stability Colab Launch Hold

status: `HOLD_COLAB_TRANSPORT_LOST`
timestamp_utc: `2026-07-04T04:22:10Z`

This is an offline launch-status artifact. It did not train, SSH, deploy, touch
the robot, or run grounded replay.

## Intended Recipe

- recipe: `outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_NEXT_RECIPE.md`
- workflow: `phase2-b0g`
- session: `open-duck-phase2-a100`
- target: z=0.0075 rough terrain, intermediate push `0.075`-`0.125`, corrected bridge
- candidate_name: `phase2_z0075_post_push_stability_cuda`

## Launch Attempt

The registered recipe command was attempted once through
`tools/run_colab_cli_cuda_workflow.py`. The wrapper reached the content API
initialization step and then failed before uploading/running the workflow:

```text
Connection closed.
[colab] Session 'open-duck-phase2-a100' appears to be lost (404/401). Cleaning up.
```

Follow-up transport checks showed the same failure:

- `colab exec` with a tiny Python file returned the same `lost (404/401)` error.
- `colab console` with a tiny shell script closed with the same `lost (404/401)` error.
- `colab sessions` still listed `open-duck-phase2-a100`, but no usable CLI execution channel remained.

## Decision

Do not mark the recipe as trained. The next Phase 2 run remains:

`outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_NEXT_RECIPE.md`

The blocker is Colab CLI/session transport, not policy code and not the
post-push stability recipe. Re-auth/recreate the Colab session, then rerun the
preferred command from the recipe artifact.

## Safety

- robot_touched: `False`
- ssh_used: `False`
- deploy_performed: `False`
- training_started: `False`
- grounded_replay: `False`
