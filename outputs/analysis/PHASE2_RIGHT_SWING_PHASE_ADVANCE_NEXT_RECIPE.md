# Phase 2 Right-Swing Phase-Advance Next Recipe

status: `PRE_REGISTERED_NOT_STARTED`
stage: `phase2_right_swing_phase_advance`

This is an offline planning artifact. It did not train, SSH, deploy, touch the
robot, or run grounded replay.

## Prior Result

- closed result: `docs/PHASE2_RIGHT_SWING_PHASE_LIFT_RESULT.md`
- closed workflow: `phase2-right-swing-phase-lift`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected bridge sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- warm start: `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- terrain: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0024`

The phase-lift run trained and exported cleanly, but no checkpoint was
promotable:

```text
40960:  1/8 pass, mean track ratio 0.2514
81920:  3/8 pass, mean track ratio 0.2496
122880: 2/8 pass, mean track ratio 0.2590
```

## Diagnostic Input

- diagnostic:
  `outputs/analysis/phase2_right_swing_phase_lift_a100_20260630/phase2_right_swing_phase_lift_81920_swing_diagnostic.json`
- diagnostic sha256:
  `861b32a6d3ec465d1269a6517db3313a50e137de0a5c1d3663365bd4432cb7c0`
- aggregate verdict: `LATENCY_LIMITED`
- side verdicts: `{'left': 'LATENCY_LIMITED', 'right': 'LATENCY_LIMITED'}`
- side counts: `{'left': {'LATENCY_LIMITED': 8}, 'right': {'LATENCY_LIMITED': 5, 'STRUCTURAL': 3}}`
- rate drivers: `{'left_hip_pitch': 8, 'right_ankle': 7, 'right_knee': 1}`

Compared with the pre-phase-lift diagnostic, the old blanket right-leg
`R > 1` problem is mostly gone. The remaining pattern is planted swing windows
with affordable commanded rates, consistent with the corrected 3-tick actuator
delay pushing lift too late in the commanded swing phase.

## Hook

The Playground now exposes:

```text
reward_config.forward_swing_phase_advance_ticks
runner CLI: --forward_swing_phase_advance_ticks
RDK wrapper CLI: --forward-swing-phase-advance-ticks
```

Default is `0`, preserving existing behavior. This recipe sets it to `3` to
advance phase-primary swing-side masks by the measured actuator delay. It does
not change the corrected bridge, policy contract, or gate thresholds.

## Proposed Colab Workflow Command

```bash
python3 \
  tools/run_colab_cli_cuda_workflow.py \
  --workflow \
  phase2-right-swing-phase-advance \
  --run \
  --no-candidate-checkpoint-sweep \
  --phase2-skip-post-training-gates \
  --artifact-checkpoint-mode \
  all \
  --timeout-s \
  7200 \
  --no-poll
```

## Acceptance

- x=0.08 z=0.0024 corrected-bridge gate passes 8/8 seeds.
- x=0.0 corrected-bridge gate passes 8/8 seeds if x=0.08 passes.
- No corrected per-joint envelope excess in p95 or max target velocity.
- Planted percentage during phase-commanded swing drops in the rerun swing
  diagnostic without increasing rate utilization above corrected limits.
- Forward progress improves over the phase-lift run without falls.

## Falsifiers

- If mean track ratio remains around `0.25`, phase advance did not solve the
  low-progress mode.
- If max target-velocity excess increases, phase advance is moving illegal
  swing commands earlier instead of fixing timing.
- If planted swing does not decrease, latency is not the missing control knob.
- If the candidate becomes unstable, reject the recipe and return to swing
  duration or knee-bend-first geometry.
