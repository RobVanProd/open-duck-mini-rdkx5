# Open Duck Mini Current Status

Updated: 2026-06-22

## Current Priority

The robot is parked. Do not run more robot motion until a new candidate policy
passes the offline actuator-bridge gates and Rob explicitly approves suspended
validation.

Current work is offline:

```text
Playground actuator bridge merged
  -> RDK training workflow merged
  -> manual CUDA/Colab candidate run
  -> import CUDA artifact bundle locally
  -> review x=0.0 and x=0.08 candidate sim gates
  -> package candidate ONNX metadata only if gates pass
  -> only then request suspended robot validation
```

Manual CUDA/Colab helper:

```text
docs/CUDA_COLAB_SINGLE_CELL.md
tools/print_cuda_colab_cell.py
```

Use this path when local `7900 XTX` ROCm/MJX remains blocked and a trusted
Colab/L4/A100 session is available.

Local `7900 XTX` update:

```text
default scanned MJX substep path: still blocked on ROCm
host-loop closed-loop smoke: PASS for 10 ticks, about 105s wall-clock
status: useful for tiny correctness probes only, not training
```

Post-reset ROCm recheck:

```text
outputs/analysis/ROCM_AFTER_RESET_RECHECK_20260622.md
basic JAX / JIT / minimal MJX: PASS
Open Duck reset: PASS
Open Duck direct mjx_env.step: TIMEOUT
Open Duck direct mjx_env.step JIT: ROCm abort
HSA_OVERRIDE_GFX_VERSION=11.0.0: harmful, aborts even basic JAX
gate: HOLD_PLAYGROUND_GPU_STEP
```

Local CPU update:

```text
training/export/package plumbing: works
candidate behavior: stable near-standing policies so far
status: not a useful candidate-training backend
```

## Current Leading Finding

The forward-fall investigation no longer points first at a gross IMU, joint
mapping, or policy-file mismatch.

Evidence now points to actuator dynamics:

```text
slow sine sweeps:
  pass at low target velocity

suspended x=0.0:
  mostly healthy / warning only

suspended x=0.08:
  coherent air-walking visually
  sustained pitch-chain lag
  target waveform faster than the real actuator chain can track

fitted actuator model:
  explains most of the suspended x=0.08 target/actual lag

CUDA closed-loop actuator bridge eval:
  PASS_CLOSED_LOOP_REPRODUCTION
```

Grounded replay remains blocked.

## Active Policy State

Baseline policy:

```text
policy/BEST_WALK_ONNX_2.onnx
sha256: 3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
contract: obs[1,101] -> continuous_actions[1,14]
```

Do not overwrite this file.

No new deployable candidate policy is active as of this update.

June 22 CUDA candidates:

- `open_duck_mini_actuator_bridge_cli_20260622T202101Z`
  (`sha256=e444d47f14846721ee1c71a4f15ed3da62b7abc07b7f2e8ecc9d122a818b125a`)
  is not deployable. It trained on Colab L4 to step `307200`, then held in sim:
  `x=0.0` fell/terminated and `x=0.08` had low forward progress.
- `open_duck_mini_actuator_bridge_cli_20260622T205753Z`
  (`sha256=bdfb5655a07bbff564e58ac8ff0f6b398fa36fcd8380c98c0c0194364ff2cd83`)
  is not deployable. It trained on Colab L4 to step `614400` with yaw tracking
  disabled, then held in local CPU gates: `x=0.0` fell/terminated and `x=0.08`
  had near-zero/negative forward progress.

The checkpoint scan for the second CUDA candidate found that the step-0 export
passed `x=0.0`, but every trained checkpoint from `153600` onward failed
`x=0.0`. Exported sample actions saturated after the first checkpoint, so the
next training recipe needs an action-magnitude penalty in addition to
action-rate and target-rate penalties.

Review-only candidate preserved in git:

```text
policy/candidates/open_duck_mini_actuator_bridge_cpu_pilot_20260622_step8240/
```

Status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`. This candidate is not deployed
and is not approved for robot-side validation.

Tiny CPU smoke ONNX exports exist under `/tmp/open_duck_actuator_bridge_smoke/`.
They are explicitly non-deployable and were used only to validate the training
loop, summarizer, and package tooling.

Post-merge CPU pilot summaries are recorded here:

```text
outputs/analysis/CPU_ACTUATOR_BRIDGE_PILOT_SUMMARY.md
```

Those pilots passed the offline training/export/package path but did not
produce a robot-ready candidate.

Initial candidate-mode CPU eval reports:

```text
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_X0_15S.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_X004_15S.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_15S.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_TARGET_RATE_X008_HOLD.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_NEG_TARGET_RATE_X008_HOLD.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP8960_POS_TARGET_RATE_X008_HOLD.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP32800_HOLD.md
outputs/analysis/CPU_FORWARD_PROBE_STEP61440_HOLD.md
outputs/analysis/CPU_AGGRESSIVE_FORWARD_PROBE_STEP61440_HOLD.md
```

`step8240_zero_penalty` passed the `15 s` CPU candidate sim gate at `x=0.0`,
but `x=0.04` and `x=0.08` now hold on
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`: mean forward velocity remains near zero.
The positive-scale and negative-penalty target-rate pilots also hold at
`x=0.08`. The step8960 positive target-rate pilot also holds on
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`: it is stable and smooth, but its mean
forward velocity remains near zero. Treat these as offline training/export
evidence, not deployable policies.

Two stronger CPU forward-curriculum probes also reached step `61440`; both
passed the `x=0.0` gate but still held at `x=0.08` because forward velocity
remained near zero. This strengthens the conclusion that local CPU is a
plumbing/correctness backend, not the next useful candidate-training backend.

## Active PRs

RDK diagnostics/workflow repo:

```text
PR: https://github.com/RobVanProd/open-duck-mini-rdkx5/pull/18
status: merged into main
purpose: training workflow, smoke launcher, candidate packaging gates, docs
```

Playground fork:

```text
PR: https://github.com/RobVanProd/Open_Duck_Playground/pull/1
status: merged into main
purpose: default-off actuator bridge in joystick env and runner controls
```

Local ROCm/MJX backend issue:

```text
issue: https://github.com/RobVanProd/open-duck-mini-rdkx5/issues/19
status: HOLD_PLAYGROUND_GPU_STEP on local RX 7900 XTX
```

## Backend State

CUDA:

```text
Google Colab NVIDIA L4:
  PASS_CLOSED_LOOP_REPRODUCTION
