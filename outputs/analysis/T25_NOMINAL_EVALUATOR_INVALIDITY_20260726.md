# T25 nominal evaluator invalidity attribution

- Status: `PASS_T25_NOMINAL_EVALUATOR_INVALIDITY_ATTRIBUTION`
- All 16 attempted cells stopped before a trace because the evaluator omitted the graph's required diagnostic context.
- The context input is proven bit-exactly ignored; explicit float32 zeros rectify only the evaluator feed.
- The invalid execution has zero policy decision weight.
- Policies, matrix, gates, seeds, simulator, and training remain unchanged.
