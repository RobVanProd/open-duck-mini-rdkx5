# Ground-Up Applied-Target-State Continuation Preregistration

status: `PREREGISTERED_BEFORE_IMPLEMENTATION_OR_UPDATE`

## Evidence selection

The bridge-only feedforward arm preserved gait, eliminated target-rate excess
and saturation, and produced one full x=.08 fitted-tracking pass, but failed the
two-checkpoint persistence rule. The exact 115-D observability audit proves a
specific remaining causal defect: the first-order bridge's previous applied
target affects the next transition but is absent from the actor observation.

The actor already has all discrete delay information in its three sent-action
history fields. Its absolute sent motor-target field is an affine duplicate of
`home + action_scale * last_act` within `5.14984e-8 rad`. A controlled fork with
identical 115-D observation and action but a `.04 rad` hidden applied-target
difference changes next physics control by `.0299975 rad`. This selects one
same-size state repair, not recurrence or reward tuning: replace the redundant
absolute sent-target slot with bridge-applied target.

## Protected source

Use the bridge-only 1,003,520-step checkpoint. It is selected over 2,007,040
because it has lower mean tracking error across the three commands (`.20031`
versus `.20550 rad`), is better at two of three commands, and already passes
x=.08 at `.18858 rad` while retaining zero saturation/rate excess.

- archive: `outputs/analysis/A1_MEASURED_BRIDGE_ONLY_artifacts.tar.gz`;
- archive SHA-256:
  `bf9116063bbd42212c7a14f0c4fb052a8f5b72dc381a35ad833f998debbcc2e8`;
- restore checkpoint:
  `A1_MEASURED_BRIDGE_ONLY/2026_07_14_164618_1003520`;
- checkpoint directory SHA-256:
  `4ad36da228a97c3f1cd7d19535896b7f256d519bbc9bd7d584b4c15d6dca8eb8`;
- source ONNX SHA-256:
  `4350900f959a25da6b3e05a942b456124db67ca3a1458c499d540551bbd593d0`;
- observability audit SHA-256:
  `c843a93171c1fef1fae0c5adc34fa2ceb52a7c93bc54f4d99f481a8588606339`;
- Playground base commit:
  `b9be205ac64488c23504ca42e5ec790337adeec3`.

`BEST_WALK_ONNX_2` remains a comparator only and is not a source, teacher,
behavior prior, or reward target.

## Frozen causal change

Keep the complete protected bridge-only recipe unchanged. Add one default-off
configuration flag. When both measured bridge and applied-target observation
are enabled:

- actor/critic state indices `83:97` contain
  `ground_up_actuator_bridge_applied_targets`;
- indices `41:55`, `55:69`, and `69:83` continue to contain current and prior
  sent actions;
- `motor_targets` remains the sent target in environment info;
- physics continues to receive the bridged applied target;
- state size remains exactly 115 with the projected reference table;
- no reward, cost, optimizer, architecture, ONNX interface, bridge vector, or
  hard target-limit change is allowed;
- when the flag is off, the old observation is bit-for-bit unchanged.

## Frozen CPU contract

Before any hosted compute, the composed patch must apply cleanly and prove on
CPU:

1. Default-off reset/step observations match the bridge-only source exactly.
2. With the flag on, the 115-D slot `83:97` equals the bridge-applied target,
   while sent target reconstructs from `home + scale * obs[41:55]` within
   `1e-6 rad`.
3. The three action histories still reconstruct the delayed-target history;
   physics control still equals bridge-applied target; no bridge-derived reward
   or cost exists.
4. The prior identical-observation hidden-state fork is resolved: after
   observation refresh, its applied-target difference is visible in `83:97`
   without changing any other intended slot.
5. A 1,024-requested-step smoke restores the protected parameter tree exactly,
   changes at least one policy leaf, and keeps every parameter/metric finite.
6. Step-zero and final ONNX retain exactly `obs, previous_action` inputs and
   `continuous_actions, previous_action_out` outputs; chained hard-bound excess
   remains `<=1e-6`.

Freeze the smoke at CPU only, seed 100, 32 environments, two exports, episode
length 100, unroll 8, batch 32, four minibatches, one update, LR `3e-4`,
discount `.97`, entropy `.005`, and imitation `1.0`. Its reward cannot select a
policy.

## Conditionally authorized hosted continuation

Only a fully passing CPU contract authorizes one T4 job from the protected 1M
checkpoint: 2,000,000 requested new steps; seed 100; 256 environments; exports
at restored zero and expected rounded `1,003,520/2,007,040`; episode length 600;
unroll 20; batch 256; four minibatches; four updates; LR `3e-4`; discount `.97`;
entropy `.005`; imitation `1.0`. Every other source, command, hard-vector,
bridge, reference, reset, phase, reward, and optimizer setting is unchanged.

No source, checkpoint, horizon, vector, reward, LR, entropy, or seed search is
authorized. Recover and hash all artifacts before stopping Colab. Training
reward is excluded from selection.

## Frozen nominal gate

Evaluate both post-update ONNX policies on local CPU with the unchanged external
fitted bridge, deterministic home reset, x=`.074/.077/.080`, seeds `100/101`,
and 1.08 seconds. The evaluator must supply the same applied-target observation
slot from its bridge estimator while retaining sent actions in history.

Both checkpoints must pass all six runs: duration, positive body-frame gait,
bilateral transitions, finite nonconstant actions, saturation `<=1%`, target-
rate excess `<=1e-5 rad/s`, and pitch-chain tracking p95 `<=.20 rad`. Any
failure closes the exact arm without tuning. A pass authorizes only a separately
preregistered x=0 preservation gate.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, deployment, torque, or motor
access is authorized. Colab remains unauthorized until the CPU contract passes.

