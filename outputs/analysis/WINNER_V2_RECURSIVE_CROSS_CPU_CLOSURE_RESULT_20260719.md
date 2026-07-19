# Winner-v2 Recursive Cross-CPU Closure Result — 2026-07-19

Decision: `PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE`

The formal post-preregistration Windows CPU result passes the frozen selected
512000-step x=0/x=.080 matrix. The policy-side Linux CPU replay independently
reproduces the same decision. This closes the reviewed CPU recursive-numeric
blocker for runtime-v2; it does not close physical COM, X5 CPU preflight, Gate
5, deployment or robot clearance.

## Formal runtime result

- runtime result commit: `f8def264c856db3905301f5473f5eb1775b3eec0`;
- result SHA-256: `e1842ca64e91056b96c297666803bdeec7c5ff2950d4dfe32e27044379049b14`;
- provider: `CPUExecutionProvider`;
- ticks: `2400`;
- direct same-input maximum: `4.76837158203125e-07`
  (frozen limit `9.9999999999999995e-07`);
- selected logical-target maximum: `5.9604644775390625e-07 rad`;
- selected P30 maximum: `5.6025073202903286e-07 rad`;
- frozen half STS count: `0.00076699039394282058 rad`;
- selected raw STS goal mismatch: `0 / 16800 words`;
- saturation/rate/envelope classifications unchanged: `true`.

The 1024000 sibling was run and recorded but remained non-gating exactly as
preregistered. The runtime reused its existing versioned v2 result filename;
this is accepted because the preregistration froze content, method and formal
post-commit ordering, not an exact result filename.

The runtime-side request and formal-result commits were concurrent siblings
from the same baseline and were subsequently merged. The formal result remains
valid because the authoritative policy preregistration predates the formal
commit, the formal verifier binds its exact commit, and the committed runtime
record attests a fresh 2,400-tick post-preregistration invocation. The request
commit itself was advisory, not the authority boundary.

## Independent policy-side replay

- provider: `CPUExecutionProvider` on `Linux-7.0.0-27-generic-x86_64-with-glibc2.43`;
- ticks: `2400`;
- selected logical-target maximum: `0 rad`;
- selected P30 maximum: `5.9576471311828527e-08 rad`;
- selected raw STS goal mismatch: `0 / 16800 words`;
- selected x=0 action/state/target/P30: bit-exact.

All formal provenance, four-cell matrix, identity, completeness, fault-
injection, same-input, native-resolution and authority checks pass. Runtime
tests separately pass `246/246`, and the runtime artifact hash check is clean.

## Authority

`PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE` closes only the reviewed CPU recursive-numeric blocker. Robot
clearance remains `NO`. Still required are the powered-off direct-reaction
torso-COM packet, a reviewed frozen runtime/policy/config asset set, and the
same CPU-only native-resolution replay on the X5 without servo access. No
robot, RDK-X5, motor, torque, deployment, GPU or iGPU action occurred here.
