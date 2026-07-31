# Winner-v101 response-conditioned CPU retry preregistration

Winner-v100 reached the PPO subprocess but stopped before environment construction, reset, locomotion, or optimization because an unused generic exporter eagerly imported TensorFlow. Winner-v101 changes only that import boundary. Policy/calibrator equations, training settings, thresholds, golden checks, and behavior gates remain frozen. Exactly one CPU smoke is authorized; no hosted or robot work is authorized.
