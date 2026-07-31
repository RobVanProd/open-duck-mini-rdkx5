# Phase 2 Stage C Terrain Clearance Instrumentation

status: `PASS_CLEARANCE_METRICS_ADDED`

## Scope

Offline sim instrumentation only. No robot, SSH, deploy, grounded replay, or
runtime behavior change was performed.

This patch adds passive reporting to the closed-loop evaluator:

- per-foot contact percentage
- per-foot swing samples
- per-foot swing site height
- per-foot swing lift over the median stance-site height
- per-foot swing peak lift
- no-contact / single-support / double-support percentages
- support transition count

The evaluator already recorded `foot_site_pos_m` and `foot_contacts`; this
change only summarizes those existing records in JSON and markdown reports.
It does not change policy stepping, reward, gates, actuator bridge behavior, or
training behavior.

## Focused Terrain Screen

Command:

```text
tools/run_candidate_seed_sweep.py
  --task rough_terrain_backlash
  --terrain-hfield-z-scale 0.002
  --command-x 0.08
  --seeds 0
  --duration 5
  --bridge-mode fitted
```

Compared policies:

```text
a2_gain099:
  policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx

c0_245760:
  outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760.onnx

c2_163840:
  outputs/phase2_domain_randomization/stage_c2_terrain_z002_targetrate_from_c1_gpu/smoke_20260628T113221Z_gpu/2026_06_28_073829_163840.onnx
```

Report:

```text
outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_CLEARANCE_SCREEN_CPU.md
outputs/analysis/phase2_stage_c_terrain_z002_clearance_screen_cpu.json
```

## Result

All three policies stayed upright and inside the corrected velocity envelope,
but all remained strict tracking holds on seed 0:

| policy | tracking p95 | track ratio | min swing peak | single support | double support |
|---|---:|---:|---:|---:|---:|
| `a2_gain099` | 0.2079 | 0.3560 | 0.0153 m | 17.6% | 82.4% |
| `c0_245760` | 0.2040 | 0.3758 | 0.0159 m | 16.8% | 83.2% |
| `c2_163840` | 0.2044 | 0.3866 | 0.0163 m | 17.2% | 82.8% |

Per-foot details:

```text
a2_gain099:
  left contact: 94.0%, swing samples: 15, peak lift: 0.0199 m
  right contact: 88.4%, swing samples: 29, peak lift: 0.0153 m

c0_245760:
  left contact: 95.6%, swing samples: 11, peak lift: 0.0197 m
  right contact: 87.6%, swing samples: 31, peak lift: 0.0159 m

c2_163840:
  left contact: 94.8%, swing samples: 13, peak lift: 0.0198 m
  right contact: 88.0%, swing samples: 30, peak lift: 0.0163 m
```

## Interpretation

The terrain failure is consistent with a low-clearance shuffle:

- the robot spends about `82-83%` of the screen in double support,
- there is no no-contact phase,
- single support is only about `17%`,
- the minimum per-foot swing peak is only about `1.5-1.6 cm`,
- and the left foot is in contact about `95%` of the time.

This aligns with the hardware observation on carpet: the gait appears to step
but does not lift the foot enough to walk forward reliably on a higher-friction
or deformable surface.

The next Stage C training objective should explicitly increase swing clearance
and reduce double-support dwell while preserving:

- corrected velocity-envelope compliance,
- no falls,
- command-conditioned forward motion,
- and the strict `0.20 rad` pitch-chain tracking gate.
