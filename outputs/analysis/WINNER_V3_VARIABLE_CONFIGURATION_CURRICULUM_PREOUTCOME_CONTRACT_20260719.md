# Winner-v3 Variable-Configuration Curriculum Pre-outcome Contract — 2026-07-19

Status: `PASS_WINNER_V3_CURRICULUM_PREOUTCOME_CONTRACT`

The implementation, integration patch, deterministic composer and formal CPU
checker are hash frozen before any curriculum PPO step or behavior cell. The
single candidate, seed, 25%/50%/100% stage schedule, reward, protected restore,
persistent checkpoints, 1,024-cell matrix and no-retry rule remain unchanged.

The implementation represents the full torso inertia tensor through MJX's
principal inertia plus inertial-frame quaternion, targets named inertial body 2,
uses one all-link mass scale, and records exact model and episode readback. The
actor receives no true configuration parameter. Disabling winner-v3 must match
the pre-patch simulator trace bit-exact.

- formal curriculum PPO steps read or executed: `0`
- formal behavior cells read or executed: `0`
- failed checks: `[]`

A pass authorizes only the formal CPU implementation contract. It is not a
candidate behavior result and grants no hosted allocation, GPU/iGPU, RDK-X5,
robot, runtime, Gate 5, deployment, torque, motion, or clearance authority.
