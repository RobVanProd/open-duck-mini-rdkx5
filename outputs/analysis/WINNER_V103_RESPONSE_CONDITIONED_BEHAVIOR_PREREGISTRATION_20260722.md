# Winner-v103 response-conditioned behavior preregistration

Status: `PREREGISTERED_WINNER_V103_RESPONSE_CONDITIONED_CPU_BEHAVIOR_AND_SELECTION_GATE`

This freezes the unchanged 1,024-cell variable-configuration matrix before any Winner-v102 training outcome exists. Each cell first performs 250 automatic-calibration ticks and 250 home-return ticks in the same simulated build and actuator plant, then scores exactly 600 locomotion ticks. Both half and final checkpoints must pass every cell; only then is the final checkpoint selected by its exact ONNX SHA-256. Training reward, a closest checkpoint, and post-outcome threshold changes have no selection weight.

No behavior cell is authorized until the hosted artifact and a separately hash-frozen zero-cell runner contract pass. No robot, RDK-X5, Gate 5, torque, motion, or grounded walking is authorized by this preregistration.
