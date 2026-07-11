import torch

def configure_torch_runtime() -> None:
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = False

    print(
        "[Torch runtime]",
        f"torch={torch.__version__}",
        f"cuda={torch.version.cuda}",
        f"cudnn={torch.backends.cudnn.version()}",
        f"benchmark={torch.backends.cudnn.benchmark}",
        f"deterministic={torch.backends.cudnn.deterministic}",
        flush=True,
    )