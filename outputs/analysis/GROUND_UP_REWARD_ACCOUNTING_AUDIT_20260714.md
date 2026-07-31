# Ground-Up Reward Accounting Audit

status: `COMMAND_INVARIANT_REWARD_SELECTED_FOR_NEXT_CAUSAL_TEST`

The logged evaluation return is reconstructed as `dt * (positive reward components - cost components)`. A material positive gap would be evidence that negative per-step totals were removed by the environment's lower clip.

| candidate | step | logged return | reconstructed raw | absolute gap | alive+yaw positive share |
|---|---:|---:|---:|---:|---:|
| `B0_NOMINAL_PHASE0` | 0 | 18.078447 | 18.078448 | 0.00000077 | 107.80% |
| `B0_NOMINAL_PHASE0` | 1003520 | 241.395981 | 241.395995 | 0.00001465 | 90.58% |
| `B0_NOMINAL_PHASE0` | 2007040 | 297.472656 | 297.472651 | 0.00000496 | 83.03% |
| `B0_NOMINAL_PHASE0` | 3010560 | 322.581604 | 322.581632 | 0.00002823 | 81.75% |
| `B0_NOMINAL_PHASE0` | 4014080 | 333.114319 | 333.114316 | 0.00000313 | 81.55% |
| `O1_SIGNED_PROGRESS` | 0 | 15.379923 | 15.379374 | 0.00054877 | 121.06% |
| `O1_SIGNED_PROGRESS` | 1003520 | 195.278595 | 195.278600 | 0.00000454 | 93.32% |
| `O1_SIGNED_PROGRESS` | 2007040 | 295.137787 | 295.137791 | 0.00000443 | 80.44% |
| `O1_SIGNED_PROGRESS` | 3010560 | 327.602142 | 327.602143 | 0.00000053 | 79.53% |
| `O1_SIGNED_PROGRESS` | 4014080 | 346.242981 | 346.242963 | 0.00001755 | 79.81% |

## Decision

Total-reward clipping is not selected for the next causal test. Across all mature B0/O1 evaluation checkpoints, reconstructed raw return matches logged return within the numerical precision recorded in TensorBoard. This does not measure every PPO training transition, but it provides no observed evaluation evidence that clipping drives the failed behavior.

Command-invariant positive reward is selected. At the final checkpoints, alive plus zero-yaw tracking account for 81.55% of B0 positive reward mass and 79.81% of O1 positive reward mass. These terms do not distinguish forward gait from stationary survival in the exact-yaw-zero nominal stage.

The next experiment must change only this structural mechanism and retain signed progress, the nominal bootstrap, PPO settings, phase, command, and frozen behavior gate. Its exact wiring and stop rule require a separate CPU contract and preregistration before accelerator compute.

Training reward is not a selection gate. This audit reads recorded files only and does not access a GPU, iGPU, RDK-X5, robot, motor, or torque.
