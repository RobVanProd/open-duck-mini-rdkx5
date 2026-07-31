# Ground-Up Scaled Control T4 Probe

status: `PASS_SCALED_CONTROL_T4_PROBE`

The pinned upstream task plus the minimal PPO-scale patch completed on a T4.
The one-shot session stopped itself and `colab sessions` showed no retained
session after completion.

- environments: `256`
- timesteps requested/completed: `1,000,000 / 1,003,520`
- episode/unroll: `600 / 10`
- batch/minibatches/updates: `256 / 4 / 4`
- evaluations: `2`
- training wall time: `794.54 s`
- total session-script wall time: `845.70 s`
- measured end-to-end training throughput: `1,258.59 steps/s`
- checkpoints: `2`
- ONNX exports: `2`
- evaluation reward step 0: `13.81025`
- evaluation reward step 1,003,520: `65.61880`
- exact compute units: not exposed by the CLI
- conservative ledger charge: `3` search units

The final exporter's sampled action is near saturation on multiple joints. This
is expected to be an immature checkpoint and is not a policy candidate. Reward
growth alone is not a search gate.

The result proves a usable T4 scale and export path. It also shows that a
300-million-step run at this measured end-to-end rate would require roughly
`66.2 hours` of training before setup overhead. Therefore the search must use
successive halving and improve parallel throughput before committing to a full
canonical-length finalist.

No robot, local GPU, deployment, or hardware action occurred.
