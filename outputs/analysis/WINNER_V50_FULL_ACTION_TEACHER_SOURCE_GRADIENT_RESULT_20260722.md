# Winner-v50 full-action teacher source-gradient result

- Status: `HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF`
- Decision: `DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY`
- Formal rollout: `80 x 250 ticks` at Winner-v46 update `352`
- Optimizer updates / support cells / exports / robot access: `0 / 0 / 0 / 0`
- Result SHA-256: `7f1a6ae01ba9aaf01766ccbdaa6246c0aa2629e04a2e695e1425a45e858b79b1`

All source, rollout, action-boundary, teacher-population, mask, gradient-scope,
default-off, finite-value, and no-mutation checks passed. The full-action
replacement changed every policy-gradient leaf and preserved every non-policy
leaf bit-exactly.

The only failed checks were the preregistered absolute direct-versus-composed
gradient limits. Both the old and new objective measured exactly
`4.76837158203125e-6`, above the frozen `4e-6` threshold. This result remains a
formal hold. It does not authorize an optimizer update. Any arithmetic-order
review must be separately preregistered and use a derived numerical rule rather
than modifying this result after observation.
