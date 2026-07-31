# Single-support balance curriculum hypothesis

Status: documented fallback hypothesis; not selected; zero decision weight in
the active T45/T46 path.

## Mechanism

Pretrain one unchanged policy ABI through a staged balance curriculum:

1. randomized left- and right-foot single-support holds;
2. weight shifts without stepping;
3. unloaded-foot lift and replacement;
4. alternating support near zero forward speed;
5. gradual introduction of the walking reference and command support.

The hypothesis is that learning a broad single-support recovery basin before
propulsion reduces the coupled discovery burden of balance, foot transfer, and
forward motion. IMU, joint, contact, phase, and applied-target observations
remain unchanged.

## Important distinction

Static one-foot pose memorization is not the mechanism. Support duration, pose,
disturbance, and transfer timing must vary so the policy learns recovery and
dynamic handoff instead of a freeze-and-brace strategy.

## Selection boundary

Do not interrupt or reinterpret the current uniform-final-base robustness
ladder. Consider this only if the current candidate family closes and the
campaign explicitly reopens gait-level training. Before hosted training, freeze
a CPU-only curriculum-transition contract and show that a single policy can
retain both support holds while beginning alternating support.
