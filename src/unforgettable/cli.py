import argparse
from collections.abc import Sequence

from unforgettable import unforgettable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unforgettable",
        description="Inspect and maintain an Unforgettable cache.",
    )
    parser.add_argument(
        "--cache-folder",
        help="Folder containing the cache files to operate on.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available cache IDs.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cache = unforgettable(cache_folder=args.cache_folder)

    if args.command == "list":
        for cache_id in cache.list():
            print(cache_id)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
