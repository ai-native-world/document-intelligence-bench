# Data and credential safety

- API keys are read only from the environment variable named by `api_key_env`. Never put a key in a suite.
- A suite sends each case asset to every configured live candidate and sends normalized candidate output plus reference facts to an optional judge. Only use endpoints authorized for that material.
- Reports omit source assets and raw model output by default. They retain digests, fact-level decisions, scores, usage, cost, latency, and errors.
- Treat benchmark suites as code: review endpoints and fixture paths before running them. Local assets and fixture references are confined to the suite directory.
- Do not publish customer corpora, ground truth, reports, or provider error bodies without an explicit data classification review.
