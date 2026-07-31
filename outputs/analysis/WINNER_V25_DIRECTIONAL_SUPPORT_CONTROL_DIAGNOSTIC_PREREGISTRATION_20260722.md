# Winner-v25 directional support-control diagnostic preregistration

- Status: `PREREGISTERED_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_SAME_STATE_DIRECTIONAL_DIAGNOSTIC_ONLY`
- Policies: Winner-v22 final source versus Winner-v24 half/final
- Population: `10` negative-X configurations x `2` plants
- Same-state forks: `800`; five-tick rollouts: `1,600`
- Optimizer / locomotion / robot: `0 / 0 / 0`

Did the failed symmetric terminal objective change the actor's action on an identical policy input in a direction that increases five-tick absolute torso pitch from the same cloned physical state?

The result chooses only between two later CPU evidence contracts. It cannot
authorize training, checkpoint selection, deployment, or robot access.
