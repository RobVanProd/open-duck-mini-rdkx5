# Ground-Up Command-Deadband Repair Result

status: `PASS_COMMAND_DEADBAND_REPAIR`
decision: `ADVANCE_OFFLINE_CANDIDATE_TO_PREREGISTERED_ROBUSTNESS_LADDER`

| step | x=0 pass | nominal pass | worst nominal tracking | min nominal vx | checkpoint pass |
|---:|---|---|---:|---:|---|
| 512000 | `True` | `True` | 0.180822033 | 0.083376151 | `True` |
| 1024000 | `True` | `True` | 0.181667066 | 0.095189543 | `True` |

## x=0 cells

| step | seed | samples | mean vx | body pitch p95 | tracking p95 | saturation | pass |
|---:|---:|---:|---:|---:|---:|---:|---|
| 512000 | 100 | 600 | -0.000657920 | 0.009043863 | 0.030322790 | 0.000000% | `True` |
| 512000 | 101 | 600 | -0.000657920 | 0.009043863 | 0.030322790 | 0.000000% | `True` |
| 1024000 | 100 | 600 | -0.000657920 | 0.009043863 | 0.030322790 | 0.000000% | `True` |
| 1024000 | 101 | 600 | -0.000657920 | 0.009043863 | 0.030322790 | 0.000000% | `True` |

The explicit zero-command branch repairs the out-of-support x=0 failure while preserving the complete moving-command gate at both selected checkpoints.

Passing authorizes only preregistration of the offline robustness ladder. No training, RDK-X5, or robot access is authorized.
