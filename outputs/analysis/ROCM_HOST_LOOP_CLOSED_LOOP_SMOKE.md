# ROCm Host-Loop Closed-Loop Smoke

Purpose: verify whether the local `7900 XTX` can run the full closed-loop
policy/eval path when repeated MJX substeps are driven from the host instead of
lowered through `jax.lax.scan`.

Command shape:

```bash
../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 0.2 \
  --bridge-mode vanilla \
  --jax-platform gpu \
  --mjx-step-loop-mode python \
  --closed-loop-timeout-s 300 \
  --sim-preflight-timeout-s 300 \
  --output-dir outputs/analysis/rocm_host_loop_closed_loop_smoke_python
```

Result:

| mjx step loop mode | status | backend | samples | termination | wall clock |
|---|---|---|---:|---|---:|
| `python` | `PASS_CLOSED_LOOP_REPRODUCTION` | `rocm:0` | 10 | `duration_complete` | 104.79s |
| `python_block_each` | `PASS_CLOSED_LOOP_REPRODUCTION` | `rocm:0` | 10 | `duration_complete` | 107.02s |

Interpretation:

- The full closed-loop policy/eval path can complete tiny ROCm correctness
  probes when the repeated MJX substeps are host-driven.
- The default Playground scanned substep path remains the local ROCm blocker.
- This is not a training path and is not practical for full 15-second evals.
- CUDA remains the confirmed backend for full closed-loop evaluation and
  candidate training.

No robot tests, SSH, deployment, runtime behavior changes, or training were
performed.
