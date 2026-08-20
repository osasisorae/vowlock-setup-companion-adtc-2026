#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPECTED_MODEL_SHA256="297077534a71a538acda7d7a7393081f759774cab48660f6d3e4858bfb58c50e"
MODEL_PATH="$ROOT/model/selected-model.gguf"

if [[ ! -r /etc/os-release ]]; then
  echo "Cannot identify this operating system." >&2
  exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" || "${VERSION_ID:-}" != "22.04" ]]; then
  echo "Expected Ubuntu 22.04; found ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "Expected an x86_64 laptop; found $(uname -m)." >&2
  exit 1
fi

memory_kb="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
if [[ -z "$memory_kb" || "$memory_kb" -lt 7500000 ]]; then
  echo "Expected approximately 8 GB RAM; found ${memory_kb:-unknown} kB." >&2
  exit 1
fi

for command_name in git cmake sha256sum llama-bench adtc-profiler; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Selected model is missing. Run: bash download_model.sh" >&2
  exit 1
fi

actual_model_sha256="$(sha256sum "$MODEL_PATH" | awk '{print $1}')"
if [[ "$actual_model_sha256" != "$EXPECTED_MODEL_SHA256" ]]; then
  echo "Selected model checksum does not match the frozen artifact." >&2
  exit 1
fi

echo "Physical Ubuntu preflight passed."
echo "OS: ${PRETTY_NAME}"
echo "Architecture: $(uname -m)"
echo "CPU: $(awk -F: '/model name/ {sub(/^ /, "", $2); print $2; exit}' /proc/cpuinfo)"
echo "Logical CPUs: $(getconf _NPROCESSORS_ONLN)"
echo "Memory: ${memory_kb} kB"
echo "Kernel: $(uname -r)"
echo "Model SHA-256: $actual_model_sha256"
echo "llama-bench: $(command -v llama-bench)"
echo "adtc-profiler: $(command -v adtc-profiler)"
