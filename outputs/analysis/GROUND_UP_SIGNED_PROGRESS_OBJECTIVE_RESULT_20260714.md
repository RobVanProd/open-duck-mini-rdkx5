# Ground-Up Signed Progress Objective Result

status: `NO_SIGNED_PROGRESS_OBJECTIVE_WINNER`

## Decision

`O1_SIGNED_PROGRESS` does not advance. It improved one measured behavior over
the protected `B0_NOMINAL_PHASE0` control, but it did not satisfy the frozen
all-run gate and retained the same total hard-failure count.

| candidate | moving passes | persistent moving seeds | hard failures | full checkpoint passes | decision |
|---|---:|---:|---:|---:|---|
| `B0_NOMINAL_PHASE0` | 1/8 | 0 | 6 | 0/2 | control; no advance |
| `O1_SIGNED_PROGRESS` | 2/8 | 1 | 6 | 0/2 | eliminate |

O1 passed x=`0.074`, seed `100` at both 3,010,560 and 4,014,080. This is a
measured persistence improvement over B0, which passed that run only at 3M.
It is not a policy winner: seed `101` fell at x=`0.074` and x=`0.08` at both
checkpoints, while both x=`0.08`, seed `100` runs produced a constant
saturated action vector. Neither checkpoint passed all four runs.

## Frozen causal comparison

O1 differed from B0 only in positive-command linear tracking:

- B0: `exp(-(command_x - body_local_vx)^2 / 0.01)`;
- O1: `clip(body_local_vx / abs(command_x), -1, 1)`.

The scale remained `2.5`; phase, command, architecture, horizon, reset,
randomization, PPO scalars, other reward terms, and total reward clipping were
unchanged. Evaluation used the preregistered x=`0.074/0.08`, seeds `100/101`,
3M/4M checkpoints, and `1.08 s` duration.

## Artifact record

- archive SHA-256:
  `55ee6f33fc2a396c61a2ad19b37dea9fd9cd9bb7c2a4d58ca815f5ad1f1ef11b`;
- 3M policy SHA-256:
  `b477e8e47f71867ea7c08fde2f6ba3ced992a00609156e59ac0ef6933fdcdeb9`;
- 4M policy SHA-256:
  `cc47011bfac200490b9951d54f866ffe0df534c9887c61bcca2631abb8261351`;
- training seconds: `1001.218938228`;
- hosted-job seconds: `1052.113361508`;
- signed-progress patch SHA-256:
  `13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b`.

The archive was downloaded and hash-verified. Colab was stopped before local
behavior evaluation and no Colab session remained.

## Interpretation and next boundary

Signed forward progress is directionally useful but insufficient by itself.
Per preregistration, do not tune its scale, clip, denominator, command, phase,
or horizon post hoc. The next work is a read-only reward-accounting audit of
the two remaining structural objective mechanisms: command-invariant survival
terms and per-step clipping of negative total reward. No new accelerator run
is authorized until that audit selects one causal factor and a new experiment
is preregistered.

No policy, Stage-2 continuation, baseline comparison, offline clearance, RDK
runtime work, deployment, or robot validation is authorized. Training reward
was excluded from selection. Evaluation used local CPU only; no local GPU,
iGPU, onboard GPU, RDK-X5, robot, motor, or torque access occurred.
