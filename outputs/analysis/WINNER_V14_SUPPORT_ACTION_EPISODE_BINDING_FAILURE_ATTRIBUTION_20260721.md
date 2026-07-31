# Winner-v14 support-action episode-binding failure attribution

- Status: `INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_EPISODE_BINDING`
- Decision: `CORRECT_ONLY_REVIEWED_EPISODE_TYPE_BINDING_AND_FRESHLY_PREREGISTER`
- GitHub run / attempt: `29833729219 / 1`
- Completed main / repeat cells: `0 / 0`
- Training / locomotion / robot access: `0 / 0 / 0`

The hash-corrected runner entered the first loop iteration but stopped
before constructing an episode or stepping physics. The reviewed base
runner owns its Episode through the imported CPU-smoke module. Only the
adapter reference changes from `base.Episode` to `base.smoke.Episode`.
