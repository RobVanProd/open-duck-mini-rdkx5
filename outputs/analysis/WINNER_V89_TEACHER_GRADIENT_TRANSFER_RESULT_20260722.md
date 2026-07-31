# Winner-v89 teacher-gradient transfer result

- Status: `PASS_WINNER_V89_TEACHER_GRADIENT_TRANSFER_DIAGNOSTIC`
- Classification: `STATIC_TEACHER_GRADIENT_NONTRANSFERABLE`
- Selected checkpoint / gradient group: `none / none`
- Half positive folds, recurrent / action / combined: `4 / 5 / 5` of `12`
- Final positive folds, recurrent / action / combined: `5 / 6 / 5` of `12`
- Half combined dot sum: `-0.1477081517`
- Final combined dot sum: `-0.2016172518`
- Gradient evaluations / optimizer updates / artifacts / robot access: `48 / 0 / 0 / 0`
- Result SHA-256: `0197add105f174eb856613fa62d773fa633841266724f4d76a791fd2fd250a20`

The per-configuration static teacher is not a transferable learning objective.
For both endpoints, gradients learned on eleven configurations oppose the
held-out teacher gradient more often than they align. The summed dot product
is negative for recurrence, the action head, and their union. This explains
why table imitation can repair selected cells while failing persistence.

The result selects no teacher-gradient step and authorizes only a separately
preregistered outcome-aligned mechanism diagnostic. No parameter changed, no
policy artifact was written, no checkpoint was selected, and
`robot_clearance` remains false.
