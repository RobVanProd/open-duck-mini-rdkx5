# Stage A Direct Reset-Outcome Training Audit

Date: 2026-07-11

Status: **ONE-FACTOR TRAINING HYPOTHESIS SUPPORTED**

## Authoritative recipe facts

The saved `smoke_manifest.final.json` for the evaluated rate175 checkpoint
records:

- canonical joystick reset multipliers were not overridden, so training used
  the same default actuator-position multiplier range `0.5-1.5` as evaluation;
- push was disabled;
- actuator bridge was enabled;
- direct alive, velocity, forward-progress, command-progress, base-height,
  pitch, and pitch-rate rewards were active;
- command-progress failure termination was disabled, but ordinary environment
  fall termination remained active and loses future alive/forward return;
- behavior-prior penalty was enabled at scale `-0.6` toward the saved behavior
  teacher;
- restore-policy KL penalty was `4.0`;
- checkpoint rewards increased from 43.09 at step 0 to 57.85 at 163,840 while
  independent canonical-reset evaluation still produced 18/64 one-second falls
  and only 7/64 passes.

The reset distribution was therefore present during learning. Missing reset
coverage is not supported as the explanation. The behavior-prior target has
separately failed outcome-alignment tests and exceeded safe target rates on
failure traces. Its penalty is the smallest identifiable objective term that
constrains direct outcome recovery toward rejected behavior.

## Supported hypothesis

Run one causal training branch identical to the authoritative Stage A recipe
except behavior-prior loss is disabled. Preserve restore KL 4.0, learning rate,
PPO geometry, rewards, bridge, reset distribution, noise, domain randomization,
no-push setting, checkpoint cadence, and source checkpoint.

This is not a claim that removing the prior will succeed. It is the smallest
one-factor test that follows the evidence after local recovery routes failed.
