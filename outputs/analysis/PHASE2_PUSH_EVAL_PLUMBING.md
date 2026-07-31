# Phase 2 Push Eval Plumbing

status: `PUSH_EVAL_MODE_ADDED`

## Summary

The canonical corrected-bridge candidate gate keeps Playground push
perturbations disabled. That remains the default so existing `x=0.08` and
`x=0.0` gates are unchanged.

Phase 2 now has an explicit push-enabled closed-loop eval path:

```text
tools/eval_policy_with_actuator_bridge.py --eval-push-enable ...
tools/run_candidate_seed_sweep.py --eval-push-enable ...
```

The eval path mirrors the Playground push implementation by sampling a push
direction and magnitude, injecting the velocity impulse into the floating base
before the MJX step, and recording per-event recovery metrics.

## Metrics Added

- push event count
- recovered event count
- push recovery success rate
- applied push velocity impulse magnitude
- recovery window sample count
- whether the full recovery window was observed
- per-event max absolute body pitch
- per-event minimum base height

Default recovery criteria:

```text
window: 0.5 s
max abs body pitch: 0.8 rad
min base height: 0.08 m
```

## Smoke Checks

No-push smoke:

```text
outputs/analysis/push_eval_smoke_no_push/
```

Push-enabled smoke:

```text
outputs/analysis/push_eval_smoke_push/
```

The push-enabled smoke forced `0.05` velocity impulses every `0.2 s` for a
short one-second rollout. The report recorded the expected `0.05` impulse
magnitude and push recovery rows in both JSON and markdown.

## Local GPU Note

A one-second local ROCm/MJX push-enabled closed-loop smoke timed out after
`600 s`:

```text
outputs/analysis/push_seed_sweep_smoke_gpu/
status: HOLD_SIM_RUNTIME_ERROR
error: closed-loop worker timed out after 600s
```

Do not use the local ROCm/MJX closed-loop path for Phase 2 correctness gates
until that backend timeout is resolved. Use CPU for small screens or Colab/A100
for longer multi-seed gates.

## Stage A Mild-Push CPU Screen

The first real Stage A push screen ran through the seed-sweep wrapper:

```text
outputs/analysis/PHASE2_STAGE_A_PUSH_SCREEN_CPU.md
outputs/analysis/phase2_stage_a_push_screen_cpu.json
```

Configuration:

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: flat_terrain_backlash
bridge: fitted corrected bridge
command_x: 0.08
duration: 5 s
seeds: 0,1
push interval: 1.0-1.5 s
push magnitude: 0.05-0.10
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE on 2/2 seeds
falls: 0/2
duration_complete: 2/2
mean track ratio: 0.3364
mean vx: 0.0269 m/s
max pitch velocity p95: 1.7561 rad/s
max tracking p95: 0.1970 rad
max velocity excess: 0.0000 rad/s
push events: 4 per seed
mean push recovery success: 0.8750
```

This is a small CPU screen, not the full Phase 2 robustness gate. It shows that
the Stage A candidate can survive mild push perturbations for short windows, but
the full `8`-seed, `15 s` push gate still needs to run on CPU or Colab/A100.

## Stage A Mild-Push CPU Gate

The full mild-push gate then ran on CPU:

```text
outputs/analysis/PHASE2_STAGE_A_PUSH_GATE_CPU.md
outputs/analysis/phase2_stage_a_push_gate_cpu.json
```

Configuration:

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: flat_terrain_backlash
bridge: fitted corrected bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
push interval: 1.0-1.5 s
push magnitude: 0.05-0.10
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE on 8/8 seeds
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.3533
mean vx: 0.0283 m/s
max pitch velocity p95: 1.7741 rad/s
max tracking p95: 0.1975 rad
max velocity excess: 0.0000 rad/s
mean push events per seed: 12.3750
mean push recovery success: 0.9704
```

Interpretation: the Stage A candidate already tolerates mild push perturbations
in evaluation. The Stage B training holds are therefore not evidence that mild
pushes are immediately impossible for the gait; they show that PPO training
with push/randomization erodes forward motion. The next Stage B design should
preserve the Stage A policy more directly while adding randomization, or should
separate evaluation-only push screening from training perturbations.

## Stage A Moderate-Push CPU Gate

A stronger push screen also passed:

```text
outputs/analysis/PHASE2_STAGE_A_PUSH_MODERATE_GATE_CPU.md
outputs/analysis/phase2_stage_a_push_moderate_gate_cpu.json
```

Configuration:

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: flat_terrain_backlash
bridge: fitted corrected bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
push interval: 1.0-1.5 s
push magnitude: 0.10-0.20
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE on 8/8 seeds
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.3467
mean vx: 0.0277 m/s
max pitch velocity p95: 1.7845 rad/s
max tracking p95: 0.1964 rad
max velocity excess: 0.0000 rad/s
mean push events per seed: 12.3750
mean push recovery success: 0.9704
```

Interpretation: the Stage A candidate has meaningful push margin at least up
to `0.20` velocity impulse magnitude in this eval setup. Stage B should not
train against broad push/randomization until a no-regression continuity
mechanism is in place.

## Scope

No robot motion, SSH, deployment, grounded replay, runtime behavior change, or
training was performed by this eval plumbing change.
