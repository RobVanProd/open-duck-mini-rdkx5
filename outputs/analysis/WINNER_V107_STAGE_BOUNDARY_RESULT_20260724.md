# Winner-v107 stage-boundary result

Status: `PASS_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC`
Decision: `EXPANDED_INITIAL_FAILED`
Selected causal boundary: `EXPANSION_EXPORT_OR_CALIBRATION_PREFIX_INTEGRATION`

| checkpoint | cells | pass | all pass | worst tracking | worst current | minimum moving vx |
|---|---:|---:|---|---:|---:|---:|
| EXPANDED_INITIAL | 4 | 1 | `False` | 0.2230566572397947 | 2.821194296117594 | 0.08592694875662346 |
| AFTER_DOMAIN_25_PERCENT | 4 | 1 | `False` | 0.20022793896496296 | 2.3789132629607073 | 0.03959618823032239 |
| AFTER_DOMAIN_50_PERCENT | 4 | 1 | `False` | 0.18748373109847308 | 1.7346619731871198 | 0.0026519056612778515 |
| DOMAIN_100_PERCENT_HALF | 4 | 1 | `False` | 0.18736044112592934 | 1.8143697266422272 | 0.002987910007244257 |
| DOMAIN_100_PERCENT_FINAL | 4 | 1 | `False` | 0.15645381137728692 | 2.0832994120332744 | 0.004010348768976352 |

This diagnostic localizes a causal boundary only. It cannot select a deployment checkpoint, authorize training, open Gate 5, or clear the policy for any robot action.
