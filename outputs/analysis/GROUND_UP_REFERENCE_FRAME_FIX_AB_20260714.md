# Ground-Up Reference Frame Fix A/B

Status: `PARTIAL_EFFECT_HARD_GATE_FAIL`

FRAMEFIX4 used the same seed, canonical recipe, 4,014,080-step horizon,
backlash task, and evaluation suite as R00W4. Its only learning change was the
body-local reference-velocity repair.

- Artifact SHA-256: `a4917562e1c87334e33e3b60b2fc2ffd7ba60c98573bb9c9f5d572585781d177`
- Patch SHA-256: `b52cb6c5269cadd74a15d9b551bd5616130800fcd54298e00e15e07c6580dde9`
- T4 training time: `1064.2445586420001 s`
- VM stopped after verified download

At 4,014,080 steps, the repair changed x=0.08 seed 100 from reverse motion to
a clean positive run:

| condition | world dx m | mean local vx m/s | termination |
|---|---:|---:|---|
| R00W4 seed 100 | -0.038768 | -0.054608 | duration complete |
| FRAMEFIX4 seed 100 | 0.049567 | 0.057171 | duration complete |

However, seed 101 regressed to an early fall and reverse motion
(`dx=-0.163517 m`, local `vx=-0.117182 m/s`). Both x=0 runs also did not remain
finite. The repair therefore has a measurable causal effect but fails the hard
gate and is not a candidate.

## Next evidence-backed correction

The preregistered stage-1 curriculum requires a zero-command and
positive-command mixture. The pinned upstream sampler instead uses x commands
uniformly from `-0.15` to `0.15` and selects exact zero only 10% of the time.
That does not implement the frozen stage-1 curriculum.

`patches/ground_up_stage1_command_mixture.patch` adds an opt-in distribution:

- 50% exact locomotion command zero;
- 50% forward x uniformly in `[0.04, 0.12]`;
- locomotion y and yaw fixed at zero;
- no negative x samples.

A deterministic 10,000-sample CPU contract measured zero fraction `0.4936`,
moving fraction `0.5064`, moving x range `[0.04000347, 0.11997301]`, zero
lateral/yaw magnitude, and zero negative-x samples.

The next bounded A/B retains the valid frame correction and adds only this
already-preregistered stage-1 command distribution. No robot, RDK, onboard
GPU, or local accelerator is authorized.
