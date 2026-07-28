# T71 T67 COM-hidden causal result

- Status: `PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED`
- Classification: `COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE`
- Decision: `SELECT_TRANSITION_CONTROL_RESCUE_FALSIFIER`
- New simulator cells / optimizer / Colab / robot: `0/0/0/0`

The paired hidden state is plant-sensitive and causally changes the moving action while the current observation is held fixed. The remaining problem is the learned response, not missing COM information.
