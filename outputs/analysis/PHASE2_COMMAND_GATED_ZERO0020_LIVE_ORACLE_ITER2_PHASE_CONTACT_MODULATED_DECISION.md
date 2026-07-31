# Phase/Contact-Modulated Live-Oracle Iter2 Decision

status: `HOLD_PHASE_CONTACT_MODULATED_MOVING_GATE`

This is an offline analysis result. It did not train PPO, deploy, SSH, run
robot tests, or change robot runtime behavior.

## Candidate

- source manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- student ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_phase_contact_modulated_bc_student/candidate.onnx`
- architecture: shared trunk with command/contact/phase modulation
- context indices: `[6, 97, 98, 99, 100]`
- samples: `11555`
- fit p95 abs error: `0.009653`
- target-rate p95: `1.232130 rad/s`
- ONNX max abs verification error: `0.00000006`

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
```

Result:

```text
x=0.08 compact gate: 2/5 pass
passes: seeds 1,7
falls: seeds 0,2,6
corrected p95 velocity excess: 0.0 rad/s on all seeds
mean track ratio: 1.0931
mean local vx: 0.0874 m/s
mean body pitch p95: 0.5699 rad
```

| seed | status | samples | mean vx | track ratio | body pitch p95 | base height min | max pitch vel p95 | max tracking p95 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `0` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 161 | 0.1343 | 1.6787 | 0.9100 | -0.0054 | 1.6523 | 0.1976 |
| `1` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0288 | 0.3598 | 0.1804 | 0.1568 | 1.6535 | 0.1917 |
| `2` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 158 | 0.1333 | 1.6668 | 0.8726 | 0.0054 | 1.6714 | 0.2003 |
| `6` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 207 | 0.1128 | 1.4105 | 0.7205 | -0.0031 | 1.6137 | 0.1932 |
| `7` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0280 | 0.3495 | 0.1660 | 0.1568 | 1.6489 | 0.1852 |

## Decision

The phase/contact-modulated student is not a valid Phase 2 warm start. It
preserves corrected velocity-envelope compliance, but it regresses the moving
gate from the live-oracle PPO-loc `4/5` result to `2/5` and converts the
remaining failures into high-forward-velocity lunge/fall cases.

Do not run the `x=0.0` command-semantics gate or launch domain-randomized PPO
from this candidate. The moving gate already rejects it.

This closes the simple feed-forward phase/contact modulation rung for the
current live-oracle iter2 aggregate. The remaining trainable-parent gap is a
closed-loop stability/branching problem, not target-rate compliance or local BC
fit.

Recommended next branch: use the passing graph command-gated parent as the
eval oracle/source, but move the trainable parent search to a stronger
branch-aware structure, recurrent/hidden-state export, or an on-policy
objective that directly preserves the compact rough+push closed-loop gate.
