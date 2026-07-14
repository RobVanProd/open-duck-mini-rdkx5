# Ground-Up Stage-One Recipe Second Ring: Live Evidence

status: `RUNNING_UNROLL_CANDIDATES`

The two preregistered discount candidates completed equal 8,028,160-step
training and frozen CPU evaluation at 6,021,120 and 8,028,160 steps.

| candidate | artifact SHA-256 | full passes | moving passes | hard failures | decision |
|---|---|---:|---:|---:|---|
| `S1DISC_LO` (`0.95`) | `105b509c2c2a3468de4fe695d21b0aea863bd876c410c76bd2eaee737ad3acf6` | 0 | 0 | 1 | eliminated |
| `S1DISC_HI` (`0.99`) | `4296b948e3000d3375b49d3a58655a1cbc55acc6a14f5eea6f0c710182714372` | 0 | 0 | 3 | eliminated |

The center control currently ranks ahead with zero hard failures and one
nonpersistent moving pass. It is not a recipe winner. `S1UNROLL_LO` and
`S1UNROLL_HI` remain in progress; no final second-ring ranking exists yet.

Training reward is excluded. Evaluation used local CPU only. No local GPU,
RDK-X5, or robot access occurred.
