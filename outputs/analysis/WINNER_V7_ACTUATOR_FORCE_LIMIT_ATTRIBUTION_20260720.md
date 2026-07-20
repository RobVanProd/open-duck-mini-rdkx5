# Winner-v7 Actuator Force-Limit Attribution

Status: `HOLD_WINNER_V7_ACTUATOR_FORCE_LIMIT_ATTRIBUTION`

Decision: `CLOSE_PHYSICAL_FORCE_LIMIT_ATTRIBUTION_ROUTE`

- traces replayed: `128` (`96` moving, `32` x=0)
- peak-current failures: `96`
- peak-torque failures: `96`
- simulator force limit: `3.23` N.m
- frozen physical force limit: `1.91229675` N.m
- worst peak: `4.117104234210315` A at `head_roll` tick `28`

The closed winner-v7 result is unchanged. This read-only audit may select only a distinct, default-off simulator force-limit contract; it does not authorize a behavior rerun, training, deployment, robot access, torque, motion, or Gate 5.
