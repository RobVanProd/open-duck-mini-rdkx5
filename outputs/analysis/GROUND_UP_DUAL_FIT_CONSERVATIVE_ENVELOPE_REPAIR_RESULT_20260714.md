# Ground-Up Dual-Fit Conservative-Envelope Repair Result

status: `PASS_DUAL_FIT_CONSERVATIVE_ENVELOPE_REPAIR`
decision: `REENTER_R1_PASS_AND_AUTHORIZE_R2_CONTRACT_ONLY`

| fit | step | x=0 | nominal | worst tracking | min vx | pass |
|---|---:|---|---|---:|---:|---|
| `p30` | 512000 | `True` | `True` | 0.180855995 | 0.086461715 | `True` |
| `p30` | 1024000 | `True` | `True` | 0.183170038 | 0.097619724 | `True` |
| `p31_34` | 512000 | `True` | `True` | 0.178732973 | 0.084911748 | `True` |
| `p31_34` | 1024000 | `True` | `True` | 0.181057256 | 0.096040766 | `True` |

The componentwise conservative measured envelope removes the P31/34 left-ankle violation while preserving both checkpoints under both hardware fits.

Passing authorizes only the R2 evaluator contract. It does not authorize R2 behavior, training, RDK-X5, or robot access.
