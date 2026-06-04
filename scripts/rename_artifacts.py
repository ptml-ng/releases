#!/usr/bin/env python3
"""Rename files in a folder to replace an existing prefix or add a new prefix.

Usage:
    rename_artifacts.py <path> <new_prefix> [existing_prefix] [--ext apk|msi|dmg|deb|...]

`--ext` defaults to `apk` so existing 2/3-positional-arg callers (driver-app, management-app)
keep working unchanged. Pass `--ext msi` to rename Compose-Desktop installers, etc.
"""
import argparse
import glob
import os
import sys
from pathlib import Path


def rename_with_prefix(file_path, new_prefix, existing_prefix=""):
    """Rename a single file to swap or add a prefix. Returns new path on success or None."""
    try:
        path_obj = Path(file_path)
        name = path_obj.name
        if existing_prefix:
            with_dash = f"{existing_prefix}-"
            if name.startswith(with_dash):
                name = name[len(with_dash):]
            elif name.startswith(existing_prefix):
                name = name[len(existing_prefix):]
        new_name = f"{new_prefix}-{name}" if new_prefix else name
        new_path = path_obj.parent / new_name
        path_obj.rename(new_path)
        print(f"Renamed: {file_path} -> {new_path}")
        return str(new_path)
    except Exception as e:
        print(f"Error renaming {file_path}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Rename files in a folder to replace an existing prefix or add a new one.",
    )
    parser.add_argument("path", help="Folder containing the files.")
    parser.add_argument("new_prefix", help="New prefix to apply (pass empty string to skip).")
    parser.add_argument(
        "existing_prefix",
        nargs="?",
        default="",
        help="Existing prefix to strip first (optional).",
    )
    parser.add_argument("--ext", default="apk", help="File extension to match (default: apk).")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Path does not exist: {args.path}", file=sys.stderr)
        return 1

    new_prefix = args.new_prefix.strip().rstrip("-") if args.new_prefix else ""
    existing = args.existing_prefix.strip().rstrip("-") if args.existing_prefix else ""

    pattern = os.path.join(args.path, f"*.{args.ext}")
    files = glob.glob(pattern)
    if not files:
        print(f"No *.{args.ext} files found in {args.path}", file=sys.stderr)
        return 1

    print(f"Found {len(files)} *.{args.ext} file(s) to rename:")
    for f in files:
        print(f"  - {f}")
    if existing:
        print(f"Replacing existing prefix '{existing}' with '{new_prefix}'")
    else:
        print(f"Adding prefix '{new_prefix}'" if new_prefix else "No prefix changes (dry run)")

    renamed = [rename_with_prefix(f, new_prefix, existing) for f in files]
    renamed = [r for r in renamed if r]
    print(f"\nRename complete: {len(renamed)}/{len(files)} files renamed successfully")
    return 0 if renamed else 1


if __name__ == "__main__":
    sys.exit(main())
