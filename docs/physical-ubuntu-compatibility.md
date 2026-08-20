# The old laptop completed the experiment—and failed the target check

On 20 August 2026, the public repository was cloned onto a physical Ubuntu laptop from scratch. The selected 396,704,576-byte model downloaded without credentials, resumed safely, matched its frozen SHA-256 and ran through the pinned `llama.cpp` and official ADTC profiler toolchain. Both returned JSON files pass the official profiler schema.

That is meaningful compatibility and distribution evidence. It is not the final challenge-machine result.

## What completed

| Check | Result |
|---|---|
| Operating system | Ubuntu 22.04.5 LTS |
| Architecture | x86_64 |
| Visible memory | 7.6 GB in the profiler report |
| Public model download | Completed and SHA-256 verified |
| Runtime | Pinned `llama.cpp` commit `9b05354ec6fb58b4e665e9a39ebc40285c015638` |
| Profiler | Official commit `7adbe08f157e9b96a670426339aca2a519706bdc` |
| Smoke report | Completed; schema-valid |
| Full report | Completed; schema-valid |
| Accuracy path | 50 ARC-Easy samples; 0.54 normalized accuracy |

## What the full run measured

| Metric | Physical compatibility run | Virtual Ubuntu integration |
|---|---:|---:|
| Generation | 23.19 tok/s | 39.24 tok/s |
| First-token latency | 7,298.69 ms | 2,047.33 ms |
| Peak RSS | 746.43 MB | 744.02 MB |
| Steady-state RSS | 699.10 MB | 683.71 MB |
| Peak temperature | 86°C | unavailable |
| Throttling | yes | unavailable |

The columns are not a controlled performance comparison. One is a physical 7th-generation Intel laptop and the other is a virtual machine on an Intel Mac. Their value is diagnostic: the model stayed well within memory, while the older physical CPU was slower, crossed the challenge's 85°C threshold and throttled.

## The important failure was our preflight

The laptop uses an Intel Core i5-7Y57. ADTC's published Standard Laptop range is Intel Core i5 10th–12th generation or AMD Ryzen 5 3000–5000. The first preflight script checked Ubuntu, x86_64 and memory but printed “passed” without enforcing the CPU range. That sentence was wrong.

The preflight now rejects processors outside the published CPU families. The original text file remains unchanged and its incorrect pass is documented rather than erased.

## What remains

This run proves that a new user can obtain the public repository and model, build the pinned runtime and complete both profiler paths on a real Ubuntu machine. It does not prove target-hardware throughput or thermal compliance. The final profiler run still needs:

1. a conforming ADTC Standard Laptop;
2. a peak temperature at or below 85°C with no throttling flag; and
3. the real ADTF team ID and registered email in place of the two `PENDING_*` values.

The reviewed measurements and hashes are recorded in [`benchmarks/physical-ubuntu-compatibility.json`](../benchmarks/physical-ubuntu-compatibility.json). The three unedited originals remain ignored locally.
