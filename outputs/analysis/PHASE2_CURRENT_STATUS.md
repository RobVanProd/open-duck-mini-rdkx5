# Phase 2 Current Status

status: `HOLD_ITER2_MAX_VELOCITY_EXCESS`
generated_at: `2026-07-03T18:55:00Z`

## Scope

Offline-only Phase 2 robustness training status. This report does not
SSH, deploy, run robot tests, start training, or change runtime behavior.

## Corrected Rate165 Baseline

- candidate status: `PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY`
- candidate ONNX: `policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx`
- candidate ONNX sha256: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
- candidate NPZ sha256: `2a896d32b9e40565008073970cacc9d31c8543e5ee8f3ee44162c5ddcd73ed36`
- corrected decision artifact: `outputs/analysis/phase2_corrected_live_oracle_iter1_rate165_candidate_decision_20260703.json`

| gate | status | pass/total | x | z | vx mean | track ratio | single support | double support | max vel p95 | max tracking p95 | vel excess |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rate165_x008 | `PASS_GATE` | 8/8 | 0.080 | 0.0026 | 0.0272 | 0.3400 | 22.5333 | 77.4667 | 1.6410 | 0.1827 | 0.0000 |
| rate165_x0 | `PASS_GATE` | 8/8 | 0.000 | 0.0026 | -0.0000 | NA | 0.0000 | 100.0000 | 0.0642 | 0.0317 | 0.0000 |

## PPO-Compatible Warm-Start

- fidelity artifact: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_export_fidelity.json`
- status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- p95 abs error: `0.0000001192`
- max abs error: `0.0000002682`

## Failed PPO / Domain-Randomization Attempts

### Stage A A100 Narrow Flat

- status: `HOLD_STAGE_A_RATE165_STANDSTILL_REGRESSION`
- artifact: `outputs/analysis/phase2_stage_a_rate165_narrow_flat_result.json`
- final step: `4587520`
- final ONNX sha256: `7d83b2a24ca2874286d80eb27743fb5a5f498fa9ecb8bd1ad2effde7c0966982`
- x=0.08 gate: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- mean vx: `0.0007 m/s`
- track ratio: `0.0091`
- single support: `0.0000%`
- double support: `100.0000%`
- corrected velocity excess: `0.0000`

### Motion-Preservation CPU2240 Smoke

- status: `HOLD_MOTION_PRESERVE_STANDSTILL_REGRESSION`
- artifact: `outputs/analysis/phase2_rate165_motion_preserve_cpu2240_result.json`
- exported ONNX sha256: `6ec74a1e418e5725c351ffbb8dadc11b4f4619846d3c82be5c12048295cb157c`
- x=0.08 compact gate: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- x=0.08 mean vx: `0.0032 m/s`
- x=0.08 track ratio: `0.0394`
- x=0.08 single/double support: `0.0000% / 100.0000%`
- x=0.0 compact gate: `PASS_CANDIDATE_SIM_GATE`

## Live-Oracle Iter2 Student

- status: `HOLD_ITER2_MAX_VELOCITY_EXCESS`
- decision artifact: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_decision.json`
- aggregate manifest: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json`
- aggregate samples: `28500`
- candidate ONNX: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student/candidate.onnx`
- candidate ONNX sha256: `c476120f75ea38b16cfe2a1c0eee49adca648811e65691e374321b58372a8cd7`
- x=0.08 gate: `HOLD_CANDIDATE_TARGET_VELOCITY`
- x=0.08 mean vx: `0.0324 m/s`
- x=0.08 track ratio: `0.4047`
- x=0.08 single/double support: `27.2000% / 72.8000%`
- x=0.08 corrected p95 velocity excess: `0.0000`
- x=0.08 corrected max velocity excess: `0.0149`
- x=0.0 spot gate: `PASS_CANDIDATE_SIM_GATE` over `2/2` seeds

Interpretation: iter2 improved motion and single support relative to the
current rate165 baseline, but it is not promotable because the strict corrected
gate rejects any max velocity excess.

## Decision

- next_status: `HOLD_ITER2_MAX_VELOCITY_EXCESS`
- next_action: Keep the corrected rate165 candidate as the offline baseline. Iter2 live-oracle data is useful because it improves forward progress and single support, but the first iter2 phase/contact student must be rejected for corrected max velocity excess. Next offline work should refit from the iter2 aggregate manifest with tighter max-rate control or an explicit max-velocity guard before any PPO/domain-randomization resume.

## Guardrails

- Do not advance to push/terrain DR stages from the rejected Stage A run.
- Do not scale the CPU2240 motion-preservation recipe into another long A100 run.
- Keep the corrected bridge and per-joint corrected velocity envelope authoritative.
- Reject candidates with any corrected max velocity excess, even if p95 excess is zero.
- No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this report.
