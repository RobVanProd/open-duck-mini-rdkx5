# Ground-Up Stage-One Mechanism Screen: Live Evidence

status: `RUNNING_REFERENCE_CONDITIONED`

The protected upstream control completed 8,028,160 seed-100 training steps and
was evaluated at 6,021,120 and 8,028,160 using the frozen CPU gate.

| candidate | artifact SHA-256 | full passes | moving passes | persistent moving seeds | hard failures | decision |
|---|---|---:|---:|---:|---:|---|
| `M0_UPSTREAM` | `25cbe9b418d87694f969a8cf37e1dbf137d04f4e33263d7fc9d00b7a3fcb3e5e` | 0 | 0 | 0 | 1 | eliminated |

At 8M, positive-command seed 101 has positive world displacement but negative
mean body-local forward velocity, so it is not a moving emergence pass. The
control does not meet the preregistered advancement rule.

`M1_REFCOND` is training. No cross-family ranking or winner exists yet.
Training reward is excluded. Evaluation used local CPU only; no local GPU,
RDK-X5, or robot access occurred.
