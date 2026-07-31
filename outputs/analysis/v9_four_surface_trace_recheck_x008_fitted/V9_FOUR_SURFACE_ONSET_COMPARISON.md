# V9 Four-Surface Onset Comparison

Offline trace comparison for representative V9 `x=0.08` fitted-bridge outcomes. No robot action was performed.

## Onset Table

| surface | samples | done_tick | init_contacts | first_asym | first_both | first_none | vx>0.08 | vx<-0.08 | pitch>0.25 | pitch>0.5 | h<0.12 | h<0.10 |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed0_lunge` | 73 | 72 | `01` | 0 | 2 | 65 | 3 | NA | 15 | 51 | 66 | 68 |
| `seed1_collapse` | 32 | 31 | `11` | 2 | 0 | 3 | 27 | NA | NA | NA | 29 | 30 |
| `seed2_standstill` | 750 | NA | `01` | 0 | 2 | NA | 1 | NA | 24 | NA | NA | NA |
| `seed5_reverse` | 56 | 55 | `00` | 5 | 2 | 0 | 2 | 25 | 34 | 43 | 51 | 52 |
| `seed6_lunge` | 58 | 57 | `10` | 0 | 17 | 3 | 13 | 0 | 22 | 38 | 51 | 53 |
| `seed7_collapse` | 27 | 26 | `11` | 3 | 0 | 25 | 13 | 3 | NA | NA | 25 | 26 |

## First 0.22s Snapshots

### seed0_lunge

```text
t0:01,h0.154,p0.00,vx-0.03; t2:11,h0.158,p0.00,vx0.08; t4:11,h0.163,p0.01,vx0.08; t6:01,h0.166,p0.04,vx0.08; t8:01,h0.163,p0.08,vx0.11; t10:01,h0.158,p0.13,vx0.11
```

### seed1_collapse

```text
t0:11,h0.159,p0.00,vx-0.01; t2:10,h0.175,p-0.00,vx0.01; t4:10,h0.180,p-0.03,vx-0.02; t6:10,h0.182,p-0.04,vx-0.06; t8:10,h0.183,p-0.05,vx-0.07; t10:10,h0.183,p-0.04,vx-0.05
```

### seed2_standstill

```text
t0:01,h0.153,p-0.01,vx0.06; t2:11,h0.157,p-0.02,vx0.12; t4:10,h0.164,p-0.01,vx0.01; t6:11,h0.164,p0.03,vx-0.07; t8:11,h0.162,p0.07,vx-0.03; t10:11,h0.161,p0.09,vx0.03
```

### seed5_reverse

```text
t0:00,h0.150,p-0.01,vx0.02; t2:11,h0.149,p-0.06,vx0.12; t4:11,h0.164,p-0.13,vx0.14; t6:01,h0.169,p-0.15,vx0.03; t8:11,h0.168,p-0.12,vx-0.03; t10:11,h0.166,p-0.09,vx-0.03
```

### seed6_lunge

```text
t0:10,h0.159,p0.01,vx-0.15; t2:10,h0.172,p0.01,vx-0.14; t4:01,h0.172,p0.01,vx-0.09; t6:01,h0.175,p0.01,vx-0.04; t8:01,h0.175,p0.02,vx0.01; t10:01,h0.172,p0.04,vx0.04
```

### seed7_collapse

```text
t0:11,h0.157,p-0.00,vx-0.06; t2:11,h0.173,p-0.02,vx-0.07; t4:01,h0.177,p-0.02,vx-0.12; t6:01,h0.179,p0.00,vx-0.08; t8:01,h0.179,p0.02,vx-0.04; t10:01,h0.178,p0.02,vx0.02
```


## Interpretation

- The failures branch almost immediately by contact/support state and velocity sign; they do not look like one common lunge mechanism with different endings.
- The lunge seeds develop forward velocity and large pitch before termination.
- The collapse seeds start or become contact-asymmetric early, lose height before meaningful pitch growth, and terminate with low body pitch.
- The reverse seed develops negative local velocity and then also reaches a large pitch/base-height failure.
- The standstill seed keeps both feet in contact, maintains height, and never develops useful local forward velocity.
- V10 should therefore optimize behavioral consistency across seeds before pure stability margin: it must prevent lunge, reverse, collapse, and freeze regimes, not only reduce forward-speed overshoot.
