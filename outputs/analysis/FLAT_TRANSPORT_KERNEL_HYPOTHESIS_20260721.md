# Flat long-range transport kernel hypothesis

Status: `RECORDED_NOT_SELECTED`

The proposed kernel is

\[
K_{n,L}=\rho^L I_n+q(1-\rho^L)C_n,
\]

where the final row of \(C_n\) is \((1/n,\ldots,1/n)\). Therefore the global
component delivered to the final row assigns the same coefficient
\(q(1-\rho^L)/n\) to every sequence position. The identity term preserves a
separate local residual. This is a constructive counterexample to the claim
that quadratic attention is required for flat long-range information
transport.

It is not used by the active Winner-v13 run. The current 64-state recurrent
encoder already passed its 250-tick observability and one-update contracts, so
changing transport during the frozen support-controller experiment would
confound the result.

The kernel becomes eligible as one isolated falsification only if the frozen
support evidence attributes failure to temporal information loss—for example,
early configuration information is demonstrably present but no longer
recoverable late in the 250-tick sequence. Such a test must preserve the
115-element observation contract, action boundary, training/evaluation
populations, checkpoint rule, and all support thresholds. It grants no
training, locomotion, robot, or deployment authority by itself.
