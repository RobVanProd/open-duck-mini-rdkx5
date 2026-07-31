# Ground-Up Tracking-Tail Joint/Phase Audit

status: `PASS_JOINT_PHASE_TAIL_AUDIT`
decision: `REJECT_MAX_JOINT_AS_RESCALED_CLOSED_OBJECTIVE`

active exceedance joints: `['left_knee', 'left_ankle']`
inactive exceedance joints: `['left_hip_pitch', 'right_hip_pitch', 'right_knee', 'right_ankle']`
gate-setting trace counts: `{'left_hip_pitch': 0, 'left_knee': 20, 'left_ankle': 16, 'right_hip_pitch': 0, 'right_knee': 0, 'right_ankle': 0}`
max evaluator reproduction error: `2.7755575615628914e-17`

| checkpoint | gate-setting joints | max/mean cost ratio |
|---|---|---:|
| `T1_QUARTER_1024000` | `{'left_knee': 6}` | 6.000000 |
| `T1_QUARTER_512000` | `{'left_knee': 6}` | 6.000000 |
| `T2_EQUAL_1024000` | `{'left_ankle': 6}` | 6.000000 |
| `T2_EQUAL_512000` | `{'left_knee': 2, 'left_ankle': 4}` | 6.000000 |
| `T3_FOUR_1024000` | `{'left_knee': 2, 'left_ankle': 4}` | 6.000000 |
| `T3_FOUR_512000` | `{'left_knee': 4, 'left_ankle': 2}` | 6.000000 |

The closed objective averages six joints although four never exceed the gate. As tail pressure rises, the gate-setting joint shifts from left knee to left ankle. However, only one joint exceeds at any tick, making per-tick maximum joint cost exactly six times the current six-joint mean on every trace. It is therefore only an untested stronger scale in the closed formulation, not a new causal mechanism. No training recipe is selected; the remaining read-only question is temporal exceedance occupancy versus squared magnitude.
