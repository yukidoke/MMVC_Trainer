#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y \
    build-essential \
    curl \
    pkg-config \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    espeak-ng \
    git-lfs

git lfs install