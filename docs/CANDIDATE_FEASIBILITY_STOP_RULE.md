# Candidate Feasibility Stop Rule

This project is no longer searching for any policy that can move in sim. It is
searching for a policy that can move inside the measured actuator envelope.

The current robust fitted pitch-chain envelope is:

```text
effective target velocity: about 2.25-3.75 rad/s
```

`BEST_WALK_ONNX_2` shows the key failure shape:

```text
x <= 0.06: target-rate feasible, but little useful forward progress
x = 0.08: target-rate jumps above the measured actuator envelope
```

## Required Post-Training Check

Every new candidate trained for locomotion must run a command feasibility curve
before any robot validation request:

```bash
python3 tools/analyze_command_feasibility_curve.py \
  --policy <candidate.onnx> \
  --commands 0,0.02,0.04,0.06,0.08,0.10,0.12 \
  --duration 5 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --run \
  --output-dir outputs/analysis/<candidate>_command_feasibility_curve
```

The curve must report:

- command_x
- local forward velocity
- gate status
- pitch-chain p95 target velocity
- action saturation
- body pitch / fall status

## Breakthrough Condition

A candidate has found an in-envelope gait if there is any nonzero command where:

```text
local forward velocity is meaningfully positive
pitch-chain p95 target velocity stays <= 3.75 rad/s
candidate does not fall or terminate early
action saturation remains low
```

This is useful even if the command is only `x=0.04` or `x=0.06`. It proves the
morphology can move forward inside the real actuator budget.

## Hold Condition

A candidate is not a breakthrough if it only moves when:

```text
pitch-chain p95 target velocity exceeds 3.75 rad/s
```

That reproduces the `BEST_WALK_ONNX_2` failure shape: forward motion appears only
when the policy asks for target dynamics the real actuator chain cannot track.

## Stop Rule

Do not run unlimited `v6`, `v7`, `v8` curriculum variants.

After three feasibility-curve-targeted recipes that all show:

```text
no meaningful forward motion below the measured envelope
and
motion onset only above the envelope
```

the project should stop treating this as a reward/curriculum problem and treat
it as an actuator-envelope problem. At that point the next recommendation should
be mechanical/electrical actuator improvement, such as a higher-bandwidth servo
path, before more training.

## Current Count

`movement_bootstrap_v5` is the first recipe explicitly targeted at this
feasibility curve. It starts the count at:

```text
feasibility-targeted recipe attempts: 1 / 3
```

The count increments only after a candidate completes training and its command
feasibility curve is analyzed.