```

Local RX `7900 XTX` / ROCm:

```text
basic JAX GPU: PASS
minimal MJX GPU: PASS
Playground reset GPU: PASS
Playground step GPU: HOLD_PLAYGROUND_GPU_STEP
```

Latest compact recheck:

```text
outputs/analysis/rocm_mjx_recheck_after_cost_sign/ROCM_MJX_RUNTIME_ISOLATION.md
basic JAX GPU: PASS
minimal MJX GPU: PASS
Playground one-step vanilla: TIMEOUT
Playground one-step JIT: FAIL
gate: HOLD_PLAYGROUND_GPU_STEP
```

Post-reset recheck:

```text
outputs/analysis/ROCM_AFTER_RESET_RECHECK_20260622.md
basic JAX GPU: PASS
JAX jit/scan GPU: PASS
minimal MJX GPU: PASS
Playground reset GPU: PASS
Playground direct mjx_env.step GPU: TIMEOUT
Playground direct mjx_env.step JIT GPU: FAIL
gate: HOLD_PLAYGROUND_GPU_STEP
```

CPU:

```text
reduced-horizon correctness checks: usable
post-merge PPO pilots: pass tooling, not deployable
full training: not practical as the primary path
```

Use `docs/CUDA_BACKEND_TRAINING_RUNBOOK.md` for CUDA runs while issue #19
remains open.

## Candidate Gate Order

Before any robot-side validation:

1. Summarize training run:

```bash
python3 tools/summarize_training_run.py <run_dir> \
  --output-md outputs/analysis/<candidate>_training_run_summary.md \
  --output-json outputs/analysis/<candidate>_training_run_summary.json
```

2. Package latest ONNX:

```bash
python3 tools/package_candidate_policy.py <candidate.onnx> \
  --candidate-name <candidate> \
  --training-manifest <run_dir>/smoke_manifest.final.json \
  --contract-audit outputs/analysis/<candidate>_contract.md \
  --candidate-gate-x0 outputs/analysis/<candidate>_candidate_gate_x0.md \
  --candidate-gate-x008 outputs/analysis/<candidate>_candidate_gate_x008.md \
  --output-md outputs/analysis/<candidate>_policy_package.md \
  --output-json outputs/analysis/<candidate>_policy_metadata.json
```

Add `--target-velocity-summary outputs/analysis/<candidate>_target_velocity.md`
when a standalone target-velocity analysis exists.

3. Review `docs/CANDIDATE_POLICY_VALIDATION_GATES.md`.

4. If all sim-side gates pass, request Rob's approval for suspended `x=0.0`.

Robot validation order remains:

```text
1. suspended x=0.0
2. suspended x=0.08
3. grounded replay only after suspended dynamic tracking passes
```

## Board State

Last known board facts from the RDK-X5 evidence snapshot:

```text
board: D-Robotics RDK-X5
hostname: ubuntu
SSH target: sunrise@192.168.1.50
runtime: /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5
board Python: /home/sunrise/duck_env/bin/python
board policy: /home/sunrise/BEST_WALK_ONNX_2.onnx
imu_upside_down: true
start_paused: true
```

The live RDK-X5 `duck_config.json` captured real calibrated offsets. Treat it
as physical truth unless a later snapshot proves otherwise.

## Superseded Historical Note

The old `open_duck_peer` candidate bundle from 2026-06-16 is superseded for the
current actuator-bridge workflow. Do not use its hardware validation commands as
the current runbook.

Historical details remain available in git history before this file was updated
on 2026-06-22.

## Hard Stops

- Do not run grounded replay yet.
- Do not deploy smoke ONNX files.
- Do not overwrite `BEST_WALK_ONNX_2.onnx`.
- Do not tune hardware gains, offsets, IMU remaps, action scale, or phase
  timing as part of candidate policy work.
- Do not treat local ROCm/MJX failure as robot evidence.

## Pre-Robot Physical Pose Gate

Do not treat future robot walking behavior as policy evidence until the physical
home/start pose is re-checked against the sim/runtime specification.

The software evidence is only partial:

```text
runtime home pose == sim home keyframe
live duck_config offsets were captured
home_pose_log_test had small compensated tracking errors
```

That does not prove the physical joint geometry is still calibrated to spec.
The large live `left_knee` offset (`-1.4880 rad`) makes this a hard gate.

Before any next robot validation:

```text
1. Support the robot and command home pose.
2. Compare real hip pitch, knee, ankle, and foot geometry to the documented
   home/start pose.
3. Re-run/audit soft offsets if any joint is off.
4. Capture a new duck_config snapshot if offsets change.
5. Re-run home_pose_log_test after any offset change.
```
