# Model shortlist

**Status:** all four candidates downloaded locally and SHA-256 verified; none selected. Weights remain ignored by Git.

All candidates below have developer/maintainer-hosted GGUF repositories that are publicly readable without an account and are compatible with `llama.cpp`. The benchmark, not reputation or parameter count, decides the winner.

| Candidate | Candidate file | Approx. file size | License/access | Why test it |
|---|---|---:|---|---|
| [Qwen3 0.6B](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF) | `Qwen3-0.6B-Q8_0.gguf` | 639,446,688 bytes | Apache-2.0; public | Smallest/faster control; tests whether constrained state explanation needs a larger model at all. |
| [Qwen2.5 1.5B Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | `qwen2.5-1.5b-instruct-q4_k_m.gguf` | 1,117,320,736 bytes | Apache-2.0; public | Official GGUF offers multiple quantizations and the model card emphasizes structured/JSON output. |
| [Qwen3 1.7B](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF) | `Qwen3-1.7B-Q8_0.gguf` | 1,834,426,016 bytes | Apache-2.0; public | Larger quality candidate with an official GGUF; benchmark non-thinking mode for latency and output control. |
| [SmolLM2 1.7B Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF) | `smollm2-1.7b-instruct-q4_k_m.gguf` | 1,055,609,536 bytes | Apache-2.0; public | Independent compact-model family and a useful check against selecting only Qwen variants. |

Credential-free downloads completed on 15 August 2026 for all four artifacts. The exact downloaded sizes and SHA-256 values match their linked repository objects. They total 4,646,802,976 bytes (about 4.33 GiB). Parameter count and artifact size are not interchangeable, and runtime RAM will be higher than the GGUF file because `llama.cpp` also allocates working memory and a context/KV cache. Exact repository revisions, linked object hashes and URLs are frozen in `benchmarks/candidates.json`.

## Deliberate exclusion

[Gemma 3 1B QAT GGUF](https://huggingface.co/google/gemma-3-1b-it-qat-q4_0-gguf) is technically attractive but currently requires accepting Google's usage licence while signed in to Hugging Face. The challenge download script must work without credentials, so it is excluded unless a clearly compliant credential-free official source is confirmed.

Llama 3.2 1B is not in the first round because the official base repository uses a custom community licence and does not itself provide the simple official public GGUF artifact offered by the candidates above. It can be reconsidered only if the first round fails.

## Selection rule

Reject a candidate immediately if it exceeds memory/thermal limits, produces any terminal safety failure, cannot follow the response contract or cannot be downloaded through a stable credential-free URL. Among survivors, select on the challenge-weighted quality/throughput/efficiency evidence plus the pre-registered safety and usability gates—not average prose preference.
