# Static development baseline

**Run date:** 12 August 2026  
**Experiment contract:** 1.0  
**Scorer:** 0.1.0  
**Split:** 11 invented development fixtures

## Result

| Measure | Observed result |
|---|---:|
| Fixture-label agreement | 11/11 |
| Safe-action accuracy | 100% |
| Perfect static contract scores | 11/11 |
| Mean score | 10.0/10 |
| Hard failures | 0 |
| False-stop rate | 0% |
| Unnecessary-evidence-request rate | 0% |
| Necessary-stop recall | 100% |
| Necessary-evidence-request recall | 100% |

The source-controlled renderer preserved every deterministic decision, exact evidence request and required risk code in the development set. Its prose was constructed only from evaluator-owned facts, so it received the rubric's two factual-support points without pretending that arbitrary natural language had been automatically verified.

## What this does not establish

This is a contract regression, not evidence that the guidance helps a novice. The renderer and development fixtures share the same deliberately small vocabulary, so a perfect result is expected if the implementation is correct. No model, sealed fixture, human participant, physical phone, throughput test, memory measurement or official ADTC profiler was involved.

Future local-model responses cannot award themselves source-controlled status. They receive at most the eight deterministic rubric points until an independent human review supplies the two factual-accuracy points. The static baseline remains the minimum comparison: a model must improve understanding or recovery without weakening safety, latency or resource use.

The complete machine-readable run is generated locally at `benchmarks/results/static-development.json` and remains ignored until it is reviewed for publication.
