# Ground-Up Recipe Search: No Winner at 4M

Status: `NO_RECIPE_WINNER_WITHIN_BUDGET`

The protected canonical R00 control did not reach the preregistered gait
emergence condition at any checkpoint through 4,014,080 steps. Because no
minimum equal comparison window exists inside the recipe-search allocation,
R01-R09 cannot be ranked fairly and no recipe is called best.

## R00W4 evidence

- Fresh seed-100 training run; no warm start
- T4 training time: `1057.4838027350002 s`
- Checkpoints: `0`, `1,003,520`, `2,007,040`, `3,010,560`, `4,014,080`
- Archive SHA-256: `32121ae4a7a44bdfab84d3ad03ff395caeb75f3c6aff80d1847be1df1a5f1318`
- Colab session stopped after verified download

At 3,010,560 steps, all frozen 1.08-second runs completed, but both x=0.08
runs had negative mean local forward velocity. At 4,014,080 steps, both moving
runs still moved backward and one x=0 seed terminated early.

| checkpoint | x=.08 seed | world dx m | mean local vx m/s | finite |
|---:|---:|---:|---:|---|
| 3,010,560 | 100 | -0.042481 | -0.056103 | yes |
| 3,010,560 | 101 | 0.040455 | -0.048054 | yes |
| 4,014,080 | 100 | -0.038768 | -0.054608 | yes |
| 4,014,080 | 101 | -0.128388 | -0.025509 | yes |

R00's training reward rose to `150.33597`; this did not override the failed
behavior gate.

## Root-cause evidence found before family search

The pinned upstream environment randomizes reset yaw across `[-3.14, 3.14]`.
Command tracking evaluates body-local velocity, but the imitation reward
compares the free-base velocity directly with the yaw-zero reference velocity.
Those objectives are not frame invariant.

`outputs/analysis/ground_up_reference_velocity_frame_audit.json` shows that a
robot exactly matching the reference in its body frame can receive an
imitation linear-velocity reward as low as `0.78162654` solely because yaw is
changed. The maximum artificial squared error is `0.03079728`.

The repair patch
`patches/ground_up_reference_velocity_frame_fix.patch` passes body-local linear
velocity and gyro data to the imitation reward. A CPU reset/step contract test
completed with finite reward and unchanged `state[101]` / privileged-state
`[212]` ABI. This is an environment-contract repair, not a recipe winner.

## Decision

Do not spend family-search compute on the known frame-inconsistent learning
signal. First run a bounded corrected-control screen. If it does not improve
the frozen forward-velocity evidence, reject this diagnosis and investigate
the remaining reward/reference contract before architecture search.

No robot, RDK, onboard GPU, or local accelerator was accessed.
