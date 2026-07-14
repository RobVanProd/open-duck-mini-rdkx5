# Ground-Up Reference Teacher Audit

status: `REJECT_DIRECT_BC_SELECT_REFERENCE_ANCHORED_RESIDUAL_CONTRACT`

## Measured teacher behavior

| reference action mode | runs | falls | mean vx | track ratio | contact mismatch | decision |
|---|---:|---:|---:|---:|---:|---|
| `raw` | 8 | 4 | -0.0863 | -1.1668 | 70.90% | invalid BC label |
| `cycle_projected` | 8 | 2 | -0.0120 | -0.1624 | 71.41% | invalid BC label |
| `contact_synchronized_projected` | 8 | 2 | -0.0127 | -0.1715 | 14.67% | invalid BC label |

The envelope-projected table itself is deterministic and valid: shape `[240, 27, 14]`, maximum action `1.0`, SHA-256 `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`. The failure is behavioral, not a missing table or action-envelope violation.

Contact synchronization reduced mismatch but did not create propulsion: mean forward velocity remained negative and two of eight runs fell. Direct supervised cloning would therefore reproduce a measured failed controller and is rejected.

## Existing learned comparison

`M1_REFCOND` gave a randomly initialized actor the same projected action as an observation feature. It produced one isolated moving pass, zero persistent moving seeds, two hard failures, and no full checkpoint pass. Reference input alone is insufficient.

## Selected contract target

The next mechanism to implement and CPU-test is an actor-internal reference-anchored residual. Its initial deterministic final action must equal the projected reference action, while the learned network supplies a state-feedback correction. The composition must be inside the exported policy, not an RDK wrapper. This uses the reference as initialization, not as a claim that its open-loop actions are correct.

No accelerator experiment is authorized until initialization equality, PPO log-probability semantics, ONNX equivalence, observation/action ABI, and a finite CPU smoke train all pass.

No GPU, iGPU, RDK-X5, robot, motor, or torque access occurred.
