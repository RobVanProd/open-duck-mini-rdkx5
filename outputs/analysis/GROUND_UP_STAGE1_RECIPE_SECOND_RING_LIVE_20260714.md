# Ground-Up Stage-One Recipe Second Ring: Live Evidence

status: `RUNTIME_LOSS_RESUME_UNFINISHED_ONLY`

The two preregistered discount candidates completed equal 8,028,160-step
training and frozen CPU evaluation at 6,021,120 and 8,028,160 steps.

| candidate | artifact SHA-256 | full passes | moving passes | hard failures | decision |
|---|---|---:|---:|---:|---|
| `S1DISC_LO` (`0.95`) | `105b509c2c2a3468de4fe695d21b0aea863bd876c410c76bd2eaee737ad3acf6` | 0 | 0 | 1 | eliminated |
| `S1DISC_HI` (`0.99`) | `4296b948e3000d3375b49d3a58655a1cbc55acc6a14f5eea6f0c710182714372` | 0 | 0 | 3 | eliminated |

`S1UNROLL_LO` also completed and was eliminated: zero full checkpoint passes,
one isolated moving pass, and three hard failures. Its artifact SHA-256 is
`23c89a22ec88b008d207a43fac4df9be09ecb1202b609655dc1210101fdff30c`.

The hosted runtime then lost its `/content` filesystem while the Colab service
still reported the session as BUSY. The local CLI process was interrupted and
the stale session stopped. The three completed artifacts were already
downloaded and verified. `S1UNROLL_HI` produced no recoverable artifact, so it
is the only candidate eligible for an isolated exact rerun. No completed
candidate will be repeated.

The center control currently ranks ahead with zero hard failures and one
nonpersistent moving pass. It is not a recipe winner. No final second-ring
ranking exists until `S1UNROLL_HI` completes or is formally unavailable.

Training reward is excluded. Evaluation used local CPU only. No local GPU,
RDK-X5, or robot access occurred.
