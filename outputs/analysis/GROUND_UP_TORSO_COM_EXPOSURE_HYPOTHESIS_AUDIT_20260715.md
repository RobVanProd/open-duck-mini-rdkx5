# Ground-Up Torso-COM Exposure Hypothesis Audit

status: `PASS_EXPOSURE_GAP_HYPOTHESIS_FALSIFIED`

The narrow remediation hypothesis was that corrected torso-X failure was
caused by zero training exposure to the true inertial torso COM axis, and that
adding full-range exposure could resolve it without changing policy
observability or architecture. The completed experiment rejects that
hypothesis as a sufficient explanation.

| evidence | cells | full duration | sample range | mean vx range m/s | worst tracking p95 rad |
|---|---:|---:|---:|---:|---:|
| pre-remediation X_NEG | 16 | 0 | 41-47 | -0.410971 to -0.371851 | 0.161377 |
| remediation nominal | 48 | 48 | 600 | -0.000658 to 0.093153 | 0.182504 |
| post-remediation X_NEG | 48 | 0 | 42-55 | -0.410235 to -0.319612 | 0.162542 |
| post-remediation X_POS | 48 | 12 | 50-600 | 0.000197 to 0.424365 | 0.183278 |

All three arms received the corrected body-2 targeted COM distribution and
two full-range checkpoints. Yet post-remediation X_NEG reproduces the prior
backward reversal magnitude, while X_POS preserves all twelve x=0 cells and
drives every moving cell forward at 0.254248-0.424365 m/s before falling.
Nominal behavior remains fully preserved and endpoint tracking stays below the
0.20-rad gate.

Therefore exposure alone does not solve the failure. This audit does not by
itself choose memory, an explicit COM input, or a narrower certified range.
The separately preregistered observability decode determines whether the saved
actor input already contains identifiable COM information.
