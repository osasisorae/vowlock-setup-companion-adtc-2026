# VowLock Setup Companion

An offline, safety-bounded explanation layer for difficult Android provisioning workflows. This repository is the new experimental proof of concept intended for the Africa Deep Tech Challenge 2026. VowLock is an existing experimental alpha used only as the first integration case study and source workflow; VowLock itself is not the submitted product.

## Current status

**Phase 2D: local quantization comparison complete; human review and target Ubuntu reproduction pending. Not submission-ready and not connected to a device.**

The repository was created from the [official ADTC 2026 submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template). Model selection, team registration details, final measured benchmarks and the public download script remain pending. `download_model.sh` fails closed until a candidate wins the pre-registered benchmark.

Public candidate weights are downloaded only to the ignored local `model/` directory and hash-verified before use; none is committed or selected yet. Corrected Q4 currently leads the local resource comparison, but it needed one permitted format repair and has not passed human prose review or the target Ubuntu profile. No phone, ADB session, APK, security control, VowLock key or commitment activation is used in this phase.

## Research question

Can a small offline language model improve a novice's understanding and recovery during a consequential technical setup compared with well-written static instructions, while a deterministic state machine retains exclusive authority over every system operation?

## Safety architecture

```text
Synthetic scenario fixture
          |
          v
Deterministic state machine ----> append-only evidence events
          |
          v
Sanitized state summary
          |
          v
Local GGUF explanation layer
          |
          v
Human-readable guidance only
```

The model may explain a known state, classify a known failure, request missing non-sensitive evidence or stop. It may not compose or execute shell/ADB commands, select or operate a device, change security controls, install software, assign Device Owner, erase/reboot a device or activate a commitment. Deterministic code owns all state transitions and stop conditions.

## Phase 1 artifacts

- [Research boundary](docs/research-boundary.md)
- [Experiment design](docs/experiment-design.md)
- [Model shortlist](docs/model-shortlist.md)
- [Benchmark plan](docs/benchmark-plan.md)
- [Static baseline result](docs/static-baseline-results.md)
- [Development change log](docs/development-change-log.md)
- [Development candidate results](docs/development-candidate-results.md)
- [Quantization round results](docs/quantization-round-results.md)
- [Machine-readable quantization results](benchmarks/quantization-results.json)
- [Machine-readable frozen protocol](experiment-protocol.json)
- [Frozen prompt hashes](prompts/MANIFEST.json)
- [Opaque sealed-set hashes](fixtures/sealed-manifest.json)
- [Technical report draft](REPORT.md)

## Synthetic evaluator foundation

The repository now includes an executable, standard-library-only deterministic core and the first fact-equivalent explanation baseline:

```text
companion/evaluator.py       decision policy and CLI
companion/experiment.py      static guidance, sanitized inputs, scorer and batch runner
schemas/                     scenario, decision and evidence-event contracts
fixtures/development/        invented development cases only
tests/                       contract, decision-boundary and baseline tests
```

Run the regression suite and compare every development result with its independent fixture label:

```bash
python3 -m unittest discover -s tests -v
python3 -m companion.evaluator fixtures/development --check-label
python3 -m companion.experiment fixtures/development \
  --variant static \
  --output benchmarks/results/static-development.json
```

The evaluator ignores `expected_outcome` when deciding. It uses labels only after evaluation to measure agreement. The static renderer receives the same sanitized fact packet planned for later variants, and its output contract contains no command, device identifier or execution field. The scorer checks action preservation, evidence requests, required risks and schema compliance. Only source-controlled static prose receives automatic factual-accuracy points; model prose requires independent human review. The sealed set is intentionally excluded from Git and must not guide development revisions.

## Challenge constraints carried forward

- Ubuntu 22.04 target on the published Standard Laptop: Intel Core i5 10th–12th gen or AMD Ryzen 5 3000–5000, 8 GB DDR4 RAM and integrated graphics only.
- GGUF weights through `llama.cpp`; inference must be fully offline.
- Public, credential-free, idempotent weight download before evaluation.
- Exactly two declared domain prompts, with hidden prompts added by organizers.
- Model quality is 50% of judging, throughput 30% and efficiency 20%; crashes or out-of-memory runs disqualify a submission.

Official sources: [challenge](https://adtc-2026.devpost.com/), [rules](https://adtc-2026.devpost.com/rules), [template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template), and [profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler).

## Submission readiness checklist

- [ ] Confirm final eligibility and obtain the ADTF team ID.
- [ ] Select the model using the frozen benchmark plan.
- [ ] Replace every `PENDING_*` value in `metadata.json`.
- [x] Freeze exactly two final test prompts.
- [ ] Implement and test the credential-free, idempotent model download.
- [ ] Run the official profiler on the target Ubuntu profile.
- [x] Run a paired official-profiler integration comparison without claiming target performance.
- [ ] Publish measured results without extrapolation or invented values.
- [ ] Keep model weights, secrets, customer data and signed APKs out of Git.
- [ ] Make the repository public before evaluation.

## License

GPL-3.0, inherited from the official template. See [LICENSE](LICENSE).
