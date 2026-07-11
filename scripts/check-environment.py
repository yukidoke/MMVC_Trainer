#!/usr/bin/env python3

import platform
import torch

print("Python:", platform.python_version())
print("Torch:", torch.__version__)
print("Torch CUDA:", torch.version.cuda)
print("cuDNN:", torch.backends.cudnn.version())
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))