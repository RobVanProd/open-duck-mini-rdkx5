# Ground-Up Stage-One Recipe Second-Ring Result

status: `NO_SCALAR_RECIPE_WINNER`

The final one-factor scalar PPO ring is complete. All four new candidates were
trained from scratch with seed 100 to 8,028,160 steps and evaluated at 6,021,120
and 8,028,160 steps using the frozen 1.08-second CPU gate. The center evidence
was reused. Training reward was excluded.

| rank | candidate | full passes | finite x=0 | moving passes | persistent moving seeds | hard failures |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `S1C` | 0 | 4 | 1 | 0 | 0 |
| 2 | `S1DISC_LO` (`0.95`) | 0 | 4 | 0 | 0 | 1 |
| 3 | `S1UNROLL_LO` (`10`) | 0 | 3 | 1 | 0 | 3 |
| 4 | `S1DISC_HI` (`0.99`) | 0 | 3 | 0 | 0 | 3 |
| 5 | `S1UNROLL_HI` (`40`) | 0 | 3 | 0 | 0 | 4 |

None meets the preregistered advancement condition: a full checkpoint pass or
the same moving seed passing at both checkpoints with zero hard failures. The
center remains only the protected control; it is not a gait recipe and is not
`BEST_RECIPE_TESTED`.

## Artifact evidence

| candidate | training seconds | artifact SHA-256 |
|---|---:|---|
| `S1DISC_LO` | `1424.168724955` | `105b509c2c2a3468de4fe695d21b0aea863bd876c410c76bd2eaee737ad3acf6` |
| `S1DISC_HI` | `938.657565255` | `4296b948e3000d3375b49d3a58655a1cbc55acc6a14f5eea6f0c710182714372` |
| `S1UNROLL_LO` | `944.0902889250001` | `23c89a22ec88b008d207a43fac4df9be09ecb1202b609655dc1210101fdff30c` |
| `S1UNROLL_HI` | `1382.833061935` | `8018a0bcf5b6045a55c1e5aa6073c0188dce251bee7fdfdaf8ae25f7d0b1233a` |

The first three candidates completed in one sweep. The hosted runtime then
lost `/content` while reported BUSY. Their artifacts had already been recovered.
Only the unfinished unroll-40 candidate was rerun in isolation; it completed
with the same frozen recipe. All Colab sessions were stopped after recovery.

## Decision

Learning rate, entropy, imitation scale, discount, and unroll length have now
all been bracketed one factor at a time around the center without producing a
persistent gait. Scalar PPO recipe search is closed. No second-training-seed
replication, post-hoc factor combination, or further scalar tuning is
authorized by this result.

The next evidence question is structural: whether a preregistered policy
mechanism or revised reference curriculum can make the closed-loop policy
learn persistent forward gait under the same hardware/evaluator contract. A
new amendment must define that fair comparison before additional compute.

No policy, RDK-X5 runtime, or robot use is cleared.
