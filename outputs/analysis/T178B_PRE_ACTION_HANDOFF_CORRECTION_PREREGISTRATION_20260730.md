# T178B pre-action handoff correction preregistration

- Status: `PREREGISTERED_T178B_PRE_ACTION_HANDOFF_CORRECTION`
- Scope: first row only from each of the `16` sealed traces
- Compare: context, recurrent input, pre-action joint position, phase, and `obs[83:97]`
- Exclude: current-action applied target and post-step qpos/qvel
- Exact comparison; no tolerance or fitted threshold
- New behavior / optimizer / hosted compute / robot: `0/0/0/0`
- A pass earns only T179 CPU A/B preregistration.
