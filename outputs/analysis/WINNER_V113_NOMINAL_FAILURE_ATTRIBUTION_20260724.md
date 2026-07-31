# Winner-v113 nominal failure attribution

Status: `PASS_WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION`

Failing cells: `11/16`

Failure joints: `{'left_hip_yaw': 0, 'left_hip_roll': 0, 'left_hip_pitch': 0, 'left_knee': 3, 'left_ankle': 11, 'head_1': 0, 'head_2': 0, 'head_3': 0, 'head_4': 0, 'right_hip_yaw': 0, 'right_hip_roll': 0, 'right_hip_pitch': 0, 'right_knee': 0, 'right_ankle': 0}`

Every failure remains a sparse left-knee/left-ankle torque event. Only one joint exceeds the boundary per tick, so a max-squared loss would be exactly a scalar rewrite of the existing mean-squared loss. The evidence instead selects a linear hinge with a non-vanishing boundary gradient. This authorizes only its CPU mechanics contract.
