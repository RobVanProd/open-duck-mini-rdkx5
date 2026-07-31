# Phase 2 z=0.0026 A100 Probe Decision

status: `HOLD_SCALAR_TEACHER_CONTINUITY_PLATEAU`
generated_at: `2026-07-02T06:25:00Z`

This is an offline decision artifact. It does not train, run simulation, SSH,
deploy, run robot tests, or change runtime behavior.

## Executive Summary

The A100 Colab execution path is now usable for bounded foreground runs when
artifact heartbeat bundling is enabled. The policy result is still a hold:
the scalar teacher-continuity recipe repeatedly lands in the same compact-gate
tracking band and does not produce a promotable corrected-bridge candidate.

Do not launch another scalar reward-only / teacher-continuity variant from
this evidence. The next work should use the canonical corrected evaluator and
move back to the pre-registered live-oracle / phase-memory path, or rebuild a
stronger corrected source/oracle before another DAgger iteration.

## Remote Execution

- active session checked: `open-duck-a100-heartbeat`
- hardware: `A100`
- status after latest probe: `IDLE`
- transport finding: `PASS_A100_HEARTBEAT_ARTIFACT_RECOVERY`
- tool change used: `tools/run_colab_cli_cuda_workflow.py --remote-artifact-interval-s 120`

The old `open-duck-a100-poll` session became stale and should not be reused.

## Probe Results

| probe | envs | steps | artifact sha256 | onnx sha256 | x=0.08 status | track ratio | mean vx | max tracking p95 | max pitch sent vel p95 |
|---|---:|---:|---|---|---|---:|---:|---:|---:|
| small foreground | 4 | 8192 | `5367ea83205b9859f4f78497d1f426c02cf8e8d199b98386ea7acfe9cb38d0b5` | `ea691aa25895de3b70953e5ead605075d67b1af16845bb155debbbc4dd8cc120` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2315 | 0.0185 | 0.2174 | 1.5133 |
| heartbeat medium | 4 | 20480 | `bad2b950a4f48d0235b0f55d566f4aebbc23b555646dba2ba6f22d46c9768033` | `2ca86dd002614716a7d8c7061fa6d371dab0f9a4879433156e4e3736652fb5a5` | `HOLD_CANDIDATE_TRACKING` | 0.3039 | 0.0243 | 0.2194 | 1.5470 |
| heartbeat 8env | 8 | 8192 | `72ec2135b101ad94c9e76c747b78177bd4f4b177c5e1530ae3f8934fde27964e` | `343342e5135ae12534ee8fde33e6d22e6b90bbe49dce2e3ef202f8ca71412b4a` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2088 | 0.0167 | 0.2197 | 1.5208 |

The 4-env / 20480-step checkpoint is the best of these bounded probes by
positive-command progress, but it still holds the strict corrected gate:

```text
max_pitch_tracking_p95 = 0.2194 rad > 0.20 rad gate
track_ratio = 0.3039
mean_local_vx = 0.0243 m/s
```

The repeated tracking p95 band of `0.2174-0.2197 rad` indicates a scalar
teacher-continuity plateau, not a Colab transport problem.

## CI Note

The latest GitHub Actions `Validate` push run failed before any static-check
steps executed:

```text
run: 28568498378
job: Static Checks
runner_name: ""
steps: []
log: not found
```

Local validation should remain the source of truth until hosted Actions starts
jobs again. Previous local checks passed after the heartbeat tool change.

## Decision

```text
HOLD_SCALAR_TEACHER_CONTINUITY_PLATEAU
```

Do not promote any A100 probe checkpoint above. Do not run robot validation from
these checkpoints. Do not spend another A100 cycle on the same scalar
teacher-continuity branch without a new mechanism.

Next allowed offline actions:

1. Use `docs/EVALUATOR_RECONCILIATION.md` as the canonical evaluator contract.
2. Treat `outputs/analysis/actuator_response_fit_corrected_knee.json` as the
   actuator bridge for all candidate gates.
3. Rebuild or strengthen the corrected source/oracle, then run live-oracle
   DAgger on the current student's visited states.
4. If using recurrence, keep it as offline diagnostic unless a hidden-state
   runtime adapter is explicitly implemented and reviewed.

No robot, SSH, deploy, grounded replay, or runtime behavior change is
authorized by this decision.
