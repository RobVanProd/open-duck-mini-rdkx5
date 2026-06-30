# Phase 2 Right-Swing Phase-Lift Next Recipe

status: `PRE_REGISTERED_NOT_STARTED`
stage: `phase2_right_swing_phase_lift`

This is an offline planning artifact. It did not train, SSH, deploy, touch the
robot, or run grounded replay.

## Prior Result

- closed result: `docs/PHASE2_RIGHT_SWING_STRUCTURAL_RESULT.md`
- closed workflow: `phase2-right-swing-structural`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected bridge sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- warm start: `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- terrain: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0024`

The right-swing structural A100 run trained and exported cleanly, but none of
its checkpoints were promotable. All three checkpoints stayed upright for 8/8
seeds at x=0.08, but held on low forward progress and corrected-envelope
max-velocity excess. This closes another scalar rate-penalty sweep.

## Recipe Intent

The prior swing-clearance diagnostic used phase-primary segmentation because
foot-off is the outcome, not the window where lift should be generated. The
existing `forward_swing_clearance` cost is contact-primary: if a failing swing
stays planted, the cost mostly sees no successful swing segment to shape.

This recipe adds a default-off phase-primary lift signal:

- reward hook: `forward_phase_swing_lift`
- target lift: `0.012 m`
- scale: `-0.0006`
- pseudo-Huber delta: `0.003`
- segmentation: commanded swing phase, not contact break

The hook is intentionally small and does not relax the corrected per-joint
envelope gate. It is a test of whether planted right-swing failures need lift
signal earlier in the commanded swing window, not another attempt to smooth or
clip the policy into passing.

## Proposed Training Command

```bash
python3 \
  tools/run_actuator_bridge_training_smoke.py \
  --platform \
  gpu \
  --run \
  --task \
  rough_terrain_backlash \
  --restore-checkpoint-path \
  outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520 \
  --terrain-hfield-z-scale \
  0.0024 \
  --forward-wrong-direction-scale \
  -6 \
  --forward-wrong-direction-allowed-reverse-ratio \
  0.01 \
  --forward-swing-target-rate-limit-scale \
  -0.0025 \
  --forward-swing-target-rate-limit-joint-indices \
  11,12,13 \
  --forward-swing-target-rate-limit-values \
  2.25,2.75,2.00 \
  --forward-swing-target-rate-limit-huber-delta \
  0.05 \
  --forward-phase-swing-lift-scale \
  -0.0006 \
  --forward-phase-swing-lift-target-m \
  0.012 \
  --forward-phase-swing-lift-huber-delta \
  0.003 \
  --forward-swing-advance-scale \
  -0.001 \
  --forward-swing-advance-target-m \
  0.004 \
  --forward-swing-advance-huber-delta \
  0.002 \
  --forward-swing-clearance-scale \
  -0.00025 \
  --forward-swing-clearance-target-m \
  0.016 \
  --forward-swing-clearance-huber-delta \
  0.003
```

## Proposed Colab Workflow Command

```bash
python3 \
  tools/run_colab_cli_cuda_workflow.py \
  --workflow \
  phase2-right-swing-phase-lift \
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
- Forward progress improves over the right-swing structural run without falling.
- Right-leg swing diagnostic no longer reports blanket STRUCTURAL from R > 1.
- Any promoted candidate is exported, hashed, and re-gated with the canonical
  corrected bridge.

## Falsifiers

- If mean track ratio remains around `0.25` with 8/8 duration completion, the
  phase-primary lift signal did not restore forward progress.
- If max target-velocity excess persists, the policy is still buying lift by
  leaving the corrected envelope.
- If lift improves but progress does not, the next branch should change swing
  timing or knee-bend-first geometry, not add another scalar penalty.
- If the hook destabilizes the candidate, reject it and do not promote a
  smoke-only result.
