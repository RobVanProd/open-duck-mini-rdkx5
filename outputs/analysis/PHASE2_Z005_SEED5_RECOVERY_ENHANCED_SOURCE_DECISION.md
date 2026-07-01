# Phase 2 z=0.005 Seed-5 Recovery Enhanced Source Decision

status: `HOLD_SAME_TICK_NEIGHBOR_RECOVERY_NOT_SUFFICIENT`

This is an offline source-curation and student-gate decision. It did not run
robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior
changes.

## Source Curation

The failed z=0.005 seed-5 support state was relabeled with same-tick actions
from z=0.005 seeds that completed, using a conservative pitch-chain target-rate
cap:

- relabel artifact: `outputs/analysis/PHASE2_Z005_SEED5_SAME_TICK_NEIGHBOR_RECOVERY_RELABEL.md`
- recovery dataset id: `5a3293ce22249030`
- recovery samples: `56`
- recovery manifest id: `4d118a243c80f01c`
- enhanced source manifest: `outputs/analysis/phase2_z005_seed5_recovery_enhanced_source_manifest.json`
- enhanced source dataset id: `a64787a6669df71d`
- enhanced source entries: `11`

The enhanced source combines:

- corrected z=0.0024 passing terrain source traces,
- x=0 command-preservation rows,
- the targeted z=0.005 seed-5 neighbor recovery trace.

It intentionally does not carry the full failed z=0.005 relabel batch forward.

## Student Fit

- student: phase/command-modulated feed-forward BC
- ONNX: `outputs/analysis/phase2_z005_seed5_recovery_enhanced_phase_mod_bc_candidate/candidate.onnx`
- fit report: `outputs/analysis/PHASE2_Z005_SEED5_RECOVERY_ENHANCED_PHASE_MOD_BC_STUDENT.md`
- gate report: `outputs/analysis/PHASE2_Z005_SEED5_RECOVERY_ENHANCED_PHASE_MOD_GATE_X008.md`

## z=0.005 x=0.08 Gate

| metric | value |
|---|---:|
| pass seeds | 0 / 8 |
| falls | 2 / 8 |
| duration complete | 6 / 8 |
| mean track ratio | -0.5756 |
| mean vx | -0.0460 m/s |
| p95 velocity excess mean | 0.0000 rad/s |
| max velocity excess mean | 0.1783 rad/s |
| max pitch vel p95 | 2.0359 rad/s |
| single support mean | 19.32% |
| double support mean | 79.94% |

Seed 5 still falls at `52` samples. Seed 3 now also falls at `74` samples. The
surviving seeds are stable but under-progressing, with track ratios roughly
`0.30-0.37`.

## Decision

Do not promote this ONNX. Do not use this same-tick neighbor recovery as the
next source oracle.

The targeted seed-5 recovery row did not change the failed support state enough
to survive z=0.005, and it introduced another early fall. The next source must
be generated from a closed-loop controller or policy that actually survives
z=0.005 with useful support transfer, not from same-tick averaging of nearby
seeds.

Recommended next branch:

1. stop same-tick neighbor recovery relabeling for seed 5;
2. build a z=0.005 source that is validated before distillation, with explicit
   support/base-height/forward-progress gates;
3. only resume live-oracle DAgger after the source itself survives the z=0.005
   support state.
