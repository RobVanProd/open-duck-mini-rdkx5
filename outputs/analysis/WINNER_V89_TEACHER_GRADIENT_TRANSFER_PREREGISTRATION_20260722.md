# Winner-v89 teacher-gradient transfer preregistration

- Checkpoints: exact V84 half/final at `705 / 755`
- Folds: `12` leave-one-configuration-out per checkpoint
- Groups: recurrent core / action head / combined policy
- Transfer sign: `dot(g_train, g_heldout) > 0`
- Coherence: all `12 / 12` folds positive
- Optimizer updates / support cells / artifacts / robot access: `0 / 0 / 0 / 0`
