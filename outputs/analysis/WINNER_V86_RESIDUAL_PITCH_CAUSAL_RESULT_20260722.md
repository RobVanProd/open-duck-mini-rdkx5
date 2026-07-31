# Winner-v86 residual pitch-output causal result

- Status: `PASS_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC`
- Population: `12 exact failed endpoint/configuration/plant pairs x 4 arms = 48 cells`
- Graph / full-teacher / pitch-teacher / non-pitch-zero passes: `0 / 12 / 12 / 0`
- Classification: `12 / 12 pitch_output_causal`
- Mean first-tick pitch-action RMS disagreement: `0.1115330538`
- Mean post-first-tick pitch-action RMS disagreement: `0.1030441558`
- Optimizer updates / locomotion-training steps / robot access: `0 / 0 / 0`
- Result SHA-256: `11225fed5b87a884fa149b1aa6f60ac904017e5ab35fac4587aa8a3f3b10a8d5`

Replacing only the six pitch-chain outputs with the frozen bounded teacher
rescues every remaining Winner-v85 locomotion failure. Replacing all outputs
does the same; zeroing only the non-pitch residual does not rescue any failure.
The remaining locomotion failure mechanism is therefore localized to the six
pitch outputs, not the non-pitch outputs or a required pitch/non-pitch
interaction. The trained graph still differs from the successful teacher by
about `0.10` pitch-action RMS after the first tick.

The frozen learned predictor remains worse than its constant comparator at
both endpoints and plants, but this diagnostic does not modify it and does not
identify it as the locomotion cause. This result selects only a separately
preregistered prospective pitch-output mechanism. It selects no checkpoint,
authorizes no training or support gate yet, and leaves `robot_clearance: false`.
