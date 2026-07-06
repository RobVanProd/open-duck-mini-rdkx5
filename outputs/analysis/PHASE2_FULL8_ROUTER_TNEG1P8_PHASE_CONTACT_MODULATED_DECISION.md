# Phase 2 Full-8 Router Phase/Contact-Modulated Conversion Decision

status: `HOLD_PHASE_CONTACT_MODULATED_COMPRESSION_NOT_PROMOTABLE`

Offline conversion and corrected-bridge gate only. No robot tests, SSH,
deploy, grounded replay, runtime behavior changes, or domain-randomized PPO
training were performed.

## Source

- source router: `policy/candidates/phase2_full8_router_tneg1p8_20260705/candidate.onnx`
- source router sha256: `f3e88820b87025788c97636599cd2caf6ef249f7cb7e50ddde31ff5c1c5457d0`
- source status: `PASS_PHASE2_ROUTER_WARMSTART_SIM_GATE`
- source x=0.08 gate: `8/8` duration complete, falls `0`, velocity excess max `0.0000`
- source x=0.0 gate: `8/8` duration complete, falls `0`, velocity excess max `0.0000`

## Student

- architecture: shared-trunk BC student with command/contact/phase modulation
- manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest_seed56_weighted.json`
- samples: `12000`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[128, 64]`
- modulation scale: `0.75`
- ONNX: `outputs/analysis/phase2_full8_router_tneg1p8_phase_contact_modulated_student/candidate.onnx`
- ONNX sha256: `bf13b86c9aafa66b1c66a509a26115bad56e1f1e7c6b56d6670321a77e09a195`
- NPZ sha256: `054df1573e60a2382d503ced614f65df0d0e3306a440e0c3cf71894f2b03061d`

## Fit Smoke

Artifact:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_PHASE_CONTACT_MODULATED_STUDENT.md
outputs/analysis/phase2_full8_router_tneg1p8_phase_contact_modulated_student.json
```

Result:

```text
fit status: PASS_PHASE_MODULATED_BC_FIT_SMOKE
MAE: 0.002042
p95 abs error: 0.006017
max abs error: 0.029472
target-rate p95: 1.259359 rad/s
target-rate max: 1.837669 rad/s
ONNX p95 abs error: 0.00000003
ONNX max abs error: 0.00000005
```

## Corrected-Bridge x=0.08 Gate

Artifact:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_PHASE_CONTACT_MODULATED_STUDENT_X008_GATE.md
outputs/analysis/phase2_full8_router_tneg1p8_phase_contact_modulated_student_x008_gate.json
```

Gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
bridge: corrected fitted actuator bridge
reset: home-support, settle 10 ticks
pushes: enabled, 0.075-0.125, every 1.0-1.5 s
seeds: 0-7
```

Result:

```text
duration complete: 3/8
falls: 5/8
failed seeds: 0, 3, 4, 5, 6
samples mean/min/max: 432.25 / 149 / 750
mean vx: 0.0755 m/s
mean track ratio: 0.9440
mean body pitch p95: 0.5017 rad
mean base height min: 0.0715 m
p95 velocity excess mean/max: 0.0000 / 0.0000 rad/s
max velocity excess mean/max: 0.1116 / 0.4199 rad/s
max tracking p95 mean/max: 0.1903 / 0.1987 rad
```

The phase/contact-modulated student lurches or collapses on most failing seeds.
It keeps p95 velocity excess at zero but does not preserve the router source's
closed-loop stability under the rough/push corrected-bridge gate.

## Decision

Do not launch domain-randomized PPO from this student. The x=0.08 gate already
disqualifies it, so the companion x=0.0 gate was intentionally skipped.

The promoted router remains the best offline source behavior, but this
phase/contact-modulated compression is not a trainable Phase 2 warm start.

recommended_next: `Use live-oracle DAgger or a genuinely stateful/branch-aware conversion from current-student rollouts; do not continue DR from this failed compression.`
