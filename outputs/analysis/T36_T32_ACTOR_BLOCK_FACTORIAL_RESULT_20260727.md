# T36 T32 actor-block factorial result

status: `PASS_T36_T32_ACTOR_BLOCK_FACTORIAL_WITH_REPAIR`

decision: `EARN_T37_NORMALIZER_HALF_FREEZE_TRAINING_CPU_CONTRACT_PREREGISTRATION`

| variant | half groups | green | samples | saturation |
|---|---|---:|---:|---:|
| `NORMALIZER_HALF` | `normalizer` | `True` | `600` | `0.000000%` |
| `BASE_HALF` | `base` | `True` | `600` | `0.000000%` |
| `ADAPTER_HALF` | `adapter` | `True` | `600` | `0.000000%` |
| `NORMALIZER_BASE_HALF` | `normalizer,base` | `True` | `600` | `0.000000%` |
| `NORMALIZER_ADAPTER_HALF` | `normalizer,adapter` | `True` | `600` | `0.000000%` |
| `BASE_ADAPTER_HALF` | `base,adapter` | `True` | `600` | `0.000000%` |

Every single-block rollback repairs the exact failed cell, as do all three
two-block rollbacks. The final failure therefore requires the combined
late-training state: no individual normalizer, base, or adapter block is
independently necessary once either of the other blocks is restored.

The preregistered precedence chooses `NORMALIZER_HALF` because it is a
one-block repair and freezing the observation normalizer is the
lowest-complexity prospective training constraint. This is a mechanism
selection for a new CPU contract, not promotion of the hybrid graph.

This result authorizes at most a separate CPU software contract for the selected freeze-during-training mechanism. It does not promote a hybrid policy.

No hosted training, Gate 5, RDK-X5, robot, torque, or motion is authorized.
