# Published Policy Command Propulsion Comparison

status: `PASS_POLICY_COMMAND_PROPULSION_COMPARISON`

This is an offline sim analysis. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Command Comparison

| label | command | status | complete | moving | weak | envelope_safe_3p75 | mean_vx | track_ratio | single_% | double_% | single_dvx_0p1s | pitch_sent_p95_max | fastest_joint_counts | body_pitch_p95 | height_min |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| straight_x004 | `x=0.04 y=0 yaw=0` | `WARN_POLICY_FORWARD_MOTION_WEAK_SEEDS` | 8/8 | 0 | 8 | 8/8 | 0.0019 | 0.0468 | 3.6500 | 96.1000 | -0.0155 | 2.9633 | `{'left_knee': 5, 'right_knee': 3}` | 0.0394 | 0.1520 |
| upstream_nearest_turn | `x=0.074 y=-0.037 yaw=-0.074` | `PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION` | 8/8 | 7 | 1 | 1/8 | 0.0540 | 0.7294 | 44.8000 | 54.9500 | 0.0042 | 5.2400 | `{'right_knee': 7, 'left_knee': 1}` | 0.0650 | 0.1523 |
| straight_x008 | `x=0.08 y=0 yaw=0` | `PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION` | 8/8 | 7 | 1 | 0/8 | 0.0640 | 0.7998 | 49.4000 | 50.3500 | 0.0030 | 5.2400 | `{'right_knee': 8}` | 0.0646 | 0.1523 |

## Source Artifacts

- straight_x004: `outputs/analysis/published_policy_propulsion_x004_straight_audit.json`
- upstream_nearest_turn: `outputs/analysis/published_policy_propulsion_audit.json`
- straight_x008: `outputs/analysis/published_policy_propulsion_x008_straight_audit.json`

## Interpretation

- Published BEST_WALK closed-loop propulsion is strongly command-dependent.
- Straight x=0.04 completes but does not walk: 0/8 seeds reach track ratio >= 0.5, mean vx is about 0.002 m/s, the policy remains in double support about 96% of the time, and all seeds stay below the 3.75 rad/s pitch-chain p95 envelope.
- Straight x=0.08 does walk in sim: 7/8 seeds reach track ratio >= 0.5 and mean vx is about 0.064 m/s, but 0/8 seeds stay within the 3.75 rad/s pitch-chain p95 envelope; right_knee reaches the 5.24 rad/s slew ceiling on most seeds.
- The upstream nearest turning command also walks: 7/8 moving seeds and mean vx about 0.054 m/s, but only 1/8 seeds stay within the 3.75 rad/s pitch-chain p95 envelope, and that seed is the weak moving seed.
- This means straight x=0.04 was not a proven-easy walking gate; even the published walking policy mostly stands there.
- It also means the published policy does not currently prove stable in-envelope walking at the moving command cells tested here. It proves closed-loop walking exists in sim, but walking uses right-knee target rates near or above the measured actuator envelope.
- The next training/eval re-entry should not grade first on straight x=0.04 walking. It should either start from a command cell where BEST_WALK actually moves and explicitly reduce right-knee rate, or use x=0.04 as a no/low-motion posture gate rather than an existence proof for walking.
- No robot motion, SSH, deploy, runtime behavior change, or training was performed.

recommended_next: `extract CoM-over-stance and contact timing from straight x=0.08 and the upstream-nearest turning command, compare against straight x=0.04, and treat right-knee target-rate reduction as part of the mechanism rather than assuming BEST_WALK is already in-envelope.`
