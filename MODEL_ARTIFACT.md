# Selected model artifact

The submission candidate is Qwen3 0.6B, quantized once from Qwen's official BF16 checkpoint to corrected Q4_K_M GGUF. The derivation and tied-embedding correction are recorded in [`benchmarks/quantization-round.json`](benchmarks/quantization-round.json); the later selection is recorded separately in [`benchmarks/model-selection.json`](benchmarks/model-selection.json) so the frozen protocol remains unchanged.

| Field | Value |
|---|---|
| File | `Qwen3-0.6B-Q4_K_M-tied.gguf` |
| Size | 396,704,576 bytes |
| SHA-256 | `297077534a71a538acda7d7a7393081f759774cab48660f6d3e4858bfb58c50e` |
| Parameters reported by profiler | 596,049,920 |
| Runtime | `llama.cpp` |
| License | Apache-2.0 |
| Public release | [Qwen3 0.6B corrected Q4_K_M candidate v1](https://github.com/osasisorae/vowlock-setup-companion-adtc-2026/releases/tag/qwen3-0.6b-q4-k-m-v1) |

`bash download_model.sh` downloads the asset without credentials, verifies the SHA-256 and refuses to overwrite an existing file whose bytes differ. The original model is Qwen3 0.6B by the Qwen team; the source checkpoint and license are available from [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B).

Selection is frozen for the next physical-Ubuntu test. A crash, out-of-memory result, challenge thermal failure or other hard rejection on the target laptop can still reject it before submission.
