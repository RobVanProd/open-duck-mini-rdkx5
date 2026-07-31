# V21 Planner CPU Smoke

status: `PASS_V21_PLANNER_CPU_SMOKE`

This was a tiny local CPU smoke of the staged V21 planner path. It was not a
candidate training run, did not use the robot, did not deploy anything, and did
not change runtime behavior.

## Command Shape

- recipe: `movement_bootstrap_v21`
- planner: `tools/plan_staged_curriculum_training.py`
- platform: `cpu`
- stop_after_phase: `1`
- timesteps_scale: `0.0001`
- effective phase timesteps: `22`
- ppo_num_envs: `4`
- ppo_episode_length: `20`
- output_root: `/tmp/open_duck_v21_planner_cpu_smoke`

## Result

- planner status: `PASS_STAGED_CURRICULUM_RUN`
- wrapper status: `PASS_SMOKE_RUN`
- elapsed_s: `51.887847695001255`
- final checkpoint: `/tmp/open_duck_v21_planner_cpu_smoke/01_phase1_soft_prior_low_command_probe/smoke_20260625T083500Z_cpu/2026_06_25_043537_40`
- final ONNX: `/tmp/open_duck_v21_planner_cpu_smoke/01_phase1_soft_prior_low_command_probe/smoke_20260625T083500Z_cpu/2026_06_25_043537_40.onnx`

The checkpoint and ONNX were generated only as smoke outputs under `/tmp` and
are not committed.

## Soft-Prior Wiring Check

The planner emitted the expected V21 phase-1 soft-prior flags:

- `--enable-soft-prior`
- `--soft-prior-config-json outputs/analysis/soft_prior_fragment_config.json`
- `--soft-prior-scale -0.025`
- `--soft-prior-huber-delta 0.05`
- `--soft-prior-phase-source imitation_i`
- `--disable-actuator-bridge`

The wrapper then resolved the relative config path before invoking the
Playground runner:

```text
/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/soft_prior_fragment_config.json
```

That confirms the full planner path can pass the compact prior into the
patched Playground runner even though the subprocess runs from the sibling
Playground checkout.

## Scope

- no robot tests
- no SSH
- no deployment
- no walking runtime changes
- no policy files modified
- no raw `/tmp` logs, checkpoints, TensorBoard event files, or ONNX smoke
  artifacts committed

## Next Gate

`movement_bootstrap_v21` still needs a real CUDA/Colab staged run and an
`x=0.04` multi-seed sim gate. The current local readiness artifact remains:

```text
outputs/analysis/V21_LAUNCH_READINESS.md
status: HOLD_COLAB_SESSION_MISSING
```

Once a Colab session is active again, rerun `tools/check_v21_launch_readiness.py`
before launching V21.
