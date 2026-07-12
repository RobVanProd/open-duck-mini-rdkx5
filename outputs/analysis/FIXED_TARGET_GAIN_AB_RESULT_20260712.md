# Fixed-target gain A/B result

Date: 2026-07-12

Status: `REJECT_P31_34_GAIN_ROUTE`

The exact same 747-target, 50 Hz suspended x=0.08 sequence was replayed at
normal P30 and at left hip/knee P31/34. Policy and IMU feedback were disabled.

| joint | P30 p95 | P31/34 p95 | improvement |
|---|---:|---:|---:|
| left hip pitch | 0.04972 | 0.04939 | 0.66% |
| left knee | 0.05585 | 0.05190 | 7.06% |

Both phases completed 747 samples with zero read, write, or transport errors.
Normal gains were restored and torque disabled after and between phases.

The frozen rule required at least 10% p95 improvement on both joints and no
greater than 10% regression in any-joint p95/max. It failed both requirements:

- left knee max increased 15.00%;
- neck pitch max increased 32.89%;
- head roll max increased 26.33%;
- head yaw max increased 16.14%;
- right hip pitch max increased 11.73%.

P31/34 therefore has a small causal knee benefit but is not an acceptable fix.
Close this exact gain route and do not increase gains post hoc. Physical
alignment remains rejected because signed errors reverse through the gait.

The remaining supported class is target-trajectory shaping evaluated offline
against motion preservation before any hardware consideration, not servo gain
or offset changes.

Rob reported no visible difference between the two phases. This agrees with the
sub-threshold p95 effect and closes the visual review without changing the
rejection.

Evidence hashes:

```text
summary:  549cafc4cced4e5aa71112888cb219bb66dc58cd9d9b4b2323bbf83a367700ae
JSONL:    2233821203a6b799ce472dbc4e043fd89f7543b3dc44823e4b930d45f77414ad
terminal: 504c512ace6c39d7965163d5af04d556230600c29f10683c73ca5703cd7e5711
```
