# Winner-v50b gradient-composition ULP attribution result

- Status: `HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION`
- Decision: `DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY`
- Old/new maximum distance: `36,608 / 16,440 signed-float32 ULP`
- Existing bound: `8 ULP`
- Old/new maximum absolute error: `4.76837158203125e-6 / 4.76837158203125e-6`
- Optimizer updates / support cells / exports / robot access: `0 / 0 / 0 / 0`
- Result SHA-256: `55b3b8ce8f16bf10f9870732c951e5719cc115123ae16cb1b2b838f53db4469a`

The exact V50 rollout, scalar evidence, source identity, and both absolute
errors reproduced bit-exactly. Every non-composition V50 check remained green.
The ULP rule nevertheless fails because gradient elements close to zero make a
small absolute difference span many representable values. V50 and V50b both
remain holds, and neither authorizes an optimizer update.

Any next attribution must be separately preregistered. A scale-aware backward-
error rule derived from float32 epsilon is the appropriate next falsification;
the eight-ULP bound must not be widened after observing this result.
