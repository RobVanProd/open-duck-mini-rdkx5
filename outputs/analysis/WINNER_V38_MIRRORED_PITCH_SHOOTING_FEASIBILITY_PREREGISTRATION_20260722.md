# Winner-v38 mirrored-pitch shooting feasibility preregistration

- Status: `PREREGISTERED_WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_MIRRORED_PITCH_COM_X_NEG_SCREEN`
- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`
- Search: `3` mirrored coordinates expanded to the same `6` pitch joints
- Frozen CEM population / elites / iterations: `64 / 8 / 4`
- Frozen horizon / block: `8 / 2` ticks
- Proposal: V36 cold start; no V37 plan memory
- Optimizer updates / locomotion training / robot: `0 / 0 / 0`

Can the unchanged cold-start bounded shooting controller hold the symmetric COM_X_NEG anchor when its six pitch-joint search is expressed in the reviewed three-dimensional bilateral mirror basis?

This is a simulator-oracle subspace falsification, not a deployable controller.
A pass can authorize only a negative-X teacher contract; a hold closes this route.
