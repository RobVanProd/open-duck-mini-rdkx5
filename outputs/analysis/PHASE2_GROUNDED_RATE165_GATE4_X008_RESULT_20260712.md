# Grounded Rate165 Gate-4 Suspended x=0.08 Result

Date: 2026-07-12

Status: `HOLD_GATE4_BUS_CONTROL_IMPACT; GROUNDED_BLOCKED`

Scope executed: staged rate165 candidate, suspended, exactly `x=0.08`, 15
seconds. No grounded replay occurred.

## Identity And Command

```text
policy SHA256: e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
command first/last: [0.08, 0, 0, 0, 0, 0, 0]
command unique count: 1
samples: 747
```

## Operator Observation

Rob reported:

```text
looked about the same but more aggressive
```

This supports a coherent continuation of the `x=0` bilateral pattern, with
greater motion amplitude/aggressiveness at nonzero command. It does not override
the numeric bus/control hold.

## Hard Hold

```text
read retries: 25 / 747 = 3.35%
red threshold: >2.00%
write errors: 0
read/write bursts: 0 / 0
post-startup tracking spikes >0.05 rad: 224
bus event correlated with post-startup tracking spike: yes
```

The result independently fails the read-retry red threshold and the correlated
control-impact rule. Grounded replay is blocked even though there were no write
errors, timing overruns, or action saturation.

Temporal audit (within ±2 ticks):

```text
x=0:    7 event ticks, 0 post-startup tracking-spike ticks, 0 correlated events
x=0.08: 23 event ticks, 172 post-startup tracking-spike ticks,
        18 event ticks near a tracking spike, 40 spike ticks near a bus event
```

This is correlation evidence, not proof that CRC failures cause the tracking
spikes or vice versa. It is strong enough to prohibit grounded escalation.

## Tracking

Pitch-chain tracking p95:

| joint | p95 abs rad | max abs rad |
|---|---:|---:|
| left hip pitch | 0.0515 | 0.1393 |
| left knee | 0.0580 | 0.1070 |
| left ankle | 0.0459 | 0.1199 |
| right hip pitch | 0.0430 | 0.1068 |
| right knee | 0.0341 | 0.0751 |
| right ankle | 0.0431 | 0.1197 |

The maximum pitch p95 (`0.0580 rad`) misses the preferred `<0.05 rad` target
but remains inside the packet's acceptable `<0.08 rad` band. The generic
analyzer labels p95 above `0.05 rad` as a hold; under the preregistered operator
packet this is a tracking warning/acceptable-margin result. This distinction
does not change the overall hard hold from bus errors and their correlation.

## Target Velocity And Lag

Pitch-chain sent-target velocity p95 ranged from `0.9343` to `1.6888 rad/s`;
the maximum observed target velocity was `3.0123 rad/s`. Rate limiting was not
active. Every pitch joint's best measured lag was 3 ticks (`60.3 ms`). Action
saturation was `0%` on every joint.

These velocities are substantially lower than the old corrected dynamic replay
range (`3.14-5.22 rad/s` p95), so the rate165 candidate achieved its intended
velocity reduction. The evidence does not support attributing the remaining
hold solely to policy aggressiveness because CRC failures are also elevated and
correlated with tracking spikes.

## Timing And Cleanup

```text
dt p95/max: 0.02009 / 0.02040 s
dt >0.03 s: 0
control-budget warnings: 0
exceptions: 0
diagnostic motor-off cleanup: present
independent turn_off.py cleanup: completed
post-run runtime process: absent
```

## Artifact Hashes

```text
raw JSONL (kept outside Git by default):
  f19b14662e3803015792cb9589b784da47174f72cb0e27d1f5dfd2971668f8f2
terminal log (kept outside Git by default):
  647a2cb192a695253d4ec8d4e23f47cd5f501114a1cc5650f89627d834ae9c9a
gate analysis Markdown:
  f18d0e3fe8e23a4354a830f82aae44c4f1e6087afdb554083846e85ae84dc590
target-velocity Markdown:
  f05f5d057025107f9b56d0c7b0a53aeb6c0f3565f453eadcbab96dbc25120f14
```

## Decision

Gate 4 holds. Do not run grounded replay. The next evidence-backed branch is to
diagnose why read CRC failures rise from `0.94%` at suspended `x=0` to `3.35%`
at `x=0.08`, including power/bus integrity and temporal correlation, before
deciding whether a controlled repeat is justified. No additional motor test is
authorized by this result.
