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
  -> run CUDA or CPU smoke/correctness checks
  -> train candidate with actuator bridge enabled
  -> summarize training run
  -> package candidate ONNX metadata
  -> review sim-side gates
  -> only then request suspended robot validation
```

Manual CUDA/Colab helper:

```text
docs/CUDA_COLAB_SINGLE_CELL.md
tools/print_cuda_colab_cell.py
```

Use this path when local `7900 XTX` ROCm/MJX remains blocked and a trusted
Colab/L4/A100 session is available.

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
outputs/analysis/CPU_CANDIDATE_GATE_STEP8240_ZERO_15S.md
outputs/analysis/CPU_CANDIDATE_GATE_STEP32800_HOLD.md
```

`step8240_zero_penalty` passed `15 s` CPU candidate sim gates at `x=0.0` and
`x=0.08`, but it is still not approved for the robot. Treat it as an offline
candidate for review, not a deployable policy.

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
  --target-velocity-summary outputs/analysis/<candidate>_target_velocity.md \
  --actuator-bridge-eval outputs/analysis/<candidate>_actuator_bridge_eval.md \
  --output-md outputs/analysis/<candidate>_policy_package.md \
  --output-json outputs/analysis/<candidate>_policy_metadata.json
```

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
