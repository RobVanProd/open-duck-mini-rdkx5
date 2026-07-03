# Phase 2 Home-Reset z0.0026 Phase/Single-Support Next Recipe

status: `PRE_REGISTERED_NOT_STARTED`

## Summary

The previous A100 rate-cap continuation is closed as
`HOLD_RATECAP_A100_NOT_PROMOTABLE`. It did not find the middle between freezing
and over-envelope motion:

- `40960`: low progress, 100% double support, in envelope.
- `81920`: forward motion only by falling and exceeding the corrected envelope.
- `122880`: low progress, mostly double support, still over envelope.

Do not repeat a scalar rate-cap continuation. The next offline branch should
target the remaining mechanism directly: commanded phase swing must turn into
single-support foot lift/advance while preserving the corrected per-joint
pitch-chain limits.

This is not a re-run of the closed `PHASE2_RIGHT_SWING_PHASE_ADVANCE` branch.
That branch ran at `z=0.0024` and held near `0.020 m/s`. This recipe is anchored
to the current corrected `z=0.0026` home-support reset gate and combines
phase-primary lift timing, explicit phase single-support shaping, and corrected
per-joint pitch-chain rate limits across both legs.

No robot test, SSH, deploy, grounded replay, or runtime behavior change is in
scope.

## Locked Inputs

- Warm-start checkpoint:
  `outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- Corrected actuator bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Corrected bridge sha256:
  `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- Task:
  `rough_terrain_backlash`
- Terrain:
  `z=0.0026`
- Reset/eval convention:
  `home-support`
- Command gate:
  `x=0.08`, plus `x=0.0` command-preservation gate before promotion.

## Corrected Pitch-Chain Envelope

Use the corrected per-joint limits, not the old global `3.75 rad/s` threshold:

| action index | joint | limit rad/s |
|---:|---|---:|
| 2 | `left_hip_pitch` | 2.50 |
| 3 | `left_knee` | 3.25 |
| 4 | `left_ankle` | 2.75 |
| 11 | `right_hip_pitch` | 2.25 |
| 12 | `right_knee` | 2.75 |
| 13 | `right_ankle` | 2.00 |

## Hypothesis

The rate-cap run confirms that global smoothing trades away swing/transition
behavior. The candidate needs phase-aware contact-pattern pressure:

1. Advance phase-primary swing lift by the fitted 3-tick bridge delay so the
   affordable left-side lift lands inside the useful swing window.
2. Penalize phase-commanded swing contact and stance no-contact directly so the
   policy cannot satisfy the objective by staying in double support.
3. Keep a hard corrected per-joint swing-rate cost on both pitch chains so the
   right leg cannot buy clearance by exceeding its tighter knee/ankle envelope.

## Training Recipe

Preferred Colab workflow:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-phase2-singlesupport \
  --workflow phase2-right-swing-phase-single-support \
  --run \
  --timeout-s 14400 \
  --candidate-timeout-s 14400 \
  --poll-interval-s 120 \
  --idle-no-sentinel-polls 6 \
  --remote-artifact-interval-s 300 \
  --artifact-checkpoint-mode latest \
  --candidate-name phase2_home_reset_z0026_phase_single_support_from_rate175_a100 \
  --phase2-num-timesteps 122880 \
  --phase2-restore-checkpoint-path outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint \
  --phase2-terrain-hfield-z-scale 0.0026 \
  --phase2-target-rate-scale -0.02 \
  --phase2-actuator-tracking-scale -0.01 \
  --phase2-forward-swing-target-rate-limit-scale -0.04 \
  --phase2-forward-swing-target-rate-limit-joint-indices 2,3,4,11,12,13 \
  --phase2-forward-swing-target-rate-limit-values 2.5,3.25,2.75,2.25,2.75,2.0 \
  --phase2-forward-swing-target-rate-limit-huber-delta 0.05 \
  --phase2-skip-post-training-gates \
  --phase2-final-training-args-json '[
    "--restore-policy-kl-scale", "8",
    "--forward-swing-phase-advance-ticks", "3",
    "--forward-phase-single-support-scale", "-0.004",
    "--forward-phase-single-support-swing-contact-weight", "1.0",
    "--forward-phase-single-support-stance-no-contact-weight", "2.0",
    "--forward-phase-swing-lift-scale", "-0.0006",
    "--forward-phase-swing-lift-target-m", "0.012",
    "--forward-phase-swing-lift-huber-delta", "0.003",
    "--reset-base-xy-jitter-m", "0",
    "--reset-yaw-jitter-rad", "0",
    "--reset-actuator-qpos-multiplier-min", "1",
    "--reset-actuator-qpos-multiplier-max", "1",
    "--reset-base-qvel-jitter", "0"
  ]'
```

The workflow's default right-side rate-limit flags are intentionally overridden
by the explicit both-leg pitch-chain values above. The wrapper appends duplicate
argparse options and the final value is the one used by the training runner.

Use detached Colab execution, not `--exec-remote`, because the last
`--exec-remote` run produced a transport artifact without checkpoints.

## Acceptance Gate

Downloaded checkpoints must be screened locally with the canonical corrected
bridge and home-support reset:

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py \
  --policies <checkpoint-list> \
  --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --duration 15 \
  --bridge-mode fitted \
  --task rough_terrain_backlash \
  --jax-platform cpu \
  --trace-full-obs \
  --run \
  --terrain-hfield-z-scale 0.0026 \
  --reset-mode home-support \
  --command-x 0.08 \
  --seeds 0,1,2,3,4,5,6,7
```

Promotion requires all of:

- `x=0.08`: 8/8 duration complete.
- `x=0.08`: zero corrected per-joint pitch-chain p95 velocity excess.
- `x=0.08`: command tracking is not lower than the Phase 1 slow-walk baseline
  class; low-progress double-support policies are holds.
- `x=0.08`: single-support and swing metrics improve over the rate-cap hold.
- `x=0.0`: 8/8 duration complete with command semantics preserved before any
  robot consideration.

## Falsifiers

- `HOLD_DOUBLE_SUPPORT_FREEZE`: duration complete but track ratio stays near
  `0.1-0.2` and double support remains dominant.
- `HOLD_RIGHT_STRUCTURAL_OVER_ENVELOPE`: right pitch-chain p95 velocity excess
  persists despite the corrected per-joint rate cost.
- `HOLD_FALL_OR_TERMINATION`: contact-pattern pressure restores movement only
  by destabilizing the body.
- `HOLD_SCALAR_BRANCH_EXHAUSTED`: result matches the closed phase-lift /
  phase-advance / rate-cap failure family. Next branch must change the policy
  representation or target manifold, not add another scalar reward term.

## CI Note

GitHub `Validate` is currently failing before any workflow steps execute:
latest job `84940771764` has `runner_id: 0`, empty `runner_name`, `steps: []`,
and `gh run view --log` returns `log not found`. The local equivalent static
checks pass. Treat the email notifications as a GitHub Actions runner/allocation
issue unless a later run produces actionable logs.
