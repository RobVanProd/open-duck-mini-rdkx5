# Rate165 Hardware-Calibrated Per-Joint Refit Preregistration

status: `PREREGISTERED_OFFLINE_ONLY`

The fixed-target P30/P31-34 fits independently select stable 2-3 tick delays
and cross-predict all six pitch-chain responses at p95 `0.0074-0.0127 rad`.
The P30 effective velocity limits are `[1.50,1.50,1.75,1.25,1.00,1.25] rad/s`
for left hip/knee/ankle and right hip/knee/ankle. The older bridge used
`[2.50,3.25,2.75,2.25,2.75,2.00]`.

Against the fixed-target bridge, unchanged rate165 completes 15 s and retains
motion (`vx=0.0257 m/s`, ratio `0.3213`) but correctly holds for per-joint
velocity excess. This supports one full-length refit, not a parameter sweep.

Frozen fit: original rate165 manifest, architecture, context, seed 2, 7000
steps, global scale 0.2, and per-action limits
`1.65,1.65,1.50,1.50,1.75,1.65,1.65,1.65,1.65,1.65,1.65,1.25,1.00,1.25`.
No phase-local penalty is used.

Pass requires unchanged fixed-target-bridge x=.08 duration/no-fall, zero p95
and max velocity excess, vx >=0.0257, ratio >=0.3213, single support >=20%,
and x=0 stillness/duration with max pitch-chain p95 <=0.07 rad/s. Failure
closes this exact refit without tuning. Colab, deployment, robot motion, and
grounded replay remain unauthorized.
