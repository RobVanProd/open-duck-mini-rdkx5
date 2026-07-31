# Phase 2 Health-Routed Parent Decision

status: `HOLD_STATIC_PARENT_NOT_READY`

## Summary

The health-gated router remains the best compact z=0.0075 rough+push behavior source, but the route has not yet been compressed into a single static deployable parent that clears the compact gate.

Inputs:

- routed trace manifest: `outputs/analysis/phase2_health_routed_parent_manifest.json`
- PPO-loc BC parent: `outputs/analysis/phase2_health_routed_parent_ppo_loc/candidate.onnx`
- phase-modulated BC parent: `outputs/analysis/phase2_health_routed_parent_phase_modulated/candidate.onnx`

## Evidence

### Routed Manifest

- status: `PASS_BC_TRACE_MANIFEST_READY`
- samples: `3750`
- source traces: selected health-routed branches from Iter24/Iter25 over seeds `0,1,2,6,7`
- dataset id: `70e54aa35a944114`

### PPO-Loc Parent

- fit status: `PASS_PPO_LOC_BC_FIT_SMOKE`
- p95 abs action error: `0.006637`
- ONNX p95 abs error: `0.00000016`
- compact gate: `1/5` pass
- decision: not promotable

### Phase-Modulated Parent

- fit status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- context indices: `6,99,100`
- p95 abs action error: `0.009091`
- ONNX p95 abs error: `0.00000012`
- compact gate: `4/5` pass
- passing seeds: `0,1,2,6`
- failing seed: `7`
- seed 7 failure: `HOLD_CANDIDATE_FALL_OR_TERMINATION` at `300` samples, mean local vx `-0.0419 m/s`, track ratio `-0.5236`, base height min `0.0673 m`

## Decision

The phase-modulated parent is the best static compression attempt so far, but it is not a valid Phase 2 DR warm start because the compact gate requires all selected seeds to survive. Do not launch long domain-randomized training from this parent.

The result narrows the next branch:

- phase/context conditioning helps preserve the routed behavior,
- pure static BC still leaves a seed-specific closed-loop failure,
- the next step should be live closed-loop correction or memory/state, not broad DR.

Recommended next branch:

```text
LIVE_ORACLE_DAGGER_PHASE_STUDENT
```

Use the phase-modulated parent as a strong initialization, then collect live student rollouts and query the selector oracle on the student's own visited states. If live DAgger still leaves seed 7 or equivalent failures, escalate to frame-stack or recurrent state.

Robot validation, SSH, deploy, grounded replay, and Phase 2 DR remain blocked.
