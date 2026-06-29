# Phase 2 z0.0035 Motion-Floor Result

Status: `HOLD_LOW_FORWARD_PROGRESS`

This run tested an intermediate terrain rung between the passing z0.002 roughness path and
the previously held z0.005 path. It was warm-started from the Phase 2 A2 checkpoint and used
the corrected actuator bridge.

## Training Run

- workflow: `phase2-z0035-motion-floor`
- Colab session: `open-duck-l4`
- remote run: `open_duck_colab_cli_phase2-z0035-motion-floor_20260629T225040Z`
- task: `rough_terrain_backlash`
- terrain heightfield z scale: `0.0035`
- timesteps: `122880`
- PPO envs: `64`
- actuator bridge: enabled
- bridge delay: `3` ticks
- bridge velocity range: `2.0-3.25 rad/s`
- restore checkpoint: `stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- latest ONNX: `2026_06_29_230919_122880.onnx`
- latest ONNX sha256: `88cc2044e9de7a3b4a6f0af81124ddc3444d3911dd1a6570708a3e44720834dd`
- training return code: `0`
- elapsed: `925.9 s`

Training completed cleanly. The remote Colab checkpoint sweep hung, so the exported ONNX
checkpoints were imported locally from the partial artifact bundle and swept on local CPU.

## Compact Checkpoint Sweep

Local sweep:

```text
../envs/open-duck-playground/bin/python tools/sweep_candidate_checkpoints.py \
  --policies <40960.onnx> <81920.onnx> <122880.onnx> \
  --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --commands 0.0,0.08 \
  --duration 1 \
  --bridge-mode fitted \
  --mode-name fitted \
  --jax-platform cpu \
  --closed-loop-timeout-s 600 \
  --output-dir outputs/analysis/phase2_z0035_motion_floor_local_sweep \
  --run
```

| checkpoint | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 mean vx | max pitch vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1615 | 0.0129 | 1.4383 | 0.2129 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1613 | 0.0129 | 1.4444 | 0.2140 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1671 | 0.0134 | 1.4431 | 0.2132 |

All checkpoints stayed below the corrected measured envelope and completed the compact
duration. None met the configured motion criteria.

## Decision

Do not promote this run. The z0.0035 motion-floor recipe preserves standing behavior and
keeps target velocity conservative, but it under-moves at x=0.08. The failure mode is not
over-envelope actuation; it is insufficient commanded forward progress under the roughness
rung.

Per the staged terrain plan, do not escalate terrain height further from this recipe. The
next useful step is to re-check the z0.002 moving policy under the same post-training gate
path and compare whether the motion loss appears between z0.002 and z0.0035, or whether the
post-training gate path is stricter than the earlier z0.002 decision path.

Robot validation remains blocked.
