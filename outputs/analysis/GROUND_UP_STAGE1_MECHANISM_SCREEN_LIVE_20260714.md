# Ground-Up Stage-One Mechanism Screen: Live Evidence

status: `RERUNNING_SYMMETRIC_CRITIC_AFTER_SECOND_RUNTIME_LOSS`

The protected upstream control completed 8,028,160 seed-100 training steps and
was evaluated at 6,021,120 and 8,028,160 using the frozen CPU gate.

| candidate | artifact SHA-256 | full passes | moving passes | persistent moving seeds | hard failures | decision |
|---|---|---:|---:|---:|---:|---|
| `M0_UPSTREAM` | `25cbe9b418d87694f969a8cf37e1dbf137d04f4e33263d7fc9d00b7a3fcb3e5e` | 0 | 0 | 0 | 1 | eliminated |
| `M1_REFCOND` | `67ad6b1ba3786f6e2dff46b8eeee71b6ddca771236754c6b23f11fd998d576b0` | 0 | 1 | 0 | 2 | eliminated |
| `M2_PHASE_MOE` | `e401f7a65ff7e9b3fa57dc0f4782582a16b6d72d5c8c1630fcdfdd422a8c1583` | 0 | 0 | 0 | 2 | eliminated |
| `M3_RECURRENT` | `17ba25bcf9cef9b21691e284dcb67661a16522e032c00eb60a748721803d9af7` | 0 | 0 | 0 | 4 | eliminated |

At 8M, positive-command seed 101 has positive world displacement but negative
mean body-local forward velocity, so it is not a moving emergence pass. The
control does not meet the preregistered advancement rule.

The reference-conditioned family produces one isolated moving pass at 8M
seed 100, but it is not persistent and that checkpoint has two hard failures.
It does not meet the advancement rule.

The hosted runtime lost its entire `/content` filesystem while Colab still
reported the session as BUSY. `M0_UPSTREAM` and `M1_REFCOND` artifacts were
already downloaded and verified. `M2_PHASE_MOE` had only partial remote
checkpoints and no completed archive, so it has no behavior evidence.

The stale client was interrupted and the session stopped. The exact phase-MoE
rerun completed on a fresh runtime, but produced zero moving passes and two
hard failures. It does not meet the advancement rule.

The recurrent policy's stateful `h_in -> h_out` evaluator contract worked, but
the learned behavior produced four hard failures and zero moving passes. It
does not meet the advancement rule.

The second hosted runtime also lost its entire `/content` filesystem while
Colab still reported the execution as BUSY. `M2_PHASE_MOE` and `M3_RECURRENT`
artifacts had already been downloaded and verified. `M4_SYMCRIT` had partial
remote checkpoints but no completed archive, so it has no behavior evidence
from that interrupted attempt. The stale execution was interrupted and the
session stopped.

`M4_SYMCRIT` is being rerun exactly, by itself. No completed candidate is being
repeated and no recipe value has changed. No final cross-family ranking or
winner exists yet.
Training reward is excluded. Evaluation used local CPU only; no local GPU,
RDK-X5, or robot access occurred.
