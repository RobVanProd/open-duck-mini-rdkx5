# Rate165 Hard-Vector Projection Feasibility Preregistration

status: `PREREGISTERED_OFFLINE_DIAGNOSTIC_ONLY`

Penalty BC and PPO both traded away motion before satisfying the independently
measured envelope. A distinct remaining feasibility question is whether the
unchanged rate165 trajectory survives exact per-joint rate projection itself.
This is an offline diagnostic, not a proposed runtime change or deployment.

Freeze rate165, fixed-target P30 bridge, x=.08 seed 0, home-support, 15 s, and
project only indices `2,3,4,11,12,13` at
`1.50,1.50,1.75,1.25,1.00,1.25 rad/s`. No sweep or tuning.

Pass requires duration/no-fall, zero p95/max excess, vx >=`0.0257 m/s`, ratio
>=`0.3213`, and single support >=`20%`. Failure closes hard rate projection and
shows the measured envelope is incompatible with this trajectory under the
current gate. Passing would authorize architecture work only, not hardware.

