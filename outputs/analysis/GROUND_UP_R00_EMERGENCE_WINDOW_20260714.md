# Ground-Up R00 Emergence Window

Status: `HOLD_GAIT_NOT_EMERGED_AT_2M`

This is the first behavior-bearing run in the preregistered recipe search. It
does not select a policy or recipe.

## Execution evidence

- Recipe: canonical R00, seed 100, trained from scratch
- Task: nominal `flat_terrain_backlash`
- Requested/completed steps: `2,000,000 / 2,007,040`
- Checkpoints: `0`, `1,003,520`, `2,007,040`
- Colab accelerator: T4
- Training time: `888.8235634069999 s`
- Frozen dependencies: JAX/JAXLIB `0.8.2`, MuJoCo `3.9.0`, Playground `0.0.5`
- Remote archive SHA-256: `15d8483ffd0a2f3e630558b48c4d1ef938d42934805da0c138b99a0a4bd41773`
- VM was stopped after the matching archive was downloaded; no Colab session
  remained active.

The recorded training rewards rose from `14.4077` at step 0 to `85.5578` at
step 2,007,040. They are logged but were not used to grade the recipe.

## Frozen CPU behavior evidence

Both learned checkpoints were evaluated for 1.08 seconds at x=0 and x=0.08
on development seeds 100 and 101 using nominal backlash plus the frozen fitted
actuator bridge.

At step 1,003,520, one seed terminated early. Both x=0.08 runs moved backward
and had negative mean local forward velocity.

At step 2,007,040, all four runs completed and both feet had contact
transitions. The x=0.08 results still failed gait emergence:

| seed | world dx m | mean local vx m/s | result |
|---:|---:|---:|---|
| 100 | -0.0405923 | -0.0463557 | reverse displacement and velocity |
| 101 | 0.0493410 | -0.0419983 | positive world dx but reverse local velocity |

Evidence files:

- `outputs/analysis/ground_up_recipe_search/R00/eval_1003520.json`
- `outputs/analysis/ground_up_recipe_search/R00/eval_2007040.json`

## Decision

R00 has not produced the two consecutive qualifying checkpoints required to
define an equal recipe-comparison window. Therefore no R01-R09 job is ranked,
and R00 is not called the best recipe. The next decision must respect the
preregistered recipe-search cap; the window will not be shortened and training
reward will not substitute for gait evidence.

No robot, RDK, onboard GPU, or local accelerator was accessed.
