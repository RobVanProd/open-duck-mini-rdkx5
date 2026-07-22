# Winner-v84 negative-gradient pitch-head continuation preregistration

- Source / half / final counts: `675 / 705 / 755`
- Remaining updates: `80`
- Direction: per-update instantaneous negative pitch-teacher gradient
- Scale: norm-match that update's inherited Adam proposal; backtrack `1` through `1/4096`
- Mutable parameters: six pitch action-weight columns and bias elements only
- Optimizer `m/v`: bit-exact preserved; count alone advances
- Snapshot every update; graphs only at `705 / 755`
- Attention / flat-transport equation: `not added`
- Support / selection / deployment / robot authorized now: `0 / 0 / 0 / 0`
