# Physical Ubuntu 22.04 runbook

This is the next evidence step. Run it on the physical Ubuntu laptop, not on the Mac or inside another virtual machine. The sealed quality result is already final; this run measures the selected artifact's physical performance and does not reopen the holdout.

## 1. Install the free build tools

```bash
sudo apt update
sudo apt install -y build-essential cmake git curl python3-pip lm-sensors
```

No paid service is required. `lm-sensors` gives the official profiler a chance to observe temperature and throttling; hardware that exposes no compatible sensor must be reported as unavailable.

## 2. Clone the public submission and model

```bash
git clone https://github.com/osasisorae/vowlock-setup-companion-adtc-2026.git
cd vowlock-setup-companion-adtc-2026
bash download_model.sh
```

The download is resumable. It is accepted only at 396,704,576 bytes with SHA-256 `297077534a71a538acda7d7a7393081f759774cab48660f6d3e4858bfb58c50e`.

## 3. Build the pinned Linux runtime

```bash
mkdir -p .adtc-tools
git clone https://github.com/ggml-org/llama.cpp .adtc-tools/llama.cpp
git -C .adtc-tools/llama.cpp checkout 9b05354ec6fb58b4e665e9a39ebc40285c015638
cmake -S .adtc-tools/llama.cpp -B .adtc-tools/llama.cpp/build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_CUDA=OFF \
  -DGGML_METAL=OFF \
  -DLLAMA_CURL=OFF
cmake --build .adtc-tools/llama.cpp/build --target llama-bench llama-server -j 4
```

## 4. Install the pinned official profiler in Python 3.11

Ubuntu 22.04's default Python is 3.10, while the profiler requires 3.11 or newer. Use the free `uv` environment rather than replacing the system Python:

```bash
python3 -m pip install --user uv
~/.local/bin/uv python install 3.11
~/.local/bin/uv venv --python 3.11 .adtc-profiler
~/.local/bin/uv pip install --python .adtc-profiler/bin/python \
  "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git@7adbe08f157e9b96a670426339aca2a519706bdc"
export PATH="$PWD/.adtc-tools/llama.cpp/build/bin:$PWD/.adtc-profiler/bin:$PATH"
```

Before the final report, replace the two remaining `PENDING_*` registration values in `metadata.json` with the real ADTF team ID and registered email.

## 5. Verify the machine without changing it

```bash
bash tools/ubuntu/physical-preflight.sh | tee physical-preflight.txt
```

Stop if this does not say `Physical Ubuntu preflight passed.` Do not relabel a different OS, architecture or memory profile as the target laptop.

## 6. Smoke test, then run full accuracy

```bash
adtc-profiler run \
  --submission "$PWD" \
  --mode participant \
  --skip-accuracy \
  --output submission-smoke.json

adtc-profiler run \
  --submission "$PWD" \
  --mode participant \
  --output submission.json
```

The full run may download the public accuracy dataset on first use; model inference remains local. Keep both JSON files and the terminal log. Do not estimate a missing thermal, accuracy or memory value.

## 7. Bring the evidence back

Copy these files to the Mac without editing them:

- `physical-preflight.txt`
- `submission-smoke.json`
- `submission.json`

We will hash the originals, create a reviewed public summary, add screenshot 12, and compare the physical result with the virtual Ubuntu result. A physical success will add performance evidence; it will not erase the recorded 23/24 sealed quality result.
