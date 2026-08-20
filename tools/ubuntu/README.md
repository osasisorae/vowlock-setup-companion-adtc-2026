# Ubuntu 22.04 reproduction image

This image supplies only the compiler and Python environment needed to build the pinned `llama.cpp` source and run the repository's development evaluator inside Ubuntu 22.04.

The host source checkout is mounted read-only. Linux binaries are written to a Docker volume, so the macOS build is never reused or modified. The container is limited to four CPUs and approximately 7.5 GiB of memory when benchmark commands run.

This is a virtual compatibility and inference reproduction. It is not presented as physical ADTC Standard Laptop throughput, thermal or power evidence.

`Dockerfile.profiler` adds only the dependencies needed for the official profiler's `--skip-accuracy` integration path. The official profiler source remains pinned separately in `benchmarks/tooling-lock.json`. This image uses Ubuntu's Python 3.10 to exercise that path even though the packaged profiler declares Python 3.11; the final physical-laptop profiler run must use a supported Python version and include accuracy.

For the real laptop, follow [`docs/physical-ubuntu-runbook.md`](../../docs/physical-ubuntu-runbook.md). `physical-preflight.sh` is read-only: it refuses the wrong OS, architecture, memory profile, tools or model checksum before profiling begins.
