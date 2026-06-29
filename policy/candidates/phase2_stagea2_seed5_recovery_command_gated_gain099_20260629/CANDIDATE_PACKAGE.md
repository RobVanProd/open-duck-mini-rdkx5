# Candidate Policy Package

status: `READY_FOR_SIM_GATE_REVIEW`
generated_at: `2026-06-29T15:37:11Z`

## Candidate

- name: `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- size_bytes: `1772930`

This candidate is the Stage-A2 / seed5-recovery command-gated ONNX with the
final action output scaled by `0.99` inside the ONNX graph. It is not using an
evaluator-side action multiplier.

Scale verification:

```text
policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/onnx_scale_verify.json
status: PASS_ONNX_OUTPUT_SCALE_VERIFY
max_abs_error: 0.0
```

## Contract

- status: `PASS_POLICY_CONTRACT`
- expected input dim: `101`
- actual input dim: `101`
- expected output dim: `14`
- actual output dim: `14`

| kind | name | shape | dtype |
|---|---|---|---|
| input | `obs` | `[1, 101]` | `tensor(float)` |
| output | `continuous_actions` | `[1, 14]` | `tensor(float)` |

## Source Revisions

| repo | branch | commit | dirty status |
|---|---|---|---|
| `rdk_repo` | `codex/live-oracle-dagger-phase-student` | `08c0381dbcdfb6cbe1536910090dfe6ea01b1f92` | `dirty` |
| `playground_repo` | `codex/forward-progress-reward` | `d969ca8c3760451a39657161cb376c44c5155a6d` | `clean` |

## Evidence

| evidence | required | status | path |
|---|---|---|---|
| `contract_audit` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/policy_sim_contract_audit.json` |
| `target_velocity_summary` | `False` | `MISSING` | `None` |
| `candidate_gate_x0` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json` |
| `candidate_gate_x008` | `True` | `PRESENT` | `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json` |
| `actuator_bridge_eval_legacy` | `False` | `MISSING` | `None` |
| `training_manifest` | `True` | `MISSING` | `None` |

## Sim Gate Status

| gate | eval_role | overall_status | candidate_gate_status | pass/total |
|---|---|---|---|---:|
| `candidate_gate_x0` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |
| `candidate_gate_x008` | `candidate_seed_sweep` | `PASS_CANDIDATE_SEED_SWEEP` | `PASS_CANDIDATE_SEED_SWEEP` | `8/8` |

The package gates above are the rough `z=0.002` gentle-push 15-second gates.
Supplemental no-push gates also passed 8/8:

```text
x=0.08 no-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X008_ROUGH_Z002_NOPUSH_15S_8SEED_CPU.md

x=0.0 no-push:
  outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X0_ROUGH_Z002_NOPUSH_15S_8SEED_CPU.md
```

## Robot Gate

This package does not approve robot testing. Robot-side suspended
validation still requires reviewed sim gates, Rob physically present,
and explicit approval for the specific test.
