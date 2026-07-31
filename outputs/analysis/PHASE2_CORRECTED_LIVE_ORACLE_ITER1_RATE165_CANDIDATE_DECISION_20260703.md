# Phase 2 Corrected Live-Oracle Iter1 Rate165 Candidate Decision

status: `PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY`

## Summary

The corrected live-oracle iteration-1 rate-limited phase/contact student clears
both canonical offline gates under the corrected actuator bridge:

- `x=0.08`: `8/8` pass.
- `x=0.0`: `8/8` pass.

This is the first Phase 2 candidate in this branch that preserves
command-conditioned forward motion while staying fully inside the corrected
per-joint actuator envelope at both p95 and max checks. It is slower than the
Phase 1 source, but it is clean under the corrected `z=0.0026` / `home-support`
gate.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed.

## Candidate

Promoted candidate directory:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703
```

Files:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate_mlp.npz
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/SHA256SUMS
```

Hashes:

- ONNX:
  `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
- NPZ:
  `2a896d32b9e40565008073970cacc9d31c8543e5ee8f3ee44162c5ddcd73ed36`

## Training Lineage

Corrected source:

```text
outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json
```

Live-oracle iteration 0:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/live_oracle_dagger_aggregate_manifest.json
```

Iteration-0 phase/contact student held for low progress:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER0_PHASE_CONTACT_DECISION_20260703.md
```

Live-oracle iteration 1:

```text
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_run/live_oracle_dagger_aggregate_manifest.json
```

Iteration-1 regular phase/contact student recovered motion but held for
instantaneous max velocity excess:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER1_PHASE_CONTACT_X008_GATE.md
```

The rate165 refit removed the instantaneous excess while preserving enough
motion to pass.

## Fit Metrics

Fit artifact:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER1_PHASE_CONTACT_RATE165_STUDENT.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_student.json
```

- samples: `21000`
- context indices: `[6, 97, 98, 99, 100]`
- p95 action error: `0.017565`
- target-rate p95: `1.423530 rad/s`
- target-rate max: `1.957195 rad/s`
- ONNX p95 abs error: `0.00000012`
- ONNX max abs error: `0.00000024`

## x=0.08 Corrected Gate

Gate artifact:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER1_PHASE_CONTACT_RATE165_X008_GATE.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x008_gate.json
```

Conditions:

- task: `rough_terrain_backlash`
- terrain hfield z-scale: `0.0026`
- reset mode: `home-support`
- bridge: corrected fitted bridge
- seeds: `0..7`
- duration: `15 s`

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- `8/8` duration complete
- falls: `0/8`
- mean local vx: `0.0272 m/s`
- track ratio: `0.3400`
- body pitch p95: `0.1324 rad`
- base height min: `0.1523 m`
- max pitch-chain p95 velocity: `1.6410 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.1827 rad`
- single support: `22.5333%`
- double support: `77.4667%`

## x=0.0 Corrected Gate

Gate artifact:

```text
outputs/analysis/PHASE2_Z0026_CORRECTED_SOURCE_LIVE_ORACLE_ITER1_PHASE_CONTACT_RATE165_X0_GATE.md
outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x0_gate.json
```

Result:

- status: `PASS_CANDIDATE_SIM_GATE`
- `8/8` duration complete
- falls: `0/8`
- mean local vx: approximately `0.0000 m/s`
- body pitch p95: `0.0118 rad`
- base height min: `0.1523 m`
- max pitch-chain p95 velocity: `0.0642 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.0000 rad/s`
- max tracking p95: `0.0317 rad`

## Interpretation

The live-oracle loop recovered the deployable behavior that the first
phase/contact student attenuated:

| metric | source parent | iter0 student | iter1 rate165 |
|---|---:|---:|---:|
| x=0.08 pass seeds | `0/8 strict` | `0/8` | `8/8` |
| duration complete | `8/8` | `8/8` | `8/8` |
| track ratio | `0.4130` | `0.1326` | `0.3400` |
| mean vx | `0.0330` | `0.0106` | `0.0272` |
| max vel excess | `0.0190` | `0.0000` | `0.0000` |
| max tracking p95 | `0.1859` | `0.1642` | `0.1827` |
| single support | `27.7333%` | `8.8000%` | `22.5333%` |

This candidate is offline-ready for review. Robot validation is still a
separate operator-approved step and should not be inferred from this artifact.
