# T98 hidden-gated expert CPU preregistration

- Status: `PREREGISTERED_T98_HIDDEN_EXPERT_CPU_CONTRACT`
- Source: exact T78 final checkpoint
- Gate: fixed T97 live-hidden linear classifier
- New actor state: one zero-initialized 64×14 correction head
- Trainable: correction head and critic only
- Mature actor / normalizer: bit-exact frozen
- Reward / optimizer / ABI / runtime-input changes: `0/0/0/0`
- CPU steps / behavior / hosted / robot now: `1024/0/0/0`

A pass earns only a separate hosted-run preregistration.
