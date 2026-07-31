# Ground-Up Tracking-Tail Rate-Boundary Audit

status: `PASS_RATE_BOUNDARY_AUDIT`
decision: `PREREGISTER_STATEFUL_PITCH_RATE_BOUNDARY_CPU_SCREEN`

pooled exceedance recent-boundary fraction: `0.9762675296655879`
pooled non-exceedance recent-boundary fraction: `0.7973260407171072`
odds ratio: `10.456537555432385`
minimum / mean top-four period-bin coverage: `0.8831168831168831` / `0.9751845080351601`
derived pitch-rate multipliers: `[0.9799092569101565, 0.959818513820313, 0.919637027640626]`

Gate-setting exceedances are phase-local and 97%+ occur at or within two ticks after the measured target-rate boundary, with an odds ratio above five. This supports a CPU-only stateful ONNX boundary A/B, not another reward or training run. Candidate multipliers are frozen from the exact T3-final gate ratio and 1x/2x/4x that measured gap before outcomes.
