# Ground-Up Guard Winner x=0 Result

status: `PASS_GUARD_WINNER_X0_NO_ADVANCE`
decision: `PREREGISTER_COMMAND_DEADBAND_ZERO_ACTION_REPAIR`

| step | seed | samples | termination | saturation | mean vx | pass |
|---:|---:|---:|---|---:|---:|---|
| 512000 | 100 | 73 | `fall_or_nan` | 87.671233% | -0.052821646 | `False` |
| 512000 | 101 | 73 | `fall_or_nan` | 87.671233% | -0.052821646 | `False` |
| 1024000 | 100 | 211 | `fall_or_nan` | 95.734597% | -0.014837593 | `False` |
| 1024000 | 101 | 211 | `fall_or_nan` | 95.734597% | -0.014837593 | `False` |

Both selected checkpoints fail x=0 with early termination and extreme action saturation. Their tracking and rate metrics remain inside bounds before termination, isolating the unsupported zero-command actor output rather than the actual-centered guard.

The nominal winner remains held. No robustness ladder, training, RDK-X5, or robot access is authorized.
