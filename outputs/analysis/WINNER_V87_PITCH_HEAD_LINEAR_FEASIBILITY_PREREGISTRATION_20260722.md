# Winner-v87 linear pitch-head feasibility preregistration

- Sources: exact Winner-v84 half/final checkpoints at `705 / 755`
- Data: one frozen 80-episode stage-2 rollout per checkpoint
- Teacher population: `16 configurations x 2 plants` per checkpoint
- Fit: affine hidden-state pitch head in teacher-logit space
- Validation: leave one configuration (both plants) out, 16 folds
- Optimizer updates / support cells / robot access: `0 / 0 / 0`
