# Grounded Rate165 Candidate Current-Tool Regression Preregistration

Date: 2026-07-11

Status: **PRE-REGISTERED; NOT RUN**

The preserved candidate
`policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703` has
matching recorded hashes and an authoritative 8/8-by-command offline result
under `rough_terrain_backlash`, terrain `z=0.0026`, `home-support` reset,
corrected fitted bridge, and 15-second duration.

Run a current-tool regression on seed 0 only at `x=0` and `x=0.08` with those
conditions unchanged, no push, no settle, no policy-action modification, and
no reward override.

Decision rule:

- both commands pass with duration completion, zero velocity excess, tracking
  <=0.20 rad, `x=0.08` ratio >=0.25 and velocity >=0.02 m/s: current default
  evaluator compatibility is confirmed; retain the existing authoritative 8/8
  evidence without spending CPU to reproduce identical seeds;
- either command fails or a contract field differs: do not retain compatibility
  by assumption; preregister and rerun the complete 8/8 gate.

CPU only with JAX and both GPU visibility variables forced off. No robot, SSH,
deployment, grounded replay, or moving hardware test.
