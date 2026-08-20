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

## 15 August 2026 — Q8 requantization rejected in preflight

The official Qwen3 0.6B GGUF repository contains only Q8_0. The pinned `llama-quantize` refused a direct Q8_0-to-Q4_K_M conversion because requantizing already quantized tensors is disabled by default and its override carries a severe quality warning. The 5.7 MB incomplete output was removed and never benchmarked.

Quantization-round protocol 1.1 forbids `--allow-requantize`. Any Q4_K_M candidate must be converted once from Qwen's official BF16 `model.safetensors` at repository commit `c1899de289a04d12100db370d81485cdf75e47ca`, whose published size and linked SHA-256 were recorded before download.

## 15 August 2026 — clean BF16-to-Q4 derivation completed

The verified official BF16 checkpoint was converted to BF16 GGUF and then quantized once to Q4_K_M with the pinned llama.cpp commit. The 1,509,347,200-byte BF16 GGUF and 484,219,776-byte Q4_K_M GGUF are identified by SHA-256 in `benchmarks/quantization-round.json`. Both artifacts remain local and ignored by Git.

The pinned converter dependency requests PyTorch 2.11.0, for which no Intel macOS wheel exists. A separate conversion-only Python 3.11 environment used PyTorch 2.2.2 to read safetensors and write BF16 GGUF. This deviation does not enter inference or quantization: both still use the frozen llama.cpp runtime. It is recorded because reproducibility includes the inconvenient platform boundary, not only the successful command.

## 15 August 2026 — first clean-source Q4 invalidated by a duplicate tied tensor

The official profiler found the first derived Q4 faster but unexpectedly larger in peak RSS than Q8. Its header also exposed 751,632,384 parameters, while the official Q8 exposed 596,049,920. The difference is exactly one 151,936 × 1,024 vocabulary tensor.

The source `config.json` declares tied word embeddings, and the raw `lm_head.weight` and `model.embed_tokens.weight` records are each 311,164,928 bytes with the same SHA-256. The pinned converter nevertheless wrote both to GGUF. This Q4 is invalid for model selection; its successful 11-case result remains useful only as evidence that the explanation harness ran.

Quantization protocol 1.2 registers a narrow repair before creating another artifact. `tools/convert_tied_qwen.py` may omit only `lm_head.weight`, and only after proving the tie declaration, tensor metadata and raw hashes all match. The repaired artifact must repeat development and profiler evaluation from zero.

## 15 August 2026 — corrected Q4 retested from zero

The corrected 396,704,576-byte Q4 reports the same 596,049,920 parameters as the official Q8. It passed all eleven cases under the adaptive gate, using one permitted format repair when `dev_reboot_mismatch` omitted its closing JSON brace. Q8's unchanged replication passed eleven of eleven without repair.

In the paired Intel Mac integration run, the corrected Q4 was 37.96% smaller on disk, 36.34% faster in official-profiler generation, 49.76% lower in first-token latency and 4.57% lower in peak RSS than Q8. The profiler accuracy stage was skipped and no temperature sensor was exposed. These measurements select no challenge winner: human prose review and an Ubuntu target-profile replication remain required, and the sealed set remains unopened.

## 20 August 2026 — blind review and virtual Ubuntu reproduction

An eleven-case blind AI-assisted prose comparison favored corrected Q4: 20/22 factual points and six preference wins, versus Q8's 17/22 and four wins, with one tie. The reviewer had implementation context, so this is comparative technical evidence rather than independent human validation.

The pinned Linux runtime was then compiled inside Ubuntu 22.04 from the verified read-only `llama.cpp` checkout. The first harness launch stopped before model startup because the repository root was absent from Python's import path. Setting `PYTHONPATH=/work` repaired the environment without changing the model, prompts, fixtures or limits.

With networking disabled, corrected Q4 passed all eleven development cases with zero adaptive repairs and zero contract failures. The official profiler's skip-accuracy path measured 39.24 generation tokens/s, 2,047.33 ms first-token latency and 744.02 MB peak RSS. The VM exposed no thermal sensor, accuracy was skipped and the narrow profiler integration used Python 3.10 despite the packaged profiler's Python 3.11 requirement. Q4 therefore advances only as the provisional physical-Ubuntu candidate. The sealed set remains unopened.

## 20 August 2026 — Q4 selected and published before the sealed run

The corrected Q4 artifact was selected from development evidence and published as a credential-free GitHub release. GitHub reports 396,704,576 bytes and SHA-256 `297077534a71a538acda7d7a7393081f759774cab48660f6d3e4858bfb58c50e`, matching the tested local artifact. `download_model.sh` now verifies that hash and refuses to replace a different existing file.

The frozen benchmark plan lists the one-time sealed run before replacement of the guarded download script. We wired the already-selected artifact into the downloader first so the physical Ubuntu laptop can reproduce it. This is an ordering deviation, recorded before opening the sealed set. It changed no model bytes, prompt, response schema, fixture, verifier or resource limit and provided no sealed-set feedback. The sealed set remains unopened and must still run exactly once.

## 20 August 2026 — run-once sealed harness prepared

The original model runner rejected every non-development fixture, so it could not execute the pre-registered sealed stage. The shared experiment function now accepts an explicit required split; the existing development wrapper still fixes that value to `development`. A separate sealed command adds hash verification and a persistent start marker but reuses the same generation, repair, scoring and checkpoint path. The change was tested and committed before any sealed fixture was evaluated.
