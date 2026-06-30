# Phase 2 z0.002 vs z0.0035 Compact Sweep Decision

Status: `HOLD_TERRAIN_HEIGHT_LOSSES_FORWARD_PROGRESS`

## Scope

Offline sim only. No robot, SSH, deploy, grounded replay, or runtime behavior change was
performed.

This comparison re-ran selected z0.002 terrain policies through the same compact
post-training sweep used for the z0.0035 motion-floor run:

```text
commands: 0.0, 0.08
duration: 1.0 s
bridge: corrected fitted actuator bridge
platform: CPU closed-loop eval
velocity envelope: 2.0-3.25 rad/s
min promote vx: 0.020 m/s
min promote ratio: 0.25
```

The purpose was to separate two possibilities after the z0.0035 hold:

1. the compact post-training sweep is stricter than earlier z0.002 screens, or
2. increasing terrain from z0.002 to z0.0035 is eroding forward motion.

## z0.002 Reference Sweep

Artifact:

```text
outputs/analysis/phase2_z002_reference_compact_sweep/
```

| policy | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 mean vx | max pitch vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `phase2_stage_a2_gain099_20260628_candidate` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | 0.2504 | 0.0200 | 1.5581 | 0.2194 |
| `stage_c0_terrain_z002_preserve_from_a2_gpu/245760` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | 0.3087 | 0.0247 | 1.4865 | 0.2188 |
| `stage_c2_terrain_z002_targetrate_from_c1_gpu/163840` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_TRACKING` | 0.2981 | 0.0238 | 1.4829 | 0.2201 |
| `stage_c7_terrain_z002_gate_selected_from_c3_gpu/35120` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1491 | 0.0119 | 1.3611 | 0.2079 |

The z0.002 C0/C2 policies still produce meaningful x=0.08 motion under the compact sweep,
but hold on the strict tracking threshold.

## z0.0035 Motion-Floor Sweep

Artifact:

```text
outputs/analysis/phase2_z0035_motion_floor_local_sweep/
```

| checkpoint | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 mean vx | max pitch vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1615 | 0.0129 | 1.4383 | 0.2129 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1613 | 0.0129 | 1.4444 | 0.2140 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1671 | 0.0134 | 1.4431 | 0.2132 |

## Interpretation

The compact sweep is strict, but it does not explain the z0.0035 hold by itself:

- z0.002 C0/C2 retain x=0.08 motion: track ratio `0.298-0.309`, mean vx `0.0238-0.0247 m/s`.
- z0.0035 drops to low forward progress: track ratio `0.161-0.167`, mean vx `0.0129-0.0134 m/s`.
- Both are below the corrected measured velocity envelope.
- Neither failure is caused by action saturation or velocity excess.

The terrain-height increase from z0.002 to z0.0035 is eroding forward motion before it
creates an over-envelope actuator problem. The z0.0035 motion-floor run is therefore not a
good parent for further terrain escalation.

## Decision

Do not escalate to z0.005 from the z0.0035 motion-floor recipe.

The next aligned training move is to return to the z0.002 moving parent, preferably C0 or
C2, and recover the strict tracking margin without sacrificing the measured forward motion.
After that, reintroduce terrain height in a smaller ramp than z0.002 -> z0.0035, or use a
curriculum that starts from the moving z0.002 checkpoint and only advances when both motion
and tracking pass the compact sweep.

Robot validation remains blocked.
