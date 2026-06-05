import argparse
import os
import sys
from collections.abc import Sequence

from unforgettable import unforgettable

DEFAULT_CACHE_FOLDER = ".unforgettable-memory"


def confirm_create_cache_folder(cache_folder: str) -> bool:
    sys.stderr.write(
        f"unforgettable: cache folder does not exist: {cache_folder}\n"
        "Create it? [y/N] "
    )
    sys.stderr.flush()

    response = sys.stdin.readline()
    if response == "":
        sys.stderr.write("unforgettable: cache folder creation cancelled\n")
        return False

    return response.strip().lower() in {"y", "yes"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unforgettable",
        description="Inspect and maintain an Unforgettable cache.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--cache-folder",
        default=None,
        help=(
            "Folder containing the cache files to operate on. "
            f"Defaults to {DEFAULT_CACHE_FOLDER}."
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available cache IDs.")

    set_parser = subparsers.add_parser("set", help="Store text content.")
    set_parser.add_argument("cache_id", help="Cache ID to store content under.")
    set_parser.add_argument("content", help="Text content to store.")

    get_parser = subparsers.add_parser("get", help="Retrieve cached content.")
    get_parser.add_argument("cache_id", help="Cache ID to retrieve.")

    subparsers.add_parser("clean", help="Remove cached values.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cache_folder_was_explicit = args.cache_folder is not None
    cache_folder = args.cache_folder or DEFAULT_CACHE_FOLDER

    if cache_folder_was_explicit and not os.path.exists(cache_folder):
        if not confirm_create_cache_folder(cache_folder):
            parser.exit(1, "unforgettable: cache folder was not created\n")
        os.makedirs(cache_folder)
    elif not cache_folder_was_explicit:
        os.makedirs(cache_folder, exist_ok=True)

    cache = unforgettable(cache_folder=cache_folder)

    if args.command == "list":
        for cache_id in cache.list():
            print(cache_id)
        return 0

    if args.command == "set":
        cache.set(content=args.content, cache_id=args.cache_id)
        return 0

    if args.command == "get":
        content = cache.get(cache_id=args.cache_id)
        if content is None:
            parser.exit(1, f"unforgettable: cache ID not found: {args.cache_id}\n")
        print(content)
        return 0

    if args.command == "clean":
        cache.clean()
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
