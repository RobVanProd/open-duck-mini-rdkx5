# Phase 2 Stage A Bounded-Continuity Causal Diagnosis

Date: 2026-07-11

Status: **HOLD — intervention was too weak and did not repair the measured
closed-loop failure**

This is offline, read-only analysis of saved CPU/Colab artifacts. No training,
robot access, deployment, Colab allocation, local iGPU, or onboard GPU was used.

## 1. Actual training exposure

The nominal 40,960-step request executed 122,880 steps because of Brax rollout
granularity and evaluation scheduling:

```text
env_step_per_training_step = 512 batch * 20 unroll * 4 minibatches = 40,960
num_evals_after_init = 4 - 1 = 3
ceil(40,960 / (3 * 40,960)) is forced to one training step per epoch
three epochs * 40,960 = 122,880 actual environment steps
```

This comes directly from the installed
`brax/training/agents/ppo/train.py` calculation and matches the three exported
checkpoint steps. Runtime duration was therefore not the intended single-update
causal exposure.

## 2. Matched checkpoint comparison

The original and bounded branches both emitted an 81,920 checkpoint, permitting
a matched-step comparison under the same x=0.08 compact evaluator.

| metric | original 81,920 | bounded 81,920 | bounded minus original |
|---|---:|---:|---:|
| mean local vx (m/s) | 0.013599 | 0.012799 | -0.000800 |
| command tracking ratio | 0.169992 | 0.159991 | -0.010000 |
| worst pitch tracking p95 (rad) | 0.214272 | 0.212255 | -0.002017 |
| double support | 92% | 90% | -2 pp |
| single support | 8% | 10% | +2 pp |
| support transitions | 5 | 7 | +2 |

The bounded teacher produced a tiny tracking improvement but slightly worse
forward progress. No pitch-chain joint changed its tracking p95 by more than
0.0051 rad at the matched checkpoint, and the same left-knee/right-ankle
bottleneck remained.

## 3. Same-observation policy effect size

All policies were evaluated on the same 400 observations from the original
rate175 step-163,840 eight-seed x=0.08 traces. This removes trajectory variation
from the policy-output comparison.

| comparison | mean abs action delta | p95 | max |
|---|---:|---:|---:|
| original 81,920 vs bounded 81,920 | 0.00278 | 0.00787 | 0.02225 |
| original 163,840 vs bounded 122,880 | 0.00514 | 0.01253 | 0.02085 |

The policies are nearly identical on the observed failure-state manifold. This
agrees with the earlier temporal projection audit: only 33 of 2,400 pitch-chain
teacher values changed, with 0.0002 mean normalized-action distortion. The
bounded teacher was therefore safe but did not provide a material causal push.

Artifact:

`outputs/analysis/PHASE2_STAGE_A_BOUNDED_POLICY_FIXED_OBS_COMPARISON.md`

## 4. Closed-loop symptom

Across the bounded checkpoints, compact x=0.08 behavior remained dominated by
double support and minimal swing:

| checkpoint | double support | single support | left swing samples | right swing samples | ratio |
|---:|---:|---:|---:|---:|---:|
| 40,960 | 92% | 8% | 3 | 1 | 0.0944 |
| 81,920 | 90% | 10% | 4 | 1 | 0.1600 |
| 122,880 | 92% | 8% | 4 | 0 | 0.2648 |

This symptom is not by itself the full cause. In the original eight-seed data,
some high-progress seeds also spent 90% in double support, while some seeds with
more single support were weak. The evidence does not justify treating a single
support-reward scalar as the solution.

Exploratory eight-seed correlations (n=8) associate progress with coordinated
roll/sagittal action details, including left-hip-roll action rate and lower
left-ankle action variability. These are hypothesis-generating only; the sample
is too small and correlated metrics are not interventions.

## 5. Decision and next evidence requirement

The temporal rate bound solved the teacher-envelope violation but was too sparse
to alter the learned policy materially. The evidence rejects:

1. continuing this bounded-teacher branch;
2. interpreting more PPO steps as proof the intervention would eventually pass;
3. another unregistered behavior-prior scalar adjustment;
4. assuming double-support punishment alone will preserve useful forward motion
   (prior matched support-transition evidence showed regression).

Before another training run, an offline teacher/objective candidate must be
screened on the saved x=0.08 failure observations and demonstrate all of the
following from measured outputs:

- a material, directionally coherent correction rather than the observed
  near-zero policy perturbation;
- preservation of the x=0 action manifold;
- both-leg swing/support intent rather than a one-sided contact pattern;
- compliance with the fitted target-rate and saturation envelope;
- an exact rollout/update budget derived from Brax granularity.

No new training is authorized by this diagnosis. A concrete candidate and its
offline effect-size/support/rate evidence must come first.
