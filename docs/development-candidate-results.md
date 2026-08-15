# Development candidate results

**Status:** first-round and local quantization evidence complete; corrected Q4 leads provisionally, but no model is selected yet.

These runs use the pinned CPU-only `llama.cpp` build on an Intel macOS development machine. They cannot substitute for the published ADTC Ubuntu Standard Laptop or the official profiler. The 24 sealed synthetic cases remain unevaluated.

Every bounded response used the same 2,048-token context, four threads, temperature zero, seed 329, 256-token attempt limit and 45-second attempt limit. A per-case JSON schema bound the deterministic decision, transition, evidence and risk fields; models generated only the three human-facing prose fields.

| Candidate | Artifact | Automatic safe passes | Repairs | Mean generation | Mean completion speed | Automatic gate |
|---|---:|---:|---:|---:|---:|---|
| Qwen3 0.6B Q8_0 | 639,446,688 B | 11/11 | 0 | 7.05 s/call | 24.40 tok/s | Pass |
| Qwen2.5 1.5B Q4_K_M | 1,117,320,736 B | 6/11 | 5 | 17.34 s/call | 14.44 tok/s | Fail |
| Qwen3 1.7B Q8_0 | 1,834,426,016 B | 5/11 | 3 | 28.53 s/call | 9.13 tok/s | Fail |
| SmolLM2 1.7B Q4_K_M | 1,055,609,536 B | 4/11 | 3 | 30.78 s/call | 7.77 tok/s | Fail |

The two larger Qwen candidates did not fail because their prose sounded unintelligent. Qwen2.5 produced five bounded responses that reached 256 tokens without completing a valid object; the single allowed repairs also reached 256. Qwen3 1.7B produced three such truncations and, late in the sustained local run, three calls that completed after the 45-second gate. Thermal state was not independently measured on this Mac, so the slowdown is not attributed to heat. The truncations independently fail the response-contract gate.

SmolLM2 completed only four adaptive cases without a hard failure. Its failures included truncation, per-attempt time excess and one adaptive pair exceeding 90 seconds. One ordinary response repeated the same uncertainty sentence until the attempt exceeded its limit. On one terminal-known-failure case its repair converted invalid JSON into a valid bounded response, proving that adaptive revision can work; the overall candidate still failed seven of eleven adaptive cases.

Qwen3 0.6B passed the automatic safety envelope, but that does not award the two factual-explanation points. Human review found a contradiction in its ordinary installation-rejection answer, an overstatement about the current state in one bounded answer, and other phrases requiring review. A schema can reserve authority; it cannot prove free-form prose accurate or useful.

The first round therefore rejects three candidates and advances Qwen3 0.6B only as a provisional survivor. An unchanged Q8 replication later passed eleven of eleven with no repair. A clean-source Q4 comparison also passed the adaptive eleven-of-eleven gate, using one permitted format repair.

The first clean-source Q4 was invalidated because its converter wrote both byte-identical tied vocabulary tensors. The official profiler exposed the error through a 751,632,384 parameter count and unexpectedly higher memory. A registered guard then omitted the duplicate only after proving the tie declaration and matching raw hashes. The corrected Q4 reports the same 596,049,920 parameters as Q8, is 37.96% smaller on disk and led the paired Intel Mac integration run on generation throughput, first-token latency and memory.

That is not final selection. The profiler accuracy stage was skipped, the Mac had no temperature sensor and Q4 required one format repair. Blinded human review and the published Ubuntu target profile remain mandatory. Detailed paired values are in [quantization-round-results.md](quantization-round-results.md). No result here authorizes opening the sealed set.

## What the development loop corrected

1. Scorer 0.1.0 falsely treated Markdown fences as invented commands and could label a correct expected continuation as false. The run was invalidated and regression tests added.
2. The first structured implementation used a general JSON schema, accidentally allowing the model to choose authority-bearing fields. That run was invalidated.
3. The current bounded schema binds those fields to deterministic constants. The model cannot authorize a transition through its response.
4. A Qwen3 1.7B repair exceeded the transport timeout and exposed that partial results were not persisted. The runner now checkpoints after every case and retains a completed over-budget output with `GENERATION_TIMEOUT` rather than losing the run. The 45-second gate did not change.

This progression is development-set work, where revision is permitted. Every candidate comparison used for selection must run again under the final harness. No sealed result may trigger another correction.
