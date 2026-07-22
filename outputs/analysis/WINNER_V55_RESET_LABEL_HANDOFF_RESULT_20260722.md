# Winner-v55 reset-label and handoff result

- Status: `PASS_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC`
- Classification: `NO_RESET_LABEL_CONFLICT`
- Decision: `CLOSE_RESET_CONFLICT_HYPOTHESIS_WITHOUT_TRAINING`
- Result SHA-256:
  `4ded36d436484af1b801d078a436b654d3aabc2507a26565117af3703008ed0e`.
- Reset input / teacher labels / graph actions: `15 / 4 / 15`
- Handoff support passes: `{"0": 12, "1": 4, "12": 0, "16": 0, "2": 4, "20": 0, "250": 0, "4": 2, "8": 1}`
- Selected positive handoff: `None`
- Optimizer / locomotion / robot: `0 / 0 / 0`

## Reset finding

The exact untransported float32 simulator inputs do not collide. Across the 15
teacher configurations, both plant rows share the same input within each
configuration, but the 15 configurations produce 15 distinct reset inputs and
15 distinct graph actions. Those inputs map to four distinct bounded V42
teacher actions. The preregistered raw-input collision hypothesis is therefore
closed.

This statement is deliberately limited to the exact core-simulator input used
by V55. The reset audit did not apply the support gate's separately declared
native BNO055/servo quantization. Before treating the 15 distinctions as
deployable information, a separate prospective attribution must test whether
native quantization preserves or collapses them. V55 is not reclassified.

## Handoff finding

The endpoint checks reproduce Winner-v54 bit-exactly: immediate full-teacher
control passes all `12/12`, while the unchanged graph endpoint passes `0/12`.
No positive handoff passes the complete population:

| First teacher tick | Support passes | Total |
| ---: | ---: | ---: |
| 0 | 12 | 12 |
| 1 | 4 | 12 |
| 2 | 4 | 12 |
| 4 | 2 | 12 |
| 8 | 1 | 12 |
| 12 | 0 | 12 |
| 16 | 0 | 12 |
| 20 | 0 | 12 |
| 250 | 0 | 12 |

Thus one graph action before teacher takeover is already causal to failure in
eight cells. The four cells surviving a one- or two-tick delay are not enough
to satisfy the frozen all-cell rule, and no closest handoff advances.

## Authority

All seven checks pass over exactly 30 reset rows and 108 handoff cells. The
audit performed zero optimizer updates, locomotion steps, graph exports, or
robot/RDK access. Robot clearance remains false. This result authorizes only a
separate CPU-only attribution of whether the raw reset distinctions survive
the already declared native sensor quantization.
