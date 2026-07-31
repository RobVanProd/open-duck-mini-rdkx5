# Winner-v4 Support Failure Diagnostic — 2026-07-20

status: `EXPLAINS_HOLD_NEGATIVE_ENDPOINT_INVERTED`

diagnostic JSON SHA-256: `acf5af92261fd4f15d69dcc212698d5726a2fb12aa8e17f7f3e1892139882e40`

completed formal result SHA-256: `b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730`

## Finding

This read-only diagnostic repeats only the 250-tick setup portion of the exact
frozen simulator scene. It runs no policy, PPO, behavior gate, runtime, or robot.
It does not retry or reclassify the completed response73 falsification.

At torso X = -0.05 m, the base finishes at Z =
`-0.156836729809` m with roll
`-3.139646185483` rad. Its absolute roll is only
`0.001946468107` rad from π. The model is
therefore inverted at the end of setup; its later two-foot contact and distinct
response73 values do not establish a valid standing calibration state.

At torso X = +0.05 m, the base finishes at Z =
`0.157214930575` m with roll
`0.000169244039` rad.

## Decision

The frozen free-body support mode is invalid across its requested signed-X
domain. Keep `DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73`. Any replacement support or
sign-preserving response mechanism requires a new prospective contract and
runtime review; this diagnostic authorizes none.
