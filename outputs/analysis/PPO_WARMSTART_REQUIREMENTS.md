# PPO Warm-Start Requirements

status: `PLAN_PPO_WARMSTART_PLUMBING`

This is an offline planning artifact. It does not train, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Why This Exists

The source-VX selector proved fitted-bridge in-envelope walking feasibility, and
the DAgger-2/DAgger-3 neural students proved that a compact ONNX/MLP can inherit
some of that behavior. The remaining hold is the deployable neural student's
tracking/rate tradeoff:

```text
latest candidate: outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate.onnx
latest gate: outputs/analysis/DAGGER3_RATE_REG_POLICY_VALIDATION.md
status: HOLD_DAGGER3_TRACKING_RATE_REGRESSION
```

Another pure BC relabel pass is not the next best default. The next branch
should PPO fine-tune from a walking BC warm start with the fitted actuator
bridge active.

## Current Runner Contract

The local Playground runner supports:

```text
--restore_checkpoint_path
```

but that path is passed into Brax PPO as an Orbax checkpoint restore. It is not
a direct ONNX or NPZ warm-start interface.

Current candidate artifacts are:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate_mlp.npz
```

So the immediate technical blocker is:

```text
BC/ONNX/NPZ student weights are not yet loadable as PPO initial params.
```

## Required Next Step

Create one of these, in order of preference:

1. A converter that maps the saved BC MLP NPZ into the PPO policy network param
   PyTree and writes an Orbax checkpoint accepted by `--restore_checkpoint_path`.
2. A runner option that initializes PPO policy params from the BC MLP NPZ before
   training starts, while leaving value-network params freshly initialized.
3. A training-side auxiliary imitation loss that queries the BC candidate during
   PPO, if direct param initialization is too risky.

## Verification Gate

Before launching a real PPO run, the warm-start plumbing must pass a smoke:

```text
load initialized PPO params
export step-0 ONNX
compare step-0 ONNX actions against the source BC candidate on held-out obs
run task-matched fitted x=0.08 seed sweep
confirm behavior is close to the BC candidate before PPO updates
```

If step-0 behavior does not match the BC candidate, do not train. Fix the
parameter mapping first.

## Training Gate After Plumbing

Only after step-0 warm-start fidelity passes:

```text
short PPO smoke
fitted actuator bridge active
flat_terrain_backlash
positive command region centered near x=0.08
low learning rate
target-rate/tracking diagnostics enabled
no robot validation
```

Success is not "reward improved." Success is:

```text
task-matched fitted gate improves tracking p95 without losing forward progress
```

## Stop Rules

- Do not start PPO from scratch for this branch.
- Do not treat ONNX as directly restorable by the current runner.
- Do not train unless step-0 warm-start fidelity is verified.
- Do not relax the actuator envelope.
- Do not run stress or robot gates until fitted tracking improves.
