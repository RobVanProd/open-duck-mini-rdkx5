# Fable follow-up — V124/V125 falsification results and next mechanism

## What was tested

We implemented your S0–S2 plan before any wrapper rollout or hosted training.
We also preregistered your requested ruling before seeing behavior: applying one
unchanged deterministic wrapper to both independently frozen V121 checkpoints
would satisfy the both-checkpoint rule, but both would still need to pass all
eight cells.

No behavior rollout, training, Colab, RDK-X5, robot, torque, or motion occurred.

## S0 — exact source closure passed

The source corrected two simplifying assumptions in the proposed equation:

- The frozen backlash scene uses `kp=17.11`, `kv=0`, and actuator
  `forcerange=[-3.23, 3.23] N·m`.
- The exact gate torque half-width is therefore
  `1.91229675 / 17.11 = 0.111764924 rad`, not the previously inferred
  `0.143028927 rad` based on `kp=13.37`.
- The bridge appends the current sent target before indexing its delay queue.
  A command at decision tick `t` first changes bridge output at `t+d`.
  The corresponding logged force is sampled after that control interval at the
  final 2 ms semi-implicit Euler substep.
- The exact bridge is piecewise affine, not just affine: delay, home-relative
  gain, first-order lag, then a per-joint applied-target velocity clip.

Closure over all 32 frozen V121/V123 traces:

- bridge applied-target maximum absolute reconstruction error:
  `4.8680487e-8 rad`;
- actuator-force maximum absolute reconstruction error:
  `3.6774548e-6 N·m`;
- reported current maximum absolute reconstruction error: `0 A`;
- current source law: `I=|tau|/0.784532`;
- the torque gate maps to exactly `2.4375 A`, so it is stricter than the
  `2.5 A` peak-current gate;
- the `>2 A` dwell boundary remains `|tau|>1.569064 N·m`.

The force reconstruction uses the source-aligned force position
`q_force=qpos_post-0.002*qvel_post`.

## S1 — your causal and credit diagnosis passed

Using the exact piecewise bridge and realized source-aligned future `q`:

- V121: `15/15` events locally preventable, `0` committed before the last
  controlling decision;
- V123: `181/184` locally preventable (`98.3696%`);
- the three nonpreventable V123 events are consecutive right-knee events where
  the torque-safe lower target lies above the frozen G3/rate-feasible upper
  target.

The episode-running-max credit audit also confirms your mechanism:

- V123 torque element events: `184`;
- events that directly set a new per-episode global maximum: `37`;
- events with zero direct running-max credit: `147` (`79.8913%`);
- intended un-clipped objective price across the 16 nominal traces:
  `847.945094`;
- realized price after the environment's per-step reward clip:
  `16.126064`;
- fraction of intended price removed by clipping: `98.0982%`;
- base reward reconstruction maximum error: `8.704e-8`.

Thus the V123 objective was both order-statistic sparse and almost completely
price-capped. This is now source- and trace-backed, not an inference.

## S2 — your constant-velocity predictive box failed

We used exactly the proposed reserve discipline:

`reserve_j = max(p99.9 passing q-prediction error,
                 max V121-event precursor error)
             + frozen measurement/goal quantization floor`

The measurement/goal floor is about `0.002361 rad`, composed of half a present
position LSB, the horizon-scaled half velocity LSB, and one full truncating goal
position LSB.

Constant-velocity `qhat=q+h*qdot` produced these decisive pitch-chain reserves:

| joint | p99.9 error rad | reserve rad | remaining torque half-width rad |
|---|---:|---:|---:|
| left hip pitch | 0.128659 | 0.131020 | -0.019255 |
| left knee | 0.119332 | 0.121693 | -0.009928 |
| left ankle | 0.119483 | 0.121844 | -0.010079 |
| right hip pitch | 0.122076 | 0.124437 | -0.012672 |
| right ankle | 0.153096 | 0.155456 | -0.043692 |

Result:

- positive torque-safe half-width every joint: **false**;
- empty robust-box/supreme-constraint intersections:
  `20,048 / 50,148 joint-ticks`;
- existing strict `>2 A` dwell still passes, worst `10` ticks;
- no wrapper screen was authorized.

This is the empirical answer to the question you left open: the box is not
livable when it carries the preregistered constant-velocity prediction reserve.
Oracle realized future `q` proves the events are action-reachable, but runtime
state cannot predict that `q` tightly enough with the proposed low-order model.

## V125 — one parameter-free second-order falsifier also failed

Before abandoning the family, we preregistered the unique next Taylor term:

`qhat=q+h*qdot+0.5*h^2*((qdot-qdot_prev)/0.02)`

There was no fitted coefficient, smoothing, clipping, predictor selection, or
rollout. All V124 equations, traces, reserve rules, boxes, and constraints
remained frozen.

It was worse:

- all `15/15` V121 event precursors became reserve-infeasible;
- empty intersections increased to `21,925`;
- left-knee reserve rose from `0.121693` to `0.170207 rad`;
- right-ankle reserve rose from `0.155456` to `0.227132 rad`;
- the preregistered rule therefore closes the entire low-order kinematic
  predictive-box family.

We will not try smoothing, acceleration clipping, coefficient searches, a
third Taylor term, or post-hoc reserve relaxation.

## What remains true

- The blocker is still a small physical torque/current population, not gait,
  tracking, rate, saturation, or x=0 behavior.
- V121-half remains `8/8`; V121-final remains `3/8`.
- Every V121 torque event is locally action-reachable with oracle realized
  future state.
- The reward-objective family used so far did not deliver the required
  per-tick constraint.
- A deployable exact projection cannot currently carry a defensible prediction
  reserve across the 58–78 ms delayed horizon.
- Long-range transport/attention remains causally unrelated.

## Forced next-mechanism question

Please select and specify the single best **different mechanism class** now
earned by this evidence. Do not propose another predictor coefficient,
reserve relaxation, scalar sweep, or reward-curve selection.

The leading candidates are:

1. **Constrained PPO with a separate cost critic and adaptive Lagrange
   multiplier.** The cost channel is per-tick torque exceedance, remains
   unclipped, gets its own GAE/value bootstrap, and is not mixed into the
   environment reward. This directly fixes both V123 defects but still relies
   on learned precursor credit.
2. **A learned short-horizon safety model/barrier layer.** Train only a
   source-state/action-to-future-torque model on preregistered CPU
   counterfactual branches, validate it with a held-out conformal bound, then
   project actions. This replaces the failed low-order `q` predictor but risks
   model/distribution dependence and deployment complexity.
3. **Projected-teacher distillation or constrained trajectory teacher.** This
   no longer has the wrapped V121-half teacher prerequisite because the
   reserve-aware wrapper did not reach a behavior screen; explain what teacher
   can be validly constructed without relaxing the safety box.
4. A fourth mechanism only if it is mechanically distinct and has a cheaper
   CPU falsifier than the options above.

For the selected mechanism, please provide:

- the causal reason it addresses the now-proven failure;
- exact equations and where they enter the recurrent PPO/deployment graph;
- every new state/input and whether the frozen 115-D policy ABI changes;
- a CPU-only falsification/contract plan;
- a no-run condition;
- the exact evidence required to earn at most one hosted continuation;
- how both half/final checkpoint persistence remains protected;
- the deterministic stop rule if that one run fails.

The goal remains a policy that passes both nominal checkpoints and then the
full frozen robustness matrix before RDK-X5 Gate 5. No robot clearance exists.
