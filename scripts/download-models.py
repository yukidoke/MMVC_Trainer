#!/usr/bin/env python3

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REVISION = "461beb60266192267204119f183b6680b0f0b7ec"
BASE_URL = (
    "https://huggingface.co/MMVC/prelearned-model/"
    f"resolve/{REVISION}"
)

MODELS = [
    {
        "filename": "G_v13_20231020.pth",
        "size": 563_540_775,
        "sha256": (
            "91d269df03e27ebdff0e1dee2d2bfc26"
            "ffd3492f05a789207d8c37c50757179d"
        ),
    },
    {
        "filename": "D_v13_20231020.pth",
        "size": 561_093_195,
        "sha256": (
            "1c9499b3ac05f5d3f6649f418d1aff10"
            "c725628cdf8a6261205e47ec32ef76fd"
        ),
    },
]

CHUNK_SIZE = 4 * 1024 * 1024
MAX_RETRIES = 3


def format_bytes(size: int) -> str:
    value = float(size)

    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024

    return f"{size} B"


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def verify_model(
    path: Path,
    model: Dict[str, Any],
    *,
    quiet: bool = False,
) -> bool:
    filename = model["filename"]
    expected_size = model["size"]
    expected_sha256 = model["sha256"]

    if not path.is_file():
        if not quiet:
            print(f"[missing] {filename}")
        return False

    actual_size = path.stat().st_size

    if actual_size != expected_size:
        if not quiet:
            print(
                f"[invalid] {filename}: size mismatch\n"
                f"  expected: {expected_size}\n"
                f"  actual:   {actual_size}"
            )
        return False

    if not quiet:
        print(f"[verify] {filename}: calculating SHA-256...")

    actual_sha256 = calculate_sha256(path)

    if actual_sha256 != expected_sha256:
        if not quiet:
            print(
                f"[invalid] {filename}: SHA-256 mismatch\n"
                f"  expected: {expected_sha256}\n"
                f"  actual:   {actual_sha256}"
            )
        return False

    if not quiet:
        print(f"[ok] {filename}")

    return True


def download_model(
    destination: Path,
    model: Dict[str, Any],
) -> None:
    filename = model["filename"]
    expected_size = model["size"]
    expected_sha256 = model["sha256"]

    url = f"{BASE_URL}/{filename}?download=true"
    temporary_path = destination.with_name(destination.name + ".part")

    for attempt in range(1, MAX_RETRIES + 1):
        if temporary_path.exists():
            temporary_path.unlink()

        digest = hashlib.sha256()
        downloaded = 0

        request = Request(
            url,
            headers={
                "User-Agent": "MMVC-v1.3-model-downloader/1.0",
            },
        )

        try:
            print(
                f"[download] {filename} "
                f"({format_bytes(expected_size)})"
            )

            with urlopen(request, timeout=60) as response:
                with temporary_path.open("wb") as output:
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break

                        output.write(chunk)
                        digest.update(chunk)
                        downloaded += len(chunk)

                        percentage = downloaded * 100 / expected_size
                        print(
                            "\r"
                            f"  {format_bytes(downloaded)} / "
                            f"{format_bytes(expected_size)} "
                            f"({percentage:5.1f}%)",
                            end="",
                            flush=True,
                        )

            print()

            if downloaded != expected_size:
                raise RuntimeError(
                    f"size mismatch: expected {expected_size}, "
                    f"got {downloaded}"
                )

            actual_sha256 = digest.hexdigest()

            if actual_sha256 != expected_sha256:
                raise RuntimeError(
                    "SHA-256 mismatch:\n"
                    f"  expected: {expected_sha256}\n"
                    f"  actual:   {actual_sha256}"
                )

            # 検証が完了してから本来のファイル名へ置き換える。
            os.replace(str(temporary_path), str(destination))
            print(f"[saved] {destination}")
            return

        except (HTTPError, URLError, OSError, RuntimeError) as error:
            if temporary_path.exists():
                temporary_path.unlink()

            print(
                f"[error] {filename}: {error}",
                file=sys.stderr,
            )

            if attempt >= MAX_RETRIES:
                raise

            wait_seconds = attempt * 2
            print(
                f"[retry] {wait_seconds}秒後に再試行します "
                f"({attempt}/{MAX_RETRIES})"
            )
            time.sleep(wait_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MMVC v1.3の事前学習済みモデルを取得します。",
    )

    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("fine_model"),
        help="保存先ディレクトリ。既定値: fine_model",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="ダウンロードせず、既存ファイルのみ検証します。",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="正常なファイルが存在していても再ダウンロードします。",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    directory = args.directory.resolve()

    if not args.check:
        directory.mkdir(parents=True, exist_ok=True)

    all_valid = True

    for model in MODELS:
        destination = directory / model["filename"]

        if args.check:
            if not verify_model(destination, model):
                all_valid = False
            continue

        if not args.force and verify_model(
            destination,
            model,
            quiet=True,
        ):
            print(f"[skip] {model['filename']} is already valid")
            continue

        download_model(destination, model)

    if args.check and not all_valid:
        print("[failed] モデルが不足しているか破損しています。")
        return 1

    print("[complete] すべてのモデルを確認しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())