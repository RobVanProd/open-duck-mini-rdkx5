# Servo CRC Localization

status: `LOCALIZED_ID13_SIGNAL_INTEGRITY_SUSPECT`

| run | samples | CRC | rate | servo IDs | battery samples |
|---|---:|---:|---:|---|---:|
| `home` | 205 | 3 | 1.46% | `{'13': 3}` | 0 |
| `x0` | 747 | 7 | 0.94% | `{'13': 7}` | 0 |
| `x008` | 747 | 25 | 3.35% | `{'13': 25}` | 0 |

## Findings

- All logged corrupt responses localize to servo IDs ['13'].
- Runtime mapping identifies servo ID 13 as right_knee.
- CRC XOR masks affect high checksum bits, led by 0x80 and 0xc0; retries recover.
- Events are distributed across gait quadrants and are not concentrated at peak right-knee target speed.
- No run captured battery voltage, so voltage sag remains untested.
- Localization supports inspecting/polling the ID-13 servo and adjacent bus segment before any policy repeat.

## Event-Window Comparisons

### home

phase_quadrants: `[3, 0, 0, 0]`

| metric | event ±2 median | non-event median |
|---|---:|---:|
| `right_knee_target_velocity_rad_s` | 0.00000 | 0.00000 |
| `right_knee_tracking_abs_rad` | 0.00300 | 0.00300 |
| `max_pitch_tracking_abs_rad` | 0.00500 | 0.00500 |
| `accel_xy_m_s2` | 1.69650 | 1.70520 |
| `dt_s` | 0.05230 | 0.04941 |

### x0

phase_quadrants: `[2, 2, 0, 3]`

| metric | event ±2 median | non-event median |
|---|---:|---:|
| `right_knee_target_velocity_rad_s` | 0.03947 | 0.02497 |
| `right_knee_tracking_abs_rad` | 0.00196 | 0.00081 |
| `max_pitch_tracking_abs_rad` | 0.00750 | 0.00786 |
| `accel_xy_m_s2` | 1.67443 | 1.66397 |
| `dt_s` | 0.02009 | 0.02009 |

### x008

phase_quadrants: `[7, 7, 5, 4]`

| metric | event ±2 median | non-event median |
|---|---:|---:|
| `right_knee_target_velocity_rad_s` | 0.27444 | 0.29950 |
| `right_knee_tracking_abs_rad` | 0.01013 | 0.00915 |
| `max_pitch_tracking_abs_rad` | 0.03588 | 0.03011 |
| `accel_xy_m_s2` | 1.85970 | 1.85270 |
| `dt_s` | 0.02009 | 0.02009 |
