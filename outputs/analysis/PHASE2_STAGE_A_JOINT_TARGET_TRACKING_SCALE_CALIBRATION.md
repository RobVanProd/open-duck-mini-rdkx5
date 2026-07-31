# Stage A Joint-Target Tracking Scale Calibration

Status: **PASS_DATA_CALIBRATED_SCALE**

| trace | bridge cost mean | pitch actual-tracking cost mean | ratio | equal scale |
|---|---:|---:|---:|---:|
| `x0` | 0.00025041 | 0.00127193 | 5.079 | -0.007875 |
| `x008` | 0.00027432 | 0.00137936 | 5.028 | -0.007955 |

Registered scale: **`-0.007915`** with pseudo-Huber delta `0.03` on pitch indices `[2, 3, 4, 11, 12, 13]`.

Mean across the preregistered x=0 and x=0.08 compact traces of the scale that gives the new pitch-chain cost the same mean absolute reward contribution as the existing all-joint bridge-tracking cost.

This calibration prevents choosing a reward scale by outcome fishing. It does not authorize training, deployment, robot access, or GPU use.
