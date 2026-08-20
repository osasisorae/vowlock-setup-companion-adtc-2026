# Quantization round: a faster file exposed a duplicated tensor

This is a development result, not an ADTC target-machine claim. The 24 sealed cases remain unopened.

## What happened

The first Q4 artifact looked faster but used more memory than Q8. The official profiler also counted 751,632,384 parameters instead of the official Q8 artifact's 596,049,920. The difference was exactly one vocabulary tensor.

Qwen's source config declares tied word embeddings. Its `lm_head.weight` and `model.embed_tokens.weight` records are each 311,164,928 bytes and have the same raw SHA-256. The pinned converter wrote both copies. That artifact is invalid for selection.

Protocol 1.2 registered a narrow correction before another artifact was made. `tools/convert_tied_qwen.py` removes the duplicate LM head only after proving the tie declaration, matching metadata and matching raw hashes. The corrected Q4 contains the same 596,049,920 counted parameters as the official Q8.

## Paired local integration result

| Measurement | Q8 replication | Corrected Q4 | Q4 difference |
|---|---:|---:|---:|
| Artifact | 639,446,688 B | 396,704,576 B | 37.96% smaller |
| Development adaptive gate | 11/11 | 11/11 | tied |
| Format repairs | 0 | 1 | Q8 more reliable here |
| Harness mean generation | 23.61 tok/s | 32.57 tok/s | 37.96% faster |
| Official-profiler generation | 35.86 tok/s | 48.89 tok/s | 36.34% faster |
| First-token latency | 3,580.79 ms | 1,798.80 ms | 49.76% lower |
| Peak RSS | 793.16 MB | 756.92 MB | 4.57% lower |
| Steady-state RSS | 732.13 MB | 677.04 MB | 7.52% lower |
| Counted parameters | 596,049,920 | 596,049,920 | matched |

The profiler accuracy stage was intentionally skipped for this integration comparison, and this Intel Mac exposed no temperature sensor. These numbers cannot be presented as Ubuntu challenge-profile performance.

## What the automatic gate could not decide

The corrected Q4 needed one permitted format repair after omitting a closing JSON brace on `dev_reboot_mismatch`. The repair did not change the deterministic STOP decision. Q8 needed no repair.

Both quantizations produced prose that deserved direct review. A constant-bound JSON schema can preserve authority, but it cannot prove that phrases such as “requires immediate action” are clear, supported or useful to a novice.

An eleven-case blind AI-assisted comparison was frozen before its A/B key was opened. Corrected Q4 received 20/22 factual points, six preference wins and two factual flags. Q8 received 17/22 factual points, four wins and five factual flags; one case tied. Q4 therefore leads on both local resources and this prose comparison.

This review is not presented as independent human evidence: the Codex reviewer knew the implementation and had previously seen one Q4 response while checking the review tool. Q4 advances as the provisional Ubuntu candidate. Target Ubuntu inference and an independent human spot-check remain before final selection. See [ai-assisted-blind-review.md](ai-assisted-blind-review.md).
