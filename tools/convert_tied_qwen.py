#!/usr/bin/env python3
"""Convert a tied Qwen checkpoint without writing its duplicate LM head.

The official Qwen3 0.6B BF16 checkpoint currently contains both
``lm_head.weight`` and ``model.embed_tokens.weight`` even though its config
declares ``tie_word_embeddings: true``. The tensors are identical. The pinned
llama.cpp converter writes both, while the official Q8 GGUF stores the tied
table once.

This guard refuses to alter anything unless the declaration, tensor metadata
and raw tensor hashes all agree. It then filters only ``lm_head.weight`` and
runs the otherwise unchanged converter from the supplied llama.cpp checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


TIED_TENSORS = ("lm_head.weight", "model.embed_tokens.weight")


def tensor_record(model_file: Path, tensor_name: str) -> dict[str, object]:
    """Return safetensors metadata and a streaming SHA-256 for one tensor."""
    with model_file.open("rb") as handle:
        header_length = struct.unpack("<Q", handle.read(8))[0]
        header = json.loads(handle.read(header_length))
        info = header[tensor_name]
        start, end = info["data_offsets"]
        handle.seek(8 + header_length + start)
        digest = hashlib.sha256()
        remaining = end - start
        while remaining:
            block = handle.read(min(remaining, 8 * 1024 * 1024))
            if not block:
                raise ValueError(f"unexpected EOF while hashing {tensor_name}")
            digest.update(block)
            remaining -= len(block)
    return {
        "dtype": info["dtype"],
        "shape": info["shape"],
        "bytes": end - start,
        "sha256": digest.hexdigest(),
    }


def verify_tied_checkpoint(model_dir: Path) -> dict[str, dict[str, object]]:
    config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
    if config.get("tie_word_embeddings") is not True:
        raise ValueError("refusing repair: config does not declare tied embeddings")

    model_file = model_dir / "model.safetensors"
    records = {name: tensor_record(model_file, name) for name in TIED_TENSORS}
    left, right = (records[name] for name in TIED_TENSORS)
    for field in ("dtype", "shape", "bytes", "sha256"):
        if left[field] != right[field]:
            raise ValueError(f"refusing repair: tied tensor {field} values differ")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llama-cpp-root", required=True, type=Path)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--outfile", required=True, type=Path)
    args = parser.parse_args()

    records = verify_tied_checkpoint(args.model_dir)
    print(json.dumps({"tied_tensor_proof": records}, indent=2, sort_keys=True))

    sys.path.insert(0, str(args.llama_cpp_root / "gguf-py"))
    sys.path.insert(0, str(args.llama_cpp_root))
    from conversion.qwen import Qwen3Model

    original_filter = Qwen3Model.filter_tensors

    def filter_duplicate_lm_head(cls, item):
        if item[0] == "lm_head.weight":
            return None
        return original_filter(item)

    Qwen3Model.filter_tensors = classmethod(filter_duplicate_lm_head)

    import convert_hf_to_gguf

    sys.argv = [
        "convert_hf_to_gguf.py",
        str(args.model_dir),
        "--outfile",
        str(args.outfile),
        "--outtype",
        "bf16",
    ]
    convert_hf_to_gguf.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
