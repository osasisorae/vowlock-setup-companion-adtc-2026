# Blind Q4/Q8 prose comparison

Eleven paired responses were shown as A and B without their quantization names. The reviewer scored factual support from the supplied evidence, clarity, usefulness and an overall preference. All ratings were saved before the A/B key was opened.

## Result

| Measure | Corrected Q4 | Q8 |
|---|---:|---:|
| Factual points | 20/22 | 17/22 |
| Responses with a factual concern | 2 | 5 |
| Mean clarity | 4.364/5 | 4.273/5 |
| Mean helpfulness | 4.182/5 | 3.636/5 |
| Preference wins | 6 | 4 |

One comparison was a tie. Q4 won the blind comparison and advances as the provisional model for target Ubuntu inference.

## What the review caught

Q8 incorrectly described one target-identification state as if the verifier baseline had already been captured. It also added unsupported phrases such as “immediate action” in several terminal cases. Q4 was usually more faithful to the evidence, although both models wrote awkward, weakly supported action language in the identity and reboot mismatch cases. Q4 also invented that authorization “was not retried” in one terminal-failure explanation.

These are useful failures. The deterministic state machine still preserved the correct decision in every reviewed case, while the prose review showed why schema compliance alone cannot establish explanation quality.

## Limitation

Codex performed this comparison as an AI-assisted technical reviewer. It had implementation context and had seen one Q4 response while validating the review tool. The result is therefore not independent human evidence. An outside human spot-check would strengthen the novice-comprehension claim, but the comparison is sufficient to choose which candidate should receive the next expensive target-machine test.

The machine-readable ratings are in [`benchmarks/ai-assisted-blind-review-results.json`](../benchmarks/ai-assisted-blind-review-results.json). The sealed 24-case set remained closed.
