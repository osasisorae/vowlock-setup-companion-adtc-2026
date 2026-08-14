# Development change log

The sealed set has not been evaluated. The revisions below came only from tests and development-fixture runs, as permitted by `experiment-protocol.json`. Invalidated local outputs remain under ignored `benchmarks/results/` and cannot support a model claim.

## 14 August 2026 — scorer 0.1.0 invalidated

The first unconstrained Qwen3 0.6B development run exposed two verifier defects:

1. Markdown JSON fences were classified as an invented command. A fence is invalid response formatting, but it is not itself a command.
2. Any incomplete consequential response with `can_advance: true` was classified as a false continuation—even when the deterministic expected decision was `CONTINUE`.

Scorer 0.1.1 removes the fence from command markers and defines false continuation only when the deterministic decision is not `CONTINUE`. Regression tests cover both cases. The original output is retained locally as `qwen3-0.6b-q8_0-development-verifier-v0.1.0-invalidated.json`.

## 14 August 2026 — general response schema invalidated

The next run used the full explanation JSON schema, but that schema allowed the model to choose authority-bearing fields such as `decision`, `can_advance`, `requested_evidence`, `risk_codes` and `fact_codes`. This contradicted the architecture: deterministic code had already decided those values.

The bounded runner now creates a per-case schema that binds every authority-bearing field to a deterministic constant. The model generates only `headline`, `explanation` and `next_step` wording. The ordinary one-shot remains unconstrained and isolated for comparison. The superseded output is retained locally as `qwen3-0.6b-q8_0-development-general-schema-invalidated.json`.

This is not a prompt trick that teaches the answer to a decision-making model. It removes decision-making from the model entirely, which is the stated safety design. Human review is still required for the three generated prose fields; schema conformance cannot prove that prose true or understandable.
