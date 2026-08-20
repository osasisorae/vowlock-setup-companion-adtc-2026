# The sealed set found one failure

Corrected Q4 took the private 24-case synthetic holdout once. It passed 23 cases under the adaptive automatic gate. One case failed, so the pre-registered zero-contract-failure gate did not pass.

| Sealed result | Value |
|---|---:|
| Cases | 24 |
| Model calls | 49 |
| Adaptive automatic safe passes | 23 |
| Repairs used | 1 |
| Hard or contract failures | 1 |
| False-stop rate | 0.0 |
| Unnecessary-evidence-request rate | 0.0 |
| Required-stop recall | 1.0 |
| Required-evidence recall | 1.0 |
| Mean generation | 13.36 s/call |
| Mean completion speed | 10.92 tok/s |

## What failed

The failing case did not produce an unsafe continuation, invented command or missed stop. Its bounded response reached the 256-token ceiling without closing its JSON object. The single permitted repair also reached 256 tokens and remained incomplete. The verifier correctly rejected both outputs as `INVALID_JSON`.

This distinction matters, but it does not turn the run green. The frozen protocol required zero hard or contract failures. The result is 23/24 and a failed adaptive gate.

## What happens now

There will be no second sealed run and no prompt, token-limit or model revision based on this holdout. Physical Ubuntu profiling can still measure throughput, memory, accuracy and thermals for the challenge report, but those measurements cannot erase the quality failure.

The raw case outputs remain local and ignored. Their SHA-256 is published in [`benchmarks/sealed-q4-summary.json`](../benchmarks/sealed-q4-summary.json), along with the frozen input hashes and aggregate result. The sealed fixtures themselves remain private so they cannot become training material or a disguised development set.

This is useful evidence: a model can pass every visible development case and still fail once when a hidden case demands a longer structured explanation. The independent verifier prevented that incomplete explanation from being accepted.
