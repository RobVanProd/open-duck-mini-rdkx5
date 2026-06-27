# Movement Bootstrap V11 A100 Summary

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
robot_touched: `false`
deployed: `false`
trained_on: `Colab A100`
environment: `jax/jaxlib 0.7.2, brax 0.14.2, mujoco/mujoco-mjx 3.9.0`

## Candidate

```text
name: movement_bootstrap_v11_hard_progress_a100_20260624
final_checkpoint: 2026_06_24_042234_245760
onnx_sha256: a3f30d64f21334a5263df15d0b8c11576a04c4fe280c2a082cecb4e2038a13c7
artifact_bundle:
  outputs/analysis/colab_cli/open-duck-a100-v11-staged-curriculum-20260624T035757Z/remote_artifacts_final.tar.gz
```

V11 was intended as a fresh hard-progress bootstrap after V10 mostly improved
lifetime by freezing. It did not restore useful forward motion.

## Gate Results

| gate | status | samples | mean local vx | track ratio | pitch p95 | base min | max pitch tracking p95 | max target velocity p95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.0 | `PASS_CANDIDATE_SIM_GATE` | 750 | ~0.0004-0.0005 | NA | 0.0987-0.1041 | 0.1519 | 0.0623 | 0.2393 |
| x=0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | ~0.0009 | 0.0107-0.0115 | 0.1167-0.1242 | 0.1536 | 0.0734 | 0.2749 |

V11 is stable in the 15 s sim gate, but it is effectively standing still under
positive command. It passes actuator, posture, and saturation constraints by
barely moving.

## Interpretation

V11 confirms that simply making forward shortfall hard and removing Huber
smoothing from the progress floors is not sufficient. The optimizer still found
a low-motion basin:

```text
x=0.08 commanded speed: 0.08 m/s
measured local vx:       ~0.0009 m/s
track ratio:             ~0.011
action saturation:       0%
target velocity p95:     <= 0.275 rad/s
```

This is not a deployable candidate and should not be sent to the robot.

## Consequence

The current reward-only staged bootstrap family remains stuck between unstable
moving policies and stable no-motion policies. Next work should inspect why the
training reward still accepts no-motion behavior despite the shortfall terms,
then change the training setup in a way that cannot be satisfied by standstill.

Candidate next directions:

```text
1. audit reward term magnitudes from V11 rollouts and PPO logs
2. make command-progress failure terminate or heavily downweight episodes
3. train/evaluate on a command-conditioned reset/task that requires displacement
4. consider gait reference or imitation from the moving but unstable phase policy
5. run cheap per-phase gates before full phase continuation to detect freeze early
```

Robot validation remains blocked.
