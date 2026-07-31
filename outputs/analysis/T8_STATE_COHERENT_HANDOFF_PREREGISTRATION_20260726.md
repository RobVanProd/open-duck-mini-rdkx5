# T8 state-coherent support-to-locomotion handoff preregistration

- Status: `PREREGISTERED_T8_STATE_COHERENT_HANDOFF`
- Contract SHA-256: `548a0b1cd5967e1e0976871a01983996b48bed5b43619969eaa5c472b2cbe7ce`
- Cells: `16` (`2 checkpoints × 2 fits × 4 commands`)
- Training: `0 steps`
- Robot/RDK-X5 access: `forbidden`

## Question

Can both frozen V121 checkpoints, under both measured actuator fits, hand off directly from the T7-proven universal support prefix into the complete nominal 600-tick command matrix without training?

## Frozen boundary

Each cell runs 250 unscored universal-support ticks and then starts V121 locomotion immediately. There is no zero-action home return. The final support action becomes `previous_action`; the applied-target observer is preserved; policy hidden state starts at zero; phase resets to `[1, 0]`; and the response context is finite and immutable.

The context input is intentionally unused by these bit-exact diagnostic wrappers. T8 therefore asks only whether a state-coherent physical handoff is viable before any actor continuation is considered.

## Decision

- Pass: earn one separately preregistered CPU software contract for a response-conditioned continuation initialized at V121-half; do not authorize hosted training.
- Fail: close direct zero-training handoff of the V121 pair and analyze the transition failure before proposing any new mechanism; do not train.

A pass does not authorize hosted training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.
