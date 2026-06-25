# Contact Weight-Transfer Discriminator

status: `HOLD_CONTACT_NOT_BINARY_MISMATCH_ONLY`

This is an offline decision note over existing artifacts. It does not run
training, simulation, robot SSH, deployment, or hardware tests.

## Question

Does the current low-command failure come from the policy being unable to enter
the requested contact state, or from the target fragments themselves not asking
for useful single-support/weight-transfer behavior?

The pre-registered branch was:

```text
clean-fragment contact + closed-loop double-support mismatch:
  add an explicit foot/contact objective

double-support in the fragment itself:
  rebuild the generator with a single-support objective
```

Existing evidence produces a third, sharper branch:

```text
clean-fragment contact + low closed-loop contact mismatch + low forward motion:
  binary contact matching is not sufficient; optimize sustained weight transfer
  and forward progress, not just contact labels or stronger joint priors.
```

## Evidence

### Raw Polynomial Reference Path

The polynomial reference path has a real contact incompatibility:

| artifact | contact mismatch | actual double support | reference double support | result |
|---|---:|---:|---:|---|
| `REFERENCE_CONTACT_COMPATIBILITY_V20.md` raw reference | 68.03% | 73.86% | 35.43% | hold |
| `REFERENCE_CONTACT_COMPATIBILITY_V20.md` projected phase 1 | 67.77% | 75.90% | 35.54% | hold |
| `REFERENCE_CONTACT_COMPATIBILITY_V20.md` projected phase 5 | 67.23% | 74.89% | 37.52% | hold |
| `REFERENCE_CONTACT_COMPATIBILITY_V20.md` projected phase 19 | 67.57% | 74.41% | 38.38% | hold |

Interpretation: the raw/projected reference expects alternating single support
much more often than the simulated body realizes. That reference path should not
be treated as a direct controller or BC label source.

Contact-synchronized projection reduces the mismatch but does not recover the
gait:

| artifact | aggregate contact mismatch | falls | duration complete | mean vx |
|---|---:|---:|---:|---:|
| `REFERENCE_MOTION_ROLLOUT_V20_CONTACT_SYNCHRONIZED_PROJECTED.md` | 4.36% | 7/8 | 1/8 | -0.0152 m/s |

Interpretation: fixing the contact labels alone did not produce usable forward
locomotion from the polynomial reference path.

### Dynamic-Roll Lateral-Fix Fragment Path

The dynamic-roll lateral-fix source is the best short target source found so
far:

| artifact | status | seed0 vx | seed2 vx | seed2 contact dominance | seed2 transitions |
|---|---|---:|---:|---:|---:|
| `TARGET_SOURCE_AUDIT.md` dynamic_roll_lateral_fix | `PASS_SEED_ROBUST_TARGETS` | 0.0416 | 0.0437 | 94.00% | 4 |

The compact prior from those fragments is in-envelope:

| artifact | mean vx | contact dominance mean | contact dominance p95 | max target velocity p95 |
|---|---:|---:|---:|---:|
| `SOFT_PRIOR_FRAGMENT_CONFIG.md` | 0.0417 m/s | 92.67% | 94.00% | 2.4428 rad/s |

Closed-loop sequence replay of the aggregate fragment table does not fail from
large binary contact mismatch:

| adapter | seed | vx | track ratio | pitch p95 | contact mismatch |
|---|---|---:|---:|---:|---:|
| contact_hold | seed_000 | 0.0119 | about 0.30 | near/over gate | 2.76% |
| contact_hold | seed_002 | 0.0138 | about 0.34 | near/over gate | 0.00% |
| contact_match | seed_000 | 0.0117 | 0.2930 | 0.2935 | 2.76% |
| contact_match | seed_002 | 0.0138 | 0.3443 | 0.2536 | 0.00% |
| state_match | seed_000 | 0.0117 | about 0.29 | near/over gate | 2.76% |
| state_match | seed_002 | 0.0138 | about 0.34 | near/over gate | 0.00% |

Interpretation: the dynamic-roll fragment replay can match the binary contact
schedule, but matching that schedule does not produce enough forward progress.
The current short fragment table remains evidence, not a sufficient gait
controller or training label source.

### Soft-Prior PPO Path

The weak V21 soft-prior learner did not stay close to the fragment prior:

```text
V21 soft_prior_abs_error_mean: 0.2609
```

The partial V22 checkpoint used a much stronger step-phased prior, but was still
far from the prior by the recovered checkpoint:

```text
V22 partial soft_prior_abs_error_mean: 0.2711
```

Interpretation: simply making the pitch-chain prior stronger did not lock the
policy into the low-command fragment basin by the recovered V22 checkpoint. This
does not justify another prior-scale-only run.

## Decision

The 68% contact mismatch remains a valid diagnosis for the raw polynomial
reference path. It is not the full diagnosis for the later dynamic-roll fragment
path.

For the current best fragments, the blocker is not simply:

```text
the phase selector cannot find the requested binary foot-contact state
```

The better current statement is:

```text
Short fragments contain useful in-envelope low-command motion, and their binary
contact sequence can be replayed with low mismatch, but the closed-loop system
does not convert that sequence into sustained forward weight transfer.
```

That points away from:

```text
- stronger pitch-chain priors alone
- another raw polynomial-reference BC run
- another contact-bit adapter around the same short table
```

and toward:

```text
- a sustained target generator with explicit weight-transfer/contact-transition
  objectives over 100-150 ticks,
- or a closed-loop learner objective that directly rewards forward weight
  transfer, penalizes unproductive double-support dwell during commanded motion,
  and preserves base height/pitch stability.
```

## Next Gate

Before another CUDA training run, add or run one bounded offline gate:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  100-150 tick target or rollout has nonzero forward progress, low lateral
  drift, stable pitch/height, in-envelope target velocities, and multiple
  useful left/right support transitions.
```

If that gate cannot be met by the generator, do not launch PPO from the short
fragment table. If it can be met, then PPO/BC can be evaluated against a target
that actually asks for sustained weight transfer rather than only short contact
labels.

