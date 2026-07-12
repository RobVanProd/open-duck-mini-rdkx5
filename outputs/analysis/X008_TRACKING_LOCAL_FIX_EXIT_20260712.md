# x=0.08 tracking local-fix exit

Date: 2026-07-12

Status: `CLOSE_ALIGNMENT_GAIN_AND_TAIL_LIMIT_ROUTES`

## Angular scale

```text
0.0513 rad = 2.939 deg
0.0572 rad = 3.278 deg
0.0500 rad = 2.865 deg
hip threshold miss:  0.075 deg
knee threshold miss: 0.413 deg
```

## Evidence

1. Alignment/offset is rejected. Signed errors are near zero on average and
   reverse with gait phase; large errors correlate with target rate.
2. P31/34 is rejected. Closed-loop p95 was unchanged; fixed-target A/B showed
   only 0.66% hip and 7.06% knee improvement, while several max errors worsened
   more than the frozen 10% limit. Rob saw no difference.
3. Hardware-fit tail limiting is insufficient. The previously fitted limits
   (hip 2.5, knee 3.25 rad/s) affect only 0.134% of targets. Predicted hip p95
   is unchanged; knee improves just 0.00043 rad. Maximum target changes are
   1.00 and 2.03 degrees respectively.
4. A rate cap strong enough merely to approach the knee gate is about 1.2 rad/s,
   changing the knee target by up to roughly 4.4 degrees and affecting about
   14% of samples. That is a material gait intervention, not a small correction.

## Decision

There is no evidence-supported small mechanical, offset, gain, or tail-clipping
fix for this policy. Do not weaken the 0.05 rad gate or tune these parameters
post hoc. The remaining honest route is a separately preregistered policy/target
trajectory objective that preserves motion while reducing the broad high-rate
portion of the knee trajectory. Until such a policy passes offline and suspended
gates, grounded replay remains blocked.

Normal runtime gains are restored, the ID-13-last bus fix remains staged, and
no runtime or serial-port owner remained after testing.
