# Winner-v24 GAE one-ULP attribution

- Status: `PASS_WINNER_V24_GAE_ONE_ULP_ATTRIBUTION`
- Decision: `AUTHORIZE_BASELINE_ANCHORED_SYMMETRIC_FAILURE_CPU_CONTRACT_ONLY`
- Return replay error / float32 ULP at 250: `1.52587890625e-05 / 1.52587890625e-05`
- Advantage replay error: `9.5367431640625e-07`
- Old result rewritten / threshold relaxed / new simulation: `false / false / false`
- Optimizer / robot: `0 / 0`

The correction must anchor to recorded baseline returns and apply only the
analytic terminal-reward delta. It cannot authorize an optimizer update.
