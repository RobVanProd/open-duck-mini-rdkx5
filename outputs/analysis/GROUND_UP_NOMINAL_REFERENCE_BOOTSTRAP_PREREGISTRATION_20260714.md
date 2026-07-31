# Ground-Up Nominal Reference Bootstrap Preregistration

status: `PREREGISTERED_BEFORE_ACCELERATOR_COMPUTE`

## Evidence basis

The scalar screen and five-family mechanism screen produced no Stage-1 winner.
The shared-setup audit then found that the polynomial reference was active, but
the declared curriculum was not staged: domain randomization, randomized reset
state, observation noise, action/IMU delay, random head commands, and pushes
were active from the first update.

The same audit found three deterministic reference-contract mismatches:

- reset phase feature `[0,0]` has norm zero, whereas valid cyclic phase features
  have norm one;
- reference phase 0 requests single support `[1,0]` and has squared leg-pose
  error `0.3624896421` from home;
- phase 20 is the closest reference phase that is both double support and
  home-compatible, with squared error `0.1126807559`;
- continuous commands `[0.04,0.12]` map 88.75% to reference cell `0.074` and
  11.25% to cell `0.148`, while the command-tracking objective still uses the
  original continuous command.

This screen corrects the ordering problem before changing the reward or another
policy topology. It asks whether a policy can first learn the frozen reference
under a genuinely nominal stage, and whether deterministic phase alignment is
causal.

## Frozen implementation contract

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- base and mechanism patch stack unchanged;
- nominal-bootstrap patch SHA-256
  `0d89b85815eb570115ec5f35d677aba68299f977b3e36c60b10dfa869533ebba`;
- CPU contract status `PASS_CPU_CONTRACT` for phases 0 and 20;
- canonical MLP actor, privileged critic, observation 101, action 14;
- seed `100`, 256 environments, 4,014,080 steps;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`, unroll `20`;
- exact command x=`0.074`, y/yaw/head=`0` throughout training;
- deterministic home reset and zero base velocity;
- observation noise, action delay, IMU delay, pushes, and domain randomization
  disabled;
- `flat_terrain_backlash`; no rough terrain;
- valid unit-norm phase feature and matching reference frame at reset.

The 4,014,080-step bound is not guessed: the earlier frame-fix causal A/B first
showed a positive seed-100 moving run at exactly that checkpoint. This is a
causal bootstrap screen, not finalist training.

## Candidates

| ID | reference start phase | purpose |
|---|---:|---|
| `B0_NOMINAL_PHASE0` | 0 | clean nominal-stage control with a valid phase feature |
| `B1_NOMINAL_PHASE20` | 20 | one-factor home-compatible double-support alignment |

No other value differs between candidates.

## Frozen evaluation and advancement

Evaluate checkpoints 3,010,560 and 4,014,080 on local CPU with the same fitted
actuator bridge at x=`0.074` and x=`0.08`, seeds `100/101`, duration `1.08 s`.
Each policy is evaluated with its own frozen reference start phase. The x=.074
condition tests its exact training/reference cell; x=.08 tests the project
command without changing the reference cell.

A bootstrap candidate advances only if:

1. every positive-command run completes the full duration;
2. every run passes moving emergence;
3. the same seeds pass at both checkpoints;
4. there are zero hard failures or constant saturated action vectors.

Training reward is excluded. A least-bad candidate does not advance. If neither
qualifies, status is `NO_NOMINAL_REFERENCE_BOOTSTRAP_WINNER` and the next
question is the outcome-aligned objective, not more phase choices, longer runs,
architectures, or scalar tuning.

A pass authorizes only a separately preregistered Stage-2 continuation that
adds true x=0 semantics. Randomization, delay, actuator robustness, pushes,
rough terrain, baseline comparison, offline clearance, RDK runtime work, and
robot validation remain later gates.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, deployment, torque, or motor
access is authorized.
