# Tracking Gate Fixed-Window Audit

Status: **PASS_TRACKING_WINDOW_AUDIT_READY**

| window | tracking p95 max | joint | vx | ratio | <=0.20 |
|---|---:|---|---:|---:|---:|
| 0.0-1.0s | 0.2478 | `left_knee` | 0.0390 | 0.487 | `False` |
| 1.0-2.0s | 0.1961 | `left_knee` | 0.0265 | 0.331 | `True` |
| 2.0-3.0s | 0.1813 | `right_knee` | 0.0402 | 0.503 | `True` |
| 3.0-4.0s | 0.1979 | `left_knee` | 0.0372 | 0.465 | `True` |
| 4.0-5.0s | 0.1860 | `right_knee` | 0.0263 | 0.328 | `True` |
| 5.0-6.0s | 0.1959 | `left_knee` | 0.0420 | 0.526 | `True` |
| 6.0-7.0s | 0.1788 | `right_knee` | 0.0438 | 0.548 | `True` |
| 7.0-8.0s | 0.1945 | `left_knee` | 0.0347 | 0.434 | `True` |
| 8.0-9.0s | 0.2016 | `left_knee` | 0.0276 | 0.345 | `False` |
| 9.0-10.0s | 0.1976 | `left_knee` | 0.0415 | 0.519 | `True` |
| 10.0-11.0s | 0.1902 | `left_knee` | 0.0309 | 0.386 | `True` |
| 11.0-12.0s | 0.1918 | `right_knee` | 0.0305 | 0.381 | `True` |
| 12.0-13.0s | 0.2030 | `left_knee` | 0.0346 | 0.432 | `False` |
| 13.0-14.0s | 0.1828 | `left_knee` | 0.0363 | 0.454 | `True` |
| 14.0-15.0s | 0.1850 | `left_knee` | 0.0391 | 0.488 | `True` |

- startup window fails: `True`
- every later complete window passes: `False`

## Decision

Do not change the compact gate from this single-seed audit. Use the result only to distinguish reset/startup tracking from steady-state tracking and define an independent gate-validity study before further policy training.

No gate, training, deployment, robot, SSH, or GPU change was performed.
