# Ground-Up Objective/Gate Mismatch Audit

status: `PASS_OBJECTIVE_GATE_MISMATCH_AUDIT`
measured mechanism: `NO_UNIQUE_OBJECTIVE_GATE_MECHANISM`

## 2M minus 1M error change

- projected reference→actual RMS: `+0.00896800 rad`
- reward reference→actual RMS: `+0.00583613 rad`
- sent target→actual RMS: `-0.00071690 rad`
- applied target→actual RMS: `+0.00007794 rad`
- sent target→projected reference RMS: `+0.00926443 rad`
- sent target→reward reference RMS: `+0.00647072 rad`

The actor feature uses the velocity-projected reference. The imitation
reward uses the unprojected polynomial joint positions, reconstructed here
by reversing the frozen per-command projection scale. A negative reward-
reference-to-actual change means realized motion became closer to the exact
joint-position target optimized by imitation.

## Largest joint-level sent-target tracking changes

| joint | reward ref→actual RMS Δ | sent→actual RMS Δ | sent→reward ref RMS Δ |
|---|---:|---:|---:|
| left_hip_yaw | +0.00831230 | +0.01040244 | +0.00537664 |
| right_knee | +0.00112780 | +0.00661727 | +0.00174588 |
| right_hip_roll | +0.00721065 | +0.00420188 | +0.00932980 |
| left_hip_roll | +0.01421204 | +0.00347989 | +0.01031145 |
| right_hip_pitch | +0.00108161 | +0.00213160 | +0.00104731 |
| right_hip_yaw | +0.01648007 | +0.00168001 | +0.01660946 |

## Decision boundary

This audit does not identify a unique objective/gate mechanism.
It does not select a penalty scale, authorize training, or weaken the
frozen hardware tracking gate. Any next causal arm requires separate
preregistration and a CPU transition/reward contract.
