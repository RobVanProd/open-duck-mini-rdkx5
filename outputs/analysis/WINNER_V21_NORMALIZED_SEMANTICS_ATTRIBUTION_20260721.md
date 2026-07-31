# Winner-v21 normalized-semantics failure attribution

- Status: `PASS_WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION`
- Decision: `AUTHORIZE_CORRECT_NORMALIZED_PREDICTOR_CPU_CONTRACT_ONLY`
- Physical support pass, half/final: `109/124` / `108/124`; every failure is roll/pitch
- Reported predictor loss, updates 1/50/100: `4.00955e+10` / `1.81992e+10` / `2.12683e+09`
- Root cause: the inherited head outputs normalized coordinates, but Winner-v21 training and its gate treated those values as raw physical responses
- Completed Winner-v21 classification: remains `HOLD` because physical support also fails
- Flat-transport equation: `not selected`
- New simulation / optimizer updates / robot access: `0 / 0 / 0`

The next authorized work is only a zero-update contract for the corrected
normalized-coordinate predictor formula and matching evaluator. No policy
training, response-conditioned locomotion, deployment, or hardware is authorized.
