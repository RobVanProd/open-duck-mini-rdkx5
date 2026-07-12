# Rate165 Phase-Local Compact Objective Result

status: `REJECT_CLOSE_OBJECTIVE_NO_COLAB`

## Frozen intervention

The single CPU-only compact fit used the preregistered phase/joint temporal
objective and exact frozen parameters in
`PHASE2_RATE165_PHASE_LOCAL_OBJECTIVE_PREREGISTRATION_20260712.md`. No sweep,
robot access, deployment, iGPU, onboard GPU, or Colab was used.

## Fit evidence

- steps: `1000`
- aggregate target-rate p95: `1.29089 rad/s` (parent `1.42353`)
- cloning p95 absolute error: `0.04480` (parent `0.01756`)
- cloning maximum absolute error: `0.99581` (parent `0.29869`)
- ONNX maximum export error: `3.51e-7`

The rate reduction came with materially degraded behavior fidelity.

## Unchanged corrected-bridge seed-0 screen

- result: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples before termination: `72`
- minimum base height: `0.0830 m` (required `>=0.120 m`)
- mean local vx: `-0.2210 m/s` (required `>=0.02584 m/s`)
- tracking ratio: `-2.7630` (required `>=0.3230`)
- single support: `11.1111%` (required `>=21.4066%`)
- maximum corrected velocity excess: `2.8131 rad/s` (required `0`)
- action saturation: left hip pitch `83.33%`, left ankle `87.50%`, right hip
  pitch `86.11%`, right ankle `87.50%`

The candidate fails multiple motion-preservation, safety, and actuator-envelope
rules by large margins. Per preregistration, the objective is closed without
longer training or parameter tuning. Colab allocation is not supported. The
promoted rate165 candidate remains unchanged.

## Artifacts

- fit: `outputs/analysis/phase2_rate165_phase_local_compact_student.json`
- candidate (rejected):
  `outputs/analysis/phase2_rate165_phase_local_compact_student/candidate.onnx`
- bridge result:
  `outputs/analysis/phase2_rate165_phase_local_compact_x008_seed0/closed_loop_actuator_bridge_eval.json`

