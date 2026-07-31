# Winner-v39 response-Jacobian feasibility preregistration

- Status: `PREREGISTERED_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_RESPONSE_JACOBIAN_COM_X_NEG_SCREEN`
- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`
- Response: signed base pitch + body pitch rate at tick `8`
- Control basis: mirrored hip-pitch magnitude / knee / ankle
- Perturbation: exact minimum paired graph delta
- Solver: deterministic minimum-norm least squares; one-step correction bound
- Optimizer updates / locomotion training / robot: `0 / 0 / 0`

Can deterministic local model-based feedback hold COM_X_NEG by measuring the exact eight-tick pitch/pitch-rate response Jacobian of the reviewed mirrored pitch coordinates and applying one minimum-norm correction per tick?

This is a simulator-oracle controller-family test, not a deployable controller.
A pass can authorize only a teacher contract; a hold closes the exact controller.
