# Q4 survived Ubuntu without a repair

The corrected Q4 model was rebuilt and tested inside a constrained Ubuntu 22.04 environment before touching the sealed set. The container had four virtual CPUs, 7.8 GiB of visible memory and no network during inference. It used a freshly compiled Linux `llama.cpp` binary from the pinned commit—not the macOS executable.

## What happened

The first command stopped before the model server started because Python could not find the repository's `companion` package. We added the repository root to `PYTHONPATH` and reran the unchanged model, prompts, fixtures and limits. This was an environment repair, not a model retry.

Q4 then completed all eleven development cases.

| Development result | Ubuntu virtual run |
|---|---:|
| Automatic safe passes | 11/11 |
| Model calls | 22 |
| Adaptive repairs | 0 |
| Hard or contract failures | 0 |
| False-stop rate | 0.0 |
| Unnecessary-evidence-request rate | 0.0 |
| Mean generation | 13.17 s/call |
| Mean completion speed | 10.61 tok/s |

The zero-repair result matters because the same Q4 artifact needed one permitted JSON repair on the Mac run. It shows that the format failure did not reproduce in this environment. It does not prove that format failures can never recur.

## Official profiler integration

The official profiler's `--skip-accuracy` path then measured the same model:

| Measurement | Result |
|---|---:|
| Generation throughput | 39.24 tok/s |
| First-token latency | 2,047.33 ms |
| Peak RSS | 744.02 MB |
| Steady-state RSS | 683.71 MB |
| Counted parameters | 596,049,920 |

Accuracy was deliberately skipped, and the virtual machine exposed no thermal sensor. The profiler integration also used Ubuntu's Python 3.10 for this narrow path, while the packaged profiler declares Python 3.11 or newer. These measurements are therefore virtual Ubuntu integration evidence—not the final physical Standard Laptop submission report.

## Decision

Q4 remains the provisional candidate for the physical Ubuntu laptop. Its smaller artifact, stronger local resource measurements, blind prose-review lead and zero-repair Ubuntu development run now point in the same direction. The 24 sealed cases remain unopened.

The reviewed machine-readable summary is in [`benchmarks/ubuntu-q4-virtual-results.json`](../benchmarks/ubuntu-q4-virtual-results.json).

## Publication postscript — 20 August 2026

After this virtual result was frozen, Q4 was selected for the physical-laptop rejection gate and published through a credential-free release. The release reports the same 396,704,576-byte size and SHA-256 as the tested local artifact. The later decision is recorded separately in [`benchmarks/model-selection.json`](../benchmarks/model-selection.json), preserving this result as it was originally reviewed.
