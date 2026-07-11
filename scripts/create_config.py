#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    required_sections = ("dataset", "normalize", "training")

    for section in required_sections:
        if section not in config:
            raise ValueError(f"設定セクションがありません: {section}")

    return config


def run_command(command: list, *, cwd: Path) -> None:
    print("+", " ".join(str(value) for value in command))

    subprocess.run(
        [str(value) for value in command],
        cwd=cwd,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MMVCのデータセットと学習設定を生成します。",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=REPOSITORY_ROOT / "config/default.json",
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = load_config(config_path)

    dataset = config["dataset"]
    normalize = config["normalize"]

    print(f"Config: {config_path}")
    print(f"Repository: {REPOSITORY_ROOT}")

    if normalize["enabled"]:
        run_command(
            [
                sys.executable,
                "normalize.py",
                str(normalize["backup"]),
            ],
            cwd=REPOSITORY_ROOT,
        )

    command = [
        sys.executable,
        "create_dataset.py",
        "-f",
        dataset["config_name"],
        "-s",
        str(dataset["sample_rate"]),
    ]

    if dataset["multi_speakers"]:
        command.extend(
            [
                "-m",
                dataset["multi_speaker_correspondence"],
            ]
        )
    else:
        command.extend(
            [
                "-t",
                str(dataset["character_select"]),
            ]
        )

    run_command(command, cwd=REPOSITORY_ROOT)

    print("\nGenerated files:")

    for directory_name in ("filelists", "configs"):
        directory = REPOSITORY_ROOT / directory_name
        print(f"\n[{directory_name}]")

        for path in sorted(directory.iterdir()):
            print(path.relative_to(REPOSITORY_ROOT))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)