# Stage A Command-Progress Failure Result

Date: 2026-07-11

Status: **NO CHECKPOINT PASSED BOTH COMPACT GATES; BRANCH CLOSED**

The preregistered one-factor experiment replayed the authoritative
prior-enabled Stage A recipe with only positive-command progress-failure
termination enabled at ratio `0.25` after 30 control ticks. Colab T4 training
completed and emitted steps 81,920, 163,840, and 245,760.

The Colab runtime disappeared during the post-training CPU checkpoint sweep
without writing its exit sentinel. This was an infrastructure interruption,
not an experimental result. The last valid artifact archive contained all
three ONNX checkpoints and the training summary. Those immutable checkpoints
were recovered, the Colab session was stopped, and the exact registered sweep
was rerun locally with JAX forced to CPU and both CUDA and HIP devices hidden.

| step | training reward | x=0 status | x=0.08 status | x=0.08 vx | ratio | tracking p95 |
|---:|---:|---|---|---:|---:|---:|
| 81,920 | 13.2027 | pass | low-progress hold | 0.0104 | 0.1295 | 0.2143 |
| 163,840 | 15.0803 | tracking hold (`0.2038`) | tracking hold | 0.0230 | 0.2870 | 0.2162 |
| 245,760 | 13.8371 | tracking hold (`0.2095`) | low-progress hold | 0.0155 | 0.1939 | 0.2166 |

No checkpoint passed both commands. Therefore the preregistered seeds 40-71
expansion was not run. This exact threshold and warmup setting is closed
without tuning. The result shows the termination can produce forward progress
at step 163,840, but it did not resolve the actuator-tracking gate and did not
preserve the x=0 gate. Training reward is not comparable to the original recipe
because the new termination changes episode length and return accumulation.

Operational note: while locating the correct local evaluation interpreter, a
single diagnostic command enumerated JAX devices before GPU visibility was
disabled and briefly initialized the ROCm device. No rollout or workload ran
on it. The corrected sweep was verified from the live worker environment with
`JAX_PLATFORMS=cpu`, `JAX_PLATFORM_NAME=cpu`, `CUDA_VISIBLE_DEVICES=-1`, and
`HIP_VISIBLE_DEVICES=-1`.

Primary evidence:

- `outputs/analysis/phase2_stage_a_progress_failure_salvaged_20260711/compact_checkpoint_sweep_cpu_retry/candidate_checkpoint_sweep.json`
- `outputs/analysis/phase2_stage_a_progress_failure_salvaged_20260711/open_duck_colab_cli_phase2-stage-a-narrow_20260711T220854Z/phase2_stage_a_narrow_rate175_cuda_training_run_summary.json`

No robot, SSH, deployment, grounded replay, or moving hardware test was used.
