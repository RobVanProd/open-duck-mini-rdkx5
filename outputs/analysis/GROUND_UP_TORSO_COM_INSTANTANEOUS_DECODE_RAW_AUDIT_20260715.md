# Ground-Up Torso-COM Instantaneous Decode Raw Audit

status: `PASS_INSTANTANEOUS_IMU_COM_DECODE_RAW_AUDIT`

| class | samples | unique tick-0 vectors | gyro xyz | accelerometer xyz |
|---|---:|---:|---|---|
| `NEG` | 48 | 1 | `[0.0, 0.0, 0.0]` | `[-13.04679012298584, 0.7727481126785278, 28.672449111938477]` |
| `NOMINAL` | 48 | 1 | `[0.0, 0.0, 0.0]` | `[-11.879271507263184, 0.8971166610717773, 29.650177001953125]` |
| `POS` | 48 | 1 | `[0.0, 0.0, 0.0]` | `[-10.715840339660645, 1.0117170810699463, 30.856430053710938]` |

The instantaneous classification is carried by the exact tick-zero accelerometer, not gyro, and is invariant across arm, checkpoint, fit, and command within each COM class.

This selects no memory architecture and authorizes no training. It supports only a separately preregistered objective/exploitation study.
