# Phase 2 Swing Geometry / Contact-Timing Next Recipe

status: `PRE_REGISTERED_NOT_STARTED`

## Why

The right-swing structural, phase-lift, and phase-advance branches all held in
the same way:

```text
candidate stays upright
candidate usually satisfies local terrain swing subchecks
mean vx remains near 0.020 m/s at x=0.08
mean track ratio remains near 0.25
double support remains near 85%
some seeds still exceed corrected per-joint max target velocity
```

The phase-advance branch specifically showed that moving the swing reward window
3 ticks earlier does not create robust forward walking. The next branch should
therefore change the gait strategy instead of adding another scalar lift/rate
penalty around the same short double-support-dominant pattern.

## Guardrails

- Offline only. No robot, SSH, deploy, grounded replay, or runtime behavior
  changes.
- Warm-start from the corrected-bridge Phase 1/Phase 2 candidate lineage.
- Keep the corrected actuator bridge canonical:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`.
- Keep the deployed policy contract: `obs[1,101] -> actions[1,14]`.
- Do not change runtime phase timing or policy action ordering.
- Do not promote any candidate unless it clears the corrected-bridge x=0.08 and
  x=0.0 gates.

## Branch Decision

Prioritize a geometry/contact-pattern change:

1. Add a default-off right-swing geometry term that encourages a knee-bend-first
   swing shape during the phase-commanded right swing, while continuing to gate
   against the corrected right pitch-chain envelope.
2. Pair it with contact-transition/single-support shaping only as needed to
   reduce double-support dwell.
3. Reject the branch if it raises corrected-envelope max target-velocity excess
   or keeps mean track ratio near the current `0.25` plateau.

If this branch also preserves the `~85%` double-support pattern, stop the scalar
reward path and pivot to the pre-registered live-oracle/phase-aware student
path. The feed-forward reward-shaped policy is then preserving the wrong contact
mode rather than lacking one more local swing cost.

## Acceptance Gate

Run the standard corrected-bridge terrain gate:

```text
task: rough_terrain_backlash
command_x: 0.08
terrain_hfield_z_scale: 0.0024
bridge: fitted corrected-knee bridge
seeds: 0-7
duration: 15 s
terrain swing subchecks enabled
```

Promotion requires:

```text
PASS_CANDIDATE_SIM_GATE 8/8
falls 0/8
duration_complete 8/8
corrected-envelope max target-velocity excess 0 on every seed
mean track ratio > Phase 1 terrain plateau, not merely ~= 0.25
double-support dwell materially reduced from ~= 85%
```
