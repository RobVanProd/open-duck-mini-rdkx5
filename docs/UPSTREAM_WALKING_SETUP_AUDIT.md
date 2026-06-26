# Upstream Walking Setup Audit

This is an offline provenance audit. It does not train, deploy, SSH, or run
robot tests.

## Executive Summary

The upstream walking story is split across two repositories:

- `apirrone/Open_Duck_Playground` contains the training/eval environment,
  polynomial reference motion, and export scripts.
- `apirrone/Open_Duck_Mini` branch `v2` publishes the deployed
  `BEST_WALK_ONNX_2.onnx` policy used by the runtime.

The local `policy/BEST_WALK_ONNX_2.onnx` matches the local
`Open_Duck_Mini/BEST_WALK_ONNX_2.onnx` byte-for-byte by SHA256:

```text
3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

GitHub reports the upstream `apirrone/Open_Duck_Mini:v2` file as:

```text
path: BEST_WALK_ONNX_2.onnx
size: 884177 bytes
git blob sha: 7e4536d90e35f9a3a886fb7584d489ad4894dfe0
download: https://raw.githubusercontent.com/apirrone/Open_Duck_Mini/v2/BEST_WALK_ONNX_2.onnx
```

The training checkpoint that produced that ONNX is not published in the
Playground repository, and the Playground repository has no GitHub releases.
The README's documented "Current win" command is:

```bash
uv run playground/open_duck_mini_v2/runner.py \
  --task flat_terrain_backlash \
  --num_timesteps 300000000
```

That means the next useful question is not another nearby teacher variant. It
is whether the published ONNX/reference/setup actually produces forward
propulsion in the expected upstream sim contract, especially the
`flat_terrain_backlash` task.

## Sources Checked

| Source | Finding |
|---|---|
| `/tmp/open_duck_playground_origin_main` | detached `origin/main` at `b9be205ac64488c23504ca42e5ec790337adeec3` |
| `Open_Duck_Playground/README.md` | documents imitation reference generation and `flat_terrain_backlash` 300M current-win command |
| `playground/open_duck_mini_v2/runner.py` | default task is `flat_terrain`; default timesteps are `150000000` |
| `playground/common/runner.py` | saves checkpoints and exports ONNX during PPO training |
| GitHub issue `apirrone/Open_Duck_Playground#8` | confirms 101 observation / 14 action training context and example checkpoint step `10813440` |
| GitHub PR `apirrone/Open_Duck_Playground#10` | merged export fix; body says a model was trained and checkpoint tested after the change |
| `Open_Duck_Mini_Runtime/README.md` | points deployment users to `Open_Duck_Mini:v2/BEST_WALK_ONNX_2.onnx` |
| `apirrone/Open_Duck_Mini:v2` | publishes `BEST_WALK_ONNX_2.onnx` but not its training checkpoint lineage |

## Upstream Reference Push-Effectiveness

The upstream polynomial reference key used for the nearest command is:

```text
x = 0.074
y = -0.037
yaw = -0.074
```

This was tested against the detached upstream-main Playground worktree using
the README's `flat_terrain_backlash` task:

```text
playground_path: /tmp/open_duck_playground_origin_main
task: flat_terrain_backlash
```

Artifact:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_BACKLASH_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0051 m/s
```

Summary:

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | -0.0500 | 66.9833% | -0.0390 | 0.1859 | 5.2400 |
| cycle projected | 0/8 | -0.0114 | 72.9500% | -0.0356 | 0.1713 | 5.2400 |
| contact synchronized projected | 1/8 | 0.0301 | 20.1366% | -0.0051 | 0.1696 | 5.2400 |

Interpretation:

```text
The README's backlash task improves some duration/stability metrics, but it
does not make the upstream reference's single-support windows create net
forward acceleration. The best 0.1s future-vx delta during reference single
support remains negative.
```

## Morphology / Reference File Audit

Artifact:

```text
outputs/analysis/UPSTREAM_SIM_MORPHOLOGY_AUDIT.md
```

Result:

```text
PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY
```

Meaning:

```text
The local XML and polynomial reference file match upstream byte-for-byte.
The known drift is in code paths such as joystick.py and runner.py, not in the
MJCF/reference assets.
```

## Decision

Do not continue local teacher variants as the default next move. The current
evidence says:

```text
local teacher push primitives:
  do not produce robust positive forward impulse

matched x=0.04 reference:
  positive impulse only while violating lateral stability / target-rate limits

upstream nearest reference on flat_terrain:
  no positive reference-single future-vx delta

upstream nearest reference on flat_terrain_backlash:
  no positive reference-single future-vx delta
```

The first contact-physics substitution did not rescue this:

```text
outputs/analysis/CONTACT_PHYSICS_AUDIT.md
status: HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT
floor friction: 0.6 -> 1.5 0.01 0.0006
solver iterations: 1/5 -> 100/50
best reference-single future-vx delta: -0.0051 -> -0.0182 m/s
```

This does not prove stable forward walking is impossible. It does prove that
the currently tested reference/teacher action-target paths are not an
existence proof for stable, in-envelope, low-command walking.

## Published-Policy Sim Audit

The published-policy discriminator has now been run:

```text
outputs/analysis/PUBLISHED_POLICY_PROPULSION_AUDIT.md
status: PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION
task: upstream-main flat_terrain_backlash
seeds: 8
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
mean local vx: 0.0540 m/s
mean single-support 0.1s future vx delta: +0.0042 m/s
```

This answers a different question than the reference rollouts:

```text
Does the published policy use closed-loop feedback to produce forward
propulsion that the open-loop/reference-target path does not?
```

Answer: yes. The upstream-main sim/morphology is not generally unable to walk.
The failed path is the open-loop/reference-target controller path. The next
offline branch should mine the published policy's closed-loop contact and
propulsion mechanism before returning to teacher generation.

The command-specific follow-up shows that this result is not uniform across
low-speed commands:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_PROPULSION_COMPARISON.md
status: PASS_POLICY_COMMAND_PROPULSION_COMPARISON
```

Summary:

| command | moving seeds | envelope-safe seeds | mean local vx | single support | max pitch sent-target p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0 / 8 | 8 / 8 | 0.0019 m/s | 3.65% | 2.9633 rad/s |
| upstream nearest `x=0.074, y=-0.037, yaw=-0.074` | 7 / 8 | 1 / 8 | 0.0540 m/s | 44.80% | 5.2400 rad/s |
| straight `x=0.08` | 7 / 8 | 0 / 8 | 0.0640 m/s | 49.40% | 5.2400 rad/s |

This tightens the conclusion:

```text
BEST_WALK proves closed-loop walking exists in this sim contract.
It does not prove stable in-envelope walking at the moving command cells tested.
At straight x=0.04, BEST_WALK stays inside the envelope but mostly stands.
At x=0.08 and the upstream nearest turning key, BEST_WALK walks but uses
right-knee target rates near the 5.24 rad/s slew ceiling.
```

So straight `x=0.04` should not be treated as the first proof-of-walking gate.
It is better interpreted as a no/low-motion posture cell unless a policy has
independently demonstrated walking there. Future training/eval work should
start mechanism extraction from command cells where BEST_WALK actually enters
single support, while explicitly reducing the right-knee rate mechanism that
keeps those cells outside the measured actuator envelope.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- training or retraining
- changing runtime behavior
- changing gains, offsets, remaps, phase timing, action scale, or policy files
