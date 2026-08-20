# One-time sealed evaluation procedure

The selected model and prompts are frozen. The local 24-case synthetic holdout still contains no physical-device evidence and remains excluded from Git.

`tools/run_sealed_once.py` changes no generation, scoring, repair or safety logic. It exposes the existing experiment path to fixtures whose declared split is `sealed`, while the original development entry point remains development-only.

Before the first model call, the runner:

1. refuses to start if a prior start marker exists;
2. verifies the selected model against `benchmarks/model-selection.json`;
3. verifies all frozen prompt hashes;
4. verifies every sealed fixture name and hash;
5. writes an ignored `sealed-run-started.json` marker.

The start marker remains even if the process crashes. There is no force or retry option. On completion, the marker gains the raw-output hash and summary. Raw case outputs stay under ignored `benchmarks/results/`; only a reviewed aggregate result may be published.

The harness-only change is committed before the run. It is necessary because the original CLI deliberately rejected every non-development fixture. It does not alter the selected model, prompt text, response contract, verifier, resource limits or per-case generation path.
