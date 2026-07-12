# Grounded Rate165 Gate-3 Suspended x=0 Result

Date: 2026-07-12

Status: `PASS_GATE3_WITH_RECOVERED_READ_WARNING`

Scope executed: staged rate165 candidate, suspended, exactly `x=0`, 15 seconds.
No nonzero command or grounded replay occurred.

## Identity And Command

```text
policy SHA256: e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
command first/last: [0, 0, 0, 0, 0, 0, 0]
command unique count: 1
duration samples: 747
```

## Numeric Gate

```text
gate: WARN_PROCEED_WITH_CAUTION
holds: none
read retries: 7 / 747 = 0.94% (yellow warning)
write errors: 0
read/write bursts: 0 / 0
dt p95/max: 0.02009 / 0.02263 s
dt >0.03 s: 0
control-budget warnings: 0
action saturation: 0% on every joint
tracking spikes >0.05 rad: 0
```

Pitch-chain tracking p95:

| joint | p95 abs rad | max abs rad |
|---|---:|---:|
| left hip pitch | 0.0072 | 0.0103 |
| left knee | 0.0130 | 0.0160 |
| left ankle | 0.0106 | 0.0130 |
| right hip pitch | 0.0082 | 0.0170 |
| right knee | 0.0053 | 0.0090 |
| right ankle | 0.0104 | 0.0162 |

All are below the preferred `<0.05 rad` threshold, with no post-startup spike
above `0.05 rad` and no sustained error above `0.10 rad`.

## Cleanup

The diagnostic printed `TURNING OFF`; terminal parsing detected one motor-off
cleanup. The runner then invoked the independent `turn_off.py` fallback. A
post-run process audit returned `NO_RUNTIME_PROCESS`.

## Runner Corrections Before Motion

Two attempts stopped before motor initialization:

1. process detection matched the preflight shell's own command text;
2. read-only SSH consumed the local confirmation line.

The process check now considers only Python processes and all SSH calls use
`-n`, reserving stdin for the local exact-confirmation prompt. The third attempt
passed preflight and is the only attempt that ran the policy.

## Artifact Hashes

```text
raw JSONL (kept outside Git by default):
  abe3b972f5eb94ccee023b62bbee7fcf4e5c2aa4ab6b7319d66be934b540ab93
terminal log (kept outside Git by default):
  445335c92bdb4c8b9cce87e3e4c4389f61fc4b9d14897ae55e01989f7a64befc
analysis Markdown:
  f943cf4357c9d292bfb86499dd350694d7d37f7ba0a4cd600bfc40a36a799bc4
```

## Decision Boundary

Rob reported:

```text
it looked okay. little movements in both legs they looked opposite of each
other and equal
```

This is a visual pass: small equal-amplitude, opposite-phase bilateral motion
is coherent and symmetric, with no reported twitch or unexpected excursion.
Gate 3 therefore passes with the retained CRC/read warning. Stop here;
`x=0.08` still requires a separate explicit approval.
