# Phase 2 Stage A On-Policy Continuity Recipe

status: `PASS_ONPOLICY_CONTINUITY_RECIPE_PRE_REGISTERED_DATA_GATE_OPEN`
training_authorized: `False`
robot_authorized: `False`

This is an offline pre-registration artifact. It did not train, deploy, SSH, use a local GPU, or touch the robot.

## Diagnosis

- Stage A best step: `163840`
- compact x=0.08: vx `0.0298` m/s, ratio `0.3724`, tracking p95 `0.2177` rad
- seed-0 full-observation tracking p95: `0.2384` rad
- on-policy teacher delta mean/p95: `0.019652692017934445` / `0.05240445968750864` normalized action
- interpretation: The global policy remains close to the teacher, but small on-policy pitch-chain deviations coincide with the tracking hold. Constrain those joints on visited states instead of increasing a uniform scalar.

### Largest On-Policy Teacher Deltas

| joint | mean | p95 |
|---|---:|---:|
| `left_knee` | 0.0253 | 0.0632 |
| `right_knee` | 0.0215 | 0.0603 |
| `left_hip_roll` | 0.0267 | 0.0580 |
| `left_ankle` | 0.0281 | 0.0562 |
| `right_ankle` | 0.0231 | 0.0510 |
| `head_yaw` | 0.0213 | 0.0503 |
| `right_hip_roll` | 0.0201 | 0.0452 |
| `left_hip_pitch` | 0.0197 | 0.0443 |

## Mechanism

- `name`: `joint_weighted_onpolicy_teacher_continuity`
- `default_off`: `True`
- `joint_weights_action_order`: `[0.25, 0.5, 1.0, 2.0, 2.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 1.0, 2.0, 2.0]`
- `joint_weight_csv`: `0.25,0.5,1.0,2.0,2.0,0.25,0.25,0.25,0.25,0.25,0.5,1.0,2.0,2.0`
- `teacher_source`: `frozen rate175 command-conditioned MLP queried on PPO-visited observations`
- `scope`: `behavior-prior auxiliary cost only; no runtime or robot change`

## Data Gate Before Training

- Collect full-observation x=0.08 corrected-bridge traces for seeds 0-7 from step 163840.
- Confirm knee/ankle or hip-pitch teacher deltas dominate tracking-damage windows across at least 6/8 seeds.
- Confirm teacher relabel target-rate p95 stays <= 1.75 rad/s and max <= 2.0 rad/s.
- Confirm no required teacher correction exceeds 0.25 normalized action on any pitch-chain joint.
- Run a default-off and uniform-weight CPU wiring parity check before any GPU allocation.

## First Causal Smoke If Data Gate Passes

- `restore`: `Stage A step 163840 checkpoint directory is unavailable; use the original rate175 restore checkpoint and pre-register equivalent initialization evidence before launch.`
- `timesteps`: `40960`
- `restore_policy_kl_scale`: `4.0`
- `behavior_prior_scale`: `-0.6`
- `behavior_prior_huber_delta`: `0.05`
- `behavior_prior_joint_weights`: `[0.25, 0.5, 1.0, 2.0, 2.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 1.0, 2.0, 2.0]`
- `all_other_stage_a_settings`: `frozen`
- `note`: `Only the joint weighting may change in the first causal smoke.`

## Acceptance

- Compact x=0.0 remains PASS_CANDIDATE_SIM_GATE.
- Compact x=0.08 tracking p95 <= 0.20 rad.
- Compact x=0.08 mean vx >= 0.0298 m/s and tracking ratio >= 0.3724.
- Pitch-chain sent-target velocity p95 remains within [2.0, 3.25] rad/s envelope and action saturation remains zero.
- Only after compact acceptance: full 15 s x=0.0 and x=0.08 corrected-bridge seeds 0-7, with no falls and no regression from the teacher full-gate mean vx 0.0339 m/s / ratio 0.4238.

## Falsifier

If the weighted smoke remains above 0.20 rad tracking p95 or loses the Stage A forward-progress floor, stop behavior-prior/KL tuning. The next branch must change the teacher target manifold or actuator objective, not the scalar or joint weights.
