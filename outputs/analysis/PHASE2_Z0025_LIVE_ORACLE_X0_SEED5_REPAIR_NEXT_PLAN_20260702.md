# Phase 2 z=0.0025 Live-Oracle x0 Seed5 Repair Next Plan

status: `PLAN_Z0025_X0_SEED5_SOFTZERO_LIVE_ORACLE_REPAIR`

This is an offline planning artifact. It does not authorize robot tests, SSH,
deployment, grounded replay, runtime behavior changes, or another scalar PPO
reward run.

## Current Evidence

The z=0.00245 A100 motion-recovery retry completed training on the pinned
Colab/A100 stack, but all exported checkpoints held for low forward progress in
the compact corrected-bridge sweep. The best partial checkpoint remained
in-envelope but reached only:

```text
track_ratio: 0.2339
mean_vx:     0.0187 m/s
```

Artifact:

```text
outputs/analysis/PHASE2_Z00245_MOTION_RECOVERY_A100_RESULT_20260702.md
```

This closes the small scalar-progress-pressure path for now.

The strongest current z=0.0025 positive-motion source is:

```text
outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx
sha256: f00ba8a89f4e24e7c393309acd434cbc95132473aa3df562dacf4fe527049822
```

It passed the full corrected-bridge `x=0.08`, `z=0.0025` gate:

```text
seeds passed:             8/8
falls:                    0/8
mean track ratio:         0.3742
mean local vx:            0.0299 m/s
max sent velocity p95:    1.9065-1.9234 rad/s
max tracking p95:         0.1917-0.1953 rad
velocity excess:          0.0000
```

It held at `x=0.0` because seed 5 collapsed:

```text
x=0.0 seeds passed:       7/8
failing seed:             5
failing samples:          43
failing mean local vx:    -0.3468 m/s
base height min:          0.0575 m
velocity excess:          0.0000
```

Artifact:

```text
outputs/analysis/PHASE2_Z0025_BOUNDARY_RATE1P9_FULL_GATE_DECISION_20260702.md
```

## Decision

Use the z=0.0025 rate1p9 candidate as the parent/source for a bounded
zero-command seed-5 repair branch. Do not promote it until the full `x=0.0`
gate and the full `x=0.08` gate both pass.

The repair should use live-oracle DAgger with softened zero-command relabeling,
not another scalar progress-pressure A100 run.

## Repair Hypothesis

Earlier hard zero-action relabeling fixed most zero-command drift but created a
seed-specific collapse pocket. The next repair should keep the useful
command-aware zero-command correction while reducing the abrupt control/posture
discontinuity on seed 5.

Primary knob:

```text
--x0-zero-action-alpha < 1.0
```

Start with a bounded soft-zero setting, then gate seed 5 before scaling.

## Planned Dry-Run Command

```bash
python3 tools/run_live_oracle_dagger_iteration.py \
  --student-policy outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx \
  --teacher-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json \
  --base-manifest outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json \
  --iteration 2 \
  --rung z0025_x0_seed5_softzero_repair \
  --output-dir outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2 \
  --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 15 \
  --x008-seeds 0-7 \
  --x0-seeds 5 \
  --bridge-mode fitted \
  --task rough_terrain_backlash \
  --terrain-hfield-z-scale 0.0025 \
  --jax-platform cpu \
  --teacher-model-kind source_vx_blend \
  --x0-teacher-model-kind zero_action \
  --x0-zero-action-alpha 0.50 \
  --gate-aware-sample-weights
```

This command only plans the live-oracle data iteration unless `--run` is added.
It does not fit a final student and does not produce a promotable candidate.

## Required Gates Before Any Promotion

Immediate repair gate:

```text
z=0.0025, x=0.0, seed 5, corrected bridge, short duration
fall: none
mean |vx|: near zero
velocity excess: 0.0000
```

Full gates after the short repair gate:

```text
z=0.0025, x=0.0, seeds 0-7, corrected bridge, 15s
z=0.0025, x=0.08, seeds 0-7, corrected bridge, 15s
```

Promotion remains blocked unless both pass with command conditioning preserved:
the policy must stay still at `x=0.0` and keep moving at `x=0.08` without
corrected-envelope velocity excess.

## Do Not Do Next

- Do not repeat another small scalar progress-pressure run.
- Do not promote the rate1p9 candidate as-is.
- Do not use robot validation for this branch.
- Do not run push or higher-terrain scaling until zero-command seed 5 is fixed.
