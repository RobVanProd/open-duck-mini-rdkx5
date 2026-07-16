# Upstream Finding: MJX JIT/Eager Forward Discrepancy

Status: `ISSUE_READY_SCOPE_LIMITED`

## Summary

For one deterministic Open Duck Mini tick-zero state, an eager `mjx.forward`
sensor branch exactly matches independently constructed negative and positive
torso-COM endpoint oracles. Three JIT forms miss the same endpoint oracle:

| form | combined endpoint max error |
|---|---:|
| eager replace-inside | 0 m/s^2 |
| JIT replace-inside sequential | 0.0268936157 m/s^2 |
| JIT model-argument sequential | 0.0269031525 m/s^2 |
| JIT paired endpoints | 0.0268936157 m/s^2 |

The JIT variants reproduce the prior invalid half-direction to within
0–7.24196e-6 m/s^2. Constructing the model outside JIT and returning both
endpoints from one compiled call do not remove the discrepancy.

## Scope

This is an effective-n=1 deterministic methods reproduction with zero dynamic
steps and zero actor calls. It supports a JIT-versus-eager discrepancy in this
tick-zero `mjx.forward` accelerometer diagnostic branch. It does not establish
a general MJX dynamics or training defect.

## Reproduction assets

- Tool: `tools/run_ground_up_torso_com_mjx_jit_boundary_audit.py`
- Frozen result:
  `outputs/analysis/ground_up_torso_com_mjx_jit_boundary_audit_result.json`
- Result decision: `GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED`

The reproduction constructs body-2 X-COM endpoints, evaluates the same
accelerometer sensor in four execution forms, and compares all endpoint vectors
to an independent eager oracle. All execution is CPU-only.

## Suggested upstream test

Turn the four frozen variants into a minimal model fixture, record exact
JAX/JAXLIB/MuJoCo/MJX versions, and bisect with X64 and compiler optimization
settings explicitly fixed. Require eager and JIT endpoint sensor vectors to
agree within a declared numerical tolerance. Until resolved, keep this
diagnostic read eager and default-off; do not infer that ordinary compiled
rollouts are invalid.

