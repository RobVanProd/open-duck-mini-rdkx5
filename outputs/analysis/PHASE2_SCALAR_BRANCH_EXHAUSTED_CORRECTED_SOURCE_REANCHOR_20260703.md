# Phase 2 Scalar Branch Exhausted / Corrected Source Re-Anchor

status: `PASS_CORRECTED_SOURCE_REANCHOR_READY`

## Summary

The `z=0.0026` scalar continuation branch is closed as exhausted for the
current Phase 2 goal. The reduced A100 `ss8` run proved the runtime profile can
export, but its exported policy moved in the wrong direction: over-envelope
target rates and early falls.

A clean corrected-bridge `z=0.0026` / `home-support` source trace was then
re-established from the Phase 1 rate-limited candidate. That source is stable
for positive command across all 8 seeds and is now the correct parent for the
next live-oracle student branch.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed.

## Closed Branch

Closed branch:

```text
PHASE2_HOME_RESET_Z0026_PHASE_SINGLE_SUPPORT
```

Evidence:

- `outputs/analysis/PHASE2_SS8_20480_A100_GATE_RESULT_20260703.md`
- A100 export succeeded at `20480` steps with `8` envs / batch `64`.
- Exported ONNX sha256:
  `8ec14fa7a8b47fc4c01cdc2b49207308216c51d0ef5774f0f190e889db9f0458`
- Corrected CPU gate result:
  `HOLD_SS8_20480_OVER_ENVELOPE_FALL`
- `8/8` seeds fell or terminated at `187` samples.
- mean local vx: `0.1089 m/s`
- track ratio: `1.3617`
- max pitch-chain p95 velocity: `5.2400 rad/s`
- corrected p95 velocity excess: `2.9900 rad/s`
- corrected max velocity excess: `3.2400 rad/s`
- double support: `92.5134%`

Interpretation:

The scalar phase/single-support pressure recovered aggressive motion, not the
Phase 2 target. More timesteps on this exact recipe are not authorized because
the early export already left the corrected actuator envelope and fell.

## Corrected Source Re-Anchor

Source policy:

```text
policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
```

Source trace:

```text
outputs/analysis/PHASE2_PHASE1_RATE175_Z0026_X008_SOURCE_TRACE.md
outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace.json
```

Conditions:

- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain hfield z-scale: `0.0026`
- reset mode: `home-support`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge mode: `fitted`
- platform: CPU JAX
- seeds: `0..7`
- trace full observations: enabled

Result:

- `8/8` seeds completed `750` samples.
- falls: `0/8`
- mean local vx: `0.0330 m/s`
- track ratio: `0.4130`
- max pitch-chain p95 velocity: `1.7269 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0190 rad/s`
- max tracking p95: `0.1859 rad`
- single support: `27.7333%`
- double support: `72.2667%`

This is not a deployable promotion result because the strict gate still reports
`HOLD_CANDIDATE_TARGET_VELOCITY` from the small instantaneous max excess.
It is, however, a clean corrected source for offline distillation: stable,
positive-command, full-observation, in-envelope at p95, and aligned to the
current `z=0.0026` / `home-support` convention.

## Source Manifest

Manifest:

```text
outputs/analysis/PHASE2_PHASE1_RATE175_Z0026_X008_SOURCE_MANIFEST.md
outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json
```

Manifest status: `PASS_BC_TRACE_MANIFEST_READY`

- dataset id: `0d4c2e82ef0ff64e`
- entries: `8`
- samples: `6000`
- bc-ready entries: `8`

This replaces the mixed `z=0.0024` source plus failed seed-5 relabel aggregate
as the preferred parent for the next corrected `z=0.0026` live-oracle branch.

## Tooling Fix

`tools/run_live_oracle_dagger_iteration.py` now accepts and reports:

```text
--reset-mode playground|home-support
```

and forwards non-default reset mode to `tools/run_candidate_seed_sweep.py`.
This prevents future live-oracle data collection from silently using the wrong
reset convention while the Phase 2 gate uses `home-support`.

Dry-run plan:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_plan/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_plan/live_oracle_dagger_iteration.json
```

Dry-run status: `PASS_LIVE_ORACLE_DAGGER_ITERATION_DRY_RUN`

## Next Authorized Branch

Next branch:

```text
PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_STUDENT
```

Allowed first step:

1. Run the dry-run live-oracle iteration plan against the corrected source
   manifest with `rough_terrain_backlash`, `z=0.0026`, and `home-support`.
2. Fit the smallest deployable student that can preserve the corrected source:
   start with phase/contact-conditioned or frame-stacked feed-forward before
   escalating to recurrent hidden state.
3. Gate on the canonical corrected bridge at both `x=0.08` and `x=0.0`.

Do not return to scalar reward-only A100 continuation unless a new
pre-registered branch explains why it is not part of the closed over-envelope
failure family.

## CI Note

Latest GitHub `Validate` failure for commit `6002658` still has no actionable
test logs:

- run: `28646260762`
- job: `84953473452`
- job steps: `[]`
- `gh run view --log`: `log not found`
- job log API: blob missing / HTTP 404

Treat the validation emails as a GitHub Actions runner/allocation failure
unless a later run produces actual failing step logs.
