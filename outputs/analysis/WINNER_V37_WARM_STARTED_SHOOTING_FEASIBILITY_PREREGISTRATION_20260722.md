# Winner-v37 warm-started shooting feasibility preregistration

- Status: `PREREGISTERED_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_WARM_STARTED_COM_X_NEG_SCREEN`
- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`
- V36 comparator terminal ticks: `55 / 52`
- Frozen CEM population / elites / iterations: `64 / 8 / 4`
- Frozen horizon / block / controlled joints: `8 / 2 / six pitch-chain`
- One change: shift the previous winning plan into the next proposal mean
- Optimizer updates / locomotion training / robot: `0 / 0 / 0`

Does preserving the prior winning plan as the next CEM proposal mean repair V36's cold-start planning discontinuity without changing its controller authority, compute, objective, horizon, action set, or physical gate?

This is a simulator-oracle mechanism falsification, not a deployable controller.
A pass can authorize only a full configuration screen; a hold closes this route.
