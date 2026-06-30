# Phase 2 z=0.002 Teacher Continuity Fixed2 A100 Run

status: `HOLD_REMOTE_NO_SENTINEL_NOT_PROMOTED`

## Summary

- workflow: `phase2-z002-teacher-continuity`
- candidate_name: `phase2_z002_teacher_continuity_cuda_fixed2`
- run_dir: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T040604Z`
- remote workflow: `open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T040650Z`
- Colab session: `open-duck-l4`
- hardware: A100
- wrapper fix present: yes

The corrected recipe launched under the patched Colab liveness parser. The remote policy/sim contract audit passed and the training command was emitted with:

`--actuator-tracking-scale -0.005`

The remote process then disappeared before writing an exit sentinel or artifact bundle. The patched wrapper correctly classified this as `HOLD_REMOTE_NO_SENTINEL` instead of spinning indefinitely.

## Evidence

- remote contract status: `PASS_POLICY_SIM_CONTRACT`
- remote PID state from wrapper: `False` / not running
- remote exit sentinel: missing
- remote artifact bundle: missing
- partial remote output archive: present, size `4069` bytes
- partial output contents: `POLICY_SIM_CONTRACT_AUDIT_CUDA.md`, `policy_sim_contract_audit_cuda.json`
- candidate ONNX: not produced
- checkpoint sweep: not run
- policy promotion: not allowed

## Decision

`HOLD_REMOTE_NO_SENTINEL_NOT_PROMOTED`

This is a Colab remote execution/session failure after training launch, not a candidate policy result. The next useful action is to isolate why the Colab A100 process disappears after starting `run_actuator_bridge_training_smoke.py`, or run the same recipe through a more reliable execution path before spending more A100 time.

No robot tests, SSH, deployment, grounded replay, or runtime behavior changes were performed.
