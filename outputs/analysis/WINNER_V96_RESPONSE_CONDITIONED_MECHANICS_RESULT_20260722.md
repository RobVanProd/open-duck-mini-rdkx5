# Winner-v96 response-conditioned mechanics result

Status: `HOLD_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS`

JSON SHA-256: `5abba51f4ce65b672c6190e76a1dc79cdba02990fc0eadca4277dc2e74377a01`

The mechanism itself reproduced all four frozen Winner-v92 signed-response traces,
kept both calibration contexts separated above `0.155`, preserved bit-exact local
default-off behavior, rejected all invalid handoffs, and matched the independent
nonzero-adapter final-action composition exactly. Three assertions held the result:
a locally reconstructed calibrator limiter differed by `5.07e-7`; the moving golden
comparison required cross-host bit identity despite the frozen `1e-6` same-input
tolerance; and the stress boundary used `1e-7` while the protected graph itself
shows a `1.49e-7` float32 boundary excess. V96 remains recorded as a hold.

No optimizer update, hardware access, policy selection, deployment, or clearance
occurred.
