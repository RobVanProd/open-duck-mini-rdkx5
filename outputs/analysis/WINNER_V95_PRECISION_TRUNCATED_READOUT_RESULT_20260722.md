# Winner-v95 precision-truncated readout result

- Status: `PASS_WINNER_V95_PRECISION_TRUNCATED_READOUT`
- Source support: `112 / 112`
- Original / retained rank: `65 / 28`
- Retained condition / float32 amplification: `7294.139 / 0.000869529`
- Float64/float32 maximum heldout delta: `0.0000933107`
- P30 fitted / frozen / constant MSE: `0.009943 / 0.930858 / 0.866829`
- P31/34 fitted / frozen / constant MSE: `0.009649 / 0.933975 / 0.869110`
- Maximum coefficient magnitude: `128.039`
- Combined coefficient SHA-256: `ccab7d2a...43419e76`
- Result SHA-256: `034e2e65c6d4f92082bfba63f8b2c57f6e79d0d2b97627f1021ff727106cab55`

The cutoff derived solely from the frozen float32 condition bound retains 28
response directions and passes every numeric, heldout, and support check. The
frozen recurrent encoder plus universal action now has a stable, transferable
response-observer contract.

This pass authorizes only a separately preregistered CPU contract for the
response-conditioned locomotion mechanism. It does not select a deployment
checkpoint or authorize training, deployment, Gate 5, or robot access.
