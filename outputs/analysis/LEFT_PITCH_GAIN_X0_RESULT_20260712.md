# Left pitch-chain gain suspended x=0 result

Date: 2026-07-12

Status: `PASS_X0_GAIN_TRIAL`

Frozen intervention:

```text
left_hip_pitch P: 31
left_knee P:      34
all other body P: 30
head P:           8
all D:            0
```

The first attempt is invalid: an RDK wall-clock step from year 2000 to 2026
tripped a `time.time()` duration guard after 299 samples/5.989 monotonic seconds.
The guard was corrected to `time.monotonic()` without changing the intervention.

Corrected repeat:

```text
samples:                    747 / 747
command:                    x=0.00 only
CRC/read errors:            0
transport resets:           0
write errors:               0
control-budget overruns:    0
dt p95 / max:               0.02009 / 0.02015 s
tracking spikes >0.05 rad:  0
left hip pitch p95:         0.0086 rad
left knee p95:              0.0123 rad
```

Cleanup printed `DEFAULT_RUNTIME_GAINS_RESTORED_AND_TORQUE_DISABLED` and
post-run checks found no runtime or `/dev/ttyACM0` owner. Visual symmetry and
absence of oscillation/buzzing remain required before requesting a separate
x=0.08 stage.

Rob subsequently reported that everything looked normal. This closes the x=0
visual gate; a separately approved x=0.08 trial may be prepared.

The dedicated `scripts/collect_left_pitch_gain_x008.sh` runner is now prepared,
syntax-checked, and refusal-tested. It is fixed to the same P31/34 intervention,
x=0.08, 15 seconds, exact hashes, isolated logs, and normal-gain/torque-off
cleanup. It contains no grounded continuation and has not been run.

Evidence hashes:

```text
JSONL:    177bdeb23ebe0ca6363b69e2df67690511aec07f7b6a23b221c6f5cff078d450
terminal: 94f389f9e9b9a4a60a6f9b28deb18825e27951fc27a82d2c0f2741d8d5597fdd
analysis: dfab9824418a85e9cd2275dfb9be90aff9119c47b30a2745432f38cf8fdf29e7
```
