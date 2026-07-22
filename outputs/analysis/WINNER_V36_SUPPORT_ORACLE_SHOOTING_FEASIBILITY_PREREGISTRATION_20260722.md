# Winner-v36 support-oracle shooting feasibility preregistration

- Status: `PREREGISTERED_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_COM_X_NEG_SHOOTING_SCREEN`
- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`
- CEM population / elites / iterations: `64 / 8 / 4`
- Horizon / block: `8 / 2` ticks
- Controlled joints: six bilateral pitch-chain actions
- Optimizer updates / locomotion training / robot: `0 / 0 / 0`

Can a deterministic receding-horizon oracle keep the canonical -0.05 m torso-X anchor support-valid for all 250 ticks under the exact graph action bounds and both measured actuator plants?

This is a simulator-oracle controllability screen, not a deployable controller.
A pass can only authorize the full configuration matrix; a hold cannot be tuned.
