#!/usr/bin/env bash
set -euo pipefail

readonly WSL_CUDA_LIB="/usr/lib/wsl/lib"

if [[ ! -e "${WSL_CUDA_LIB}/libcuda.so.1" ]]; then
    echo "Error: ${WSL_CUDA_LIB}/libcuda.so.1 が見つかりません。" >&2
    echo "WSLのNVIDIA GPU連携を確認してください。" >&2
    exit 1
fi

export LD_LIBRARY_PATH="${WSL_CUDA_LIB}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

exec uv run --frozen "$@"