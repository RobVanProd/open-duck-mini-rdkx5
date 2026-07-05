# Recurrent Live-Oracle Iter2 Decision

status: `HOLD_RECURRENT_BC_OVER_ENVELOPE_COLLAPSE`

This is an offline stateful-ONNX diagnostic. It did not train PPO, deploy,
SSH, run robot tests, or change robot runtime behavior.

## Candidate

- source manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- recurrent ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_recurrent_h64_s32_bc_student/candidate.onnx`
- recurrent NPZ: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_recurrent_h64_s32_bc_student/candidate_rnn.npz`
- contract: `obs[1,101], h_in[1,64] -> continuous_actions[1,14], h_out[1,64]`
- sequence length: `32`
- samples: `11555`
- fit p95 abs error: `0.015230`
- target-rate p95 during fit: `1.215406 rad/s`
- ONNX max action error: `0.00000051`

This export is not robot-deployable without a reviewed hidden-state runtime
adapter. It was used only to test whether explicit recurrent state improves
the compact corrected-bridge sim gate.

## Gate

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
reset_mode: home-support
reset_settle_ticks: 10
bridge: fitted corrected bridge
command_x: 0.08
pushes: 0.075-0.125, interval 1.0-1.5s
seeds: 0,1,2,6,7
stateful ONNX flags: obs,h_in -> continuous_actions,h_out
```

Result:

```text
x=0.08 compact gate: 0/5 pass
all seeds fall at 57 samples
mean local vx: -0.3345 m/s
mean track ratio: -4.1817
max pitch-chain p95 velocity: 5.2400 rad/s
corrected p95 velocity excess: 3.2400 rad/s
max tracking p95: 0.2746 rad
```

| seed | status | samples | mean vx | track ratio | max pitch vel p95 | p95 velocity excess | max tracking p95 |
|---:|---|---:|---:|---:|---:|---:|---:|
| `0` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.3346 | -4.1824 | 5.2400 | 3.2400 | 0.2746 |
| `1` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.3346 | -4.1820 | 5.2400 | 3.2400 | 0.2746 |
| `2` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.3346 | -4.1820 | 5.2400 | 3.2400 | 0.2746 |
| `6` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.3344 | -4.1794 | 5.2400 | 3.2400 | 0.2746 |
| `7` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | -0.3346 | -4.1824 | 5.2400 | 3.2400 | 0.2746 |

## Decision

Do not use this recurrent BC student as a Phase 2 warm start. It is worse than
the feed-forward live-oracle PPO-loc result and worse than the phase/contact
modulated diagnostic: it collapses all compact moving seeds, moves backward,
and immediately violates the corrected actuator envelope.

This closes plain supervised recurrent BC for the current live-oracle iter2
aggregate. The trainable-parent blocker is not solved by adding hidden state to
the same BC objective. The next branch should be a gate-aware/on-policy
behavior-preservation objective or an explicit branch/router mechanism that is
trained against closed-loop gate outcomes, not another one-shot BC compression
of the same aggregate.
