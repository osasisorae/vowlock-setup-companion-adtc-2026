#!/usr/bin/env bash
set -euo pipefail

MODEL_URL="https://github.com/osasisorae/vowlock-setup-companion-adtc-2026/releases/download/qwen3-0.6b-q4-k-m-v1/Qwen3-0.6B-Q4_K_M-tied.gguf"
EXPECTED_SHA256="297077534a71a538acda7d7a7393081f759774cab48660f6d3e4858bfb58c50e"
EXPECTED_BYTES=396704576
MODEL_DIR="${MODEL_DIR:-model}"
MODEL_PATH="${MODEL_PATH:-${MODEL_DIR}/selected-model.gguf}"

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "A SHA-256 tool (sha256sum or shasum) is required." >&2
    return 1
  fi
}

file_size() {
  if stat -c %s "$1" >/dev/null 2>&1; then
    stat -c %s "$1"
  else
    stat -f %z "$1"
  fi
}

mkdir -p "$MODEL_DIR"

if [[ -e "$MODEL_PATH" ]]; then
  existing_sha256="$(hash_file "$MODEL_PATH")"
  if [[ "$existing_sha256" == "$EXPECTED_SHA256" ]]; then
    echo "Model already present and verified: $MODEL_PATH"
    exit 0
  fi

  echo "Refusing to replace an existing model with the wrong checksum: $MODEL_PATH" >&2
  echo "Expected: $EXPECTED_SHA256" >&2
  echo "Found:    $existing_sha256" >&2
  exit 1
fi

partial_path="${MODEL_PATH}.partial"

if [[ -e "$partial_path" ]]; then
  echo "Resuming the selected Qwen3 0.6B Q4_K_M download..."
else
  echo "Downloading the selected Qwen3 0.6B Q4_K_M artifact..."
fi
curl \
  --fail \
  --location \
  --retry 5 \
  --retry-all-errors \
  --retry-delay 2 \
  --continue-at - \
  --output "$partial_path" \
  "$MODEL_URL"

downloaded_bytes="$(file_size "$partial_path")"
if [[ "$downloaded_bytes" != "$EXPECTED_BYTES" ]]; then
  echo "Download ended at an unexpected size; partial file was preserved for resume." >&2
  echo "Expected: $EXPECTED_BYTES bytes" >&2
  echo "Found:    $downloaded_bytes bytes" >&2
  exit 1
fi

downloaded_sha256="$(hash_file "$partial_path")"
if [[ "$downloaded_sha256" != "$EXPECTED_SHA256" ]]; then
  echo "Downloaded model failed SHA-256 verification." >&2
  echo "Expected: $EXPECTED_SHA256" >&2
  echo "Found:    $downloaded_sha256" >&2
  exit 1
fi

mv "$partial_path" "$MODEL_PATH"
echo "Model downloaded and verified: $MODEL_PATH"
