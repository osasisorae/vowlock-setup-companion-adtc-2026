# Profiler-first benchmark plan

The source-controlled static development baseline has run. No model benchmark has run yet. This document freezes the comparison before model weights or UI work begin.

## Environment

Primary decision environment: the published ADTC Standard Laptop profile—Ubuntu 22.04 on an Intel Core i5 10th–12th gen or AMD Ryzen 5 3000–5000, 8 GB DDR4 RAM and integrated graphics only. Record OS/kernel, CPU, RAM, `llama.cpp` commit, profiler commit, model URL, SHA-256, quantization, context size, thread count, temperature, seed and generation limits for every run.

A macOS development run may catch integration errors but must be labelled separately and cannot substitute for the challenge-profile result.

## Fixed sequence

1. Pin the official profiler and `llama.cpp` revisions.
2. Freeze development fixtures, sealed fixtures, prompts, response schema, rubric, hard failures and resource ceilings.
3. Verify every candidate URL is public and record its hash after download.
4. Run a minimal smoke test; reject invalid GGUF/runtime combinations.
5. Run the official profiler using the same settings for each candidate.
6. Evaluate all four explanation variants on the development set.
7. Select/freeze a model and prompt only from development results.
8. Run the sealed set once and preserve every attempt and failure.
9. Replace the guarded `download_model.sh` and pending metadata only after selection.

The explanation response schema, static renderer, deterministic portion of the scorer, prompts and resource ceilings are frozen as contract version `1.0`. The seed-private sealed fixture set is generated and hash-registered but must not be evaluated until model and prompt selection are frozen. Model downloads can begin only after the seal and prompt manifests pass their integrity checks.

The first development run is recorded in [the static baseline result](static-baseline-results.md). Its perfect contract score is an implementation check, not a claim of novice usefulness.

## Measurements

- peak RAM and model load time;
- time to first token, tokens/second and total response latency;
- generated tokens and adaptive attempt count;
- thermal maximum and throttling flag;
- correct safe-next-action score and total rubric score;
- command hallucination and terminal-failure count;
- false-stop and unnecessary-evidence-request rates;
- necessary-stop and necessary-evidence-request recall;
- novice next-step errors versus fact-equivalent static instructions.

## Hard rejection

Reject on out-of-memory/crash, temperature above the challenge limit or throttling penalty condition, credentialed download, online inference dependency, invalid response contract, any terminal failure or any false continuation on a consequential case.

## Reproducibility record

Store machine-readable outputs under `benchmarks/results/` locally; this directory is ignored until results have been reviewed and redacted. Publish a reviewed summary plus hashes and exact commands. Never publish private VowLock data, device identifiers, customer data, keys, signed APKs or a sealed test set used for final evaluation.

## Commands after model selection

Do not run these during Phase 1. After the winner is wired into `metadata.json` and `download_model.sh`:

```bash
bash download_model.sh

adtc-profiler run \
  --submission . \
  --mode participant \
  --output submission.json \
  --skip-accuracy
```

The official profiler output and custom safety evaluation must both be retained; neither replaces the other.
