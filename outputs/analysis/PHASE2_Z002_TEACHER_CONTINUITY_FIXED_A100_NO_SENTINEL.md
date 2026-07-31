# Phase 2 z=0.002 Teacher Continuity Fixed A100 Run

status: `HOLD_REMOTE_NO_SENTINEL_NOT_PROMOTED`

## Summary

- workflow: `phase2-z002-teacher-continuity`
- candidate_name: `phase2_z002_teacher_continuity_cuda_fixed`
- run_dir: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T035118Z`
- remote workflow: `open_duck_colab_cli_phase2-z002-teacher-continuity_20260630T035142Z`
- Colab session: `open-duck-l4`
- hardware: A100

The corrected teacher-continuity command launched and confirmed the intended light actuator tracking setting:

`--actuator-tracking-scale -0.005`

The remote policy/sim contract audit passed, but the remote process exited before writing an exit sentinel, artifact bundle, training summary, checkpoint sweep, or candidate ONNX. This run is not a model result and no checkpoint is promotable from it.

## Evidence

- remote PID file: present
- remote PID state checked after failure: `NOT_RUNNING`
- remote log: present, size `41493` bytes
- remote exit sentinel: missing
- remote artifact bundle: missing
- partial remote analysis output: downloaded
- partial output contents: `POLICY_SIM_CONTRACT_AUDIT_CUDA.md`, `policy_sim_contract_audit_cuda.json`
- remote contract status: `PASS_POLICY_SIM_CONTRACT`
- training directory artifact: not recovered due Colab CLI connection loss during postmortem inspection

## Local Wrapper Fix

During this run, the local Colab wrapper was found to misparse remote PID liveness: it checked for `RUNNING` before `NOT_RUNNING`, so `NOT_RUNNING` could be interpreted as running. The parser was patched to check `NOT_RUNNING` first.

## Decision

`HOLD_REMOTE_NO_SENTINEL_NOT_PROMOTED`

Do not use this run for policy selection. The next launch should use the patched wrapper, the same corrected recipe, and should be treated as the first valid fixed A100 attempt only if it produces an exit sentinel plus artifact bundle or a recoverable training summary/checkpoint set.

No robot tests, SSH, deployment, grounded replay, or runtime behavior changes were performed.
