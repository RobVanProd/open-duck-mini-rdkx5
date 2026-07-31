# Winner-v118 nominal failure attribution

Status: `PASS_WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION`

Decision: `PREREGISTER_V119_DEFAULT_OFF_AND_CPU_TRANSITION_CONTRACT`

V117 to V118 tightened the same four final rate caps, but the half checkpoint fell from 3/8 to 2/8 and both worst current and torque increased. Repeating output-only tightening is closed. V114 trained under the older vector without the deployed G3/final projection, so the next mechanism is an exact train/deploy transition match. This artifact authorizes only a default-off CPU contract, not training.
