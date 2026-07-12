#!/usr/bin/env bash
set -euo pipefail

ORT_SO=$(
  find ".venv/lib" \
    -path '*/site-packages/onnxruntime/capi/onnxruntime_pybind11_state*.so' \
    -print \
    -quit
)

if [[ -z "${ORT_SO}" ]]; then
    echo "onnxruntime shared library was not found." >&2
    exit 1
fi

if ! command -v patchelf >/dev/null 2>&1; then
    echo "patchelf is required: sudo apt install patchelf" >&2
    exit 1
fi

echo "Clearing executable-stack flag: ${ORT_SO}"
patchelf --clear-execstack "${ORT_SO}"

uv run --frozen python -c \
    'import onnxruntime as ort; print("onnxruntime:", ort.__version__)'