#!/usr/bin/env python3
"""
Rename APK files to replace an existing prefix or add a new prefix.
Usage: rename_artifacts.py <path> <new_prefix> [existing_prefix]
"""
import sys
import os
import glob
from pathlib import Path


def rename_apk_with_prefix(apk_path, new_prefix, existing_prefix=""):
    """
    Rename a single APK file to replace existing prefix or add new prefix.
    
    Args:
        apk_path: Path to the APK file
        new_prefix: New prefix to add (without trailing dash)
        existing_prefix: Existing prefix to replace (optional, default is empty)
    
    Returns:
        New file path if successful, None if failed
    """
    try:
        path_obj = Path(apk_path)
        
        # Get original filename
        original_name = path_obj.name
        
        # Handle existing prefix replacement
        if existing_prefix:
            # Check if filename starts with existing prefix
            prefix_with_dash = f"{existing_prefix}-"
            if original_name.startswith(prefix_with_dash):
                # Remove existing prefix
                original_name = original_name[len(prefix_with_dash):]
            elif original_name.startswith(existing_prefix):
                # Handle case where existing prefix doesn't have trailing dash
                original_name = original_name[len(existing_prefix):]
        
        # Create new filename with new prefix
        if new_prefix:
            new_name = f"{new_prefix}-{original_name}"
        else:
            new_name = original_name
        
        new_path = path_obj.parent / new_name
        
        # Rename the file
        path_obj.rename(new_path)
        print(f"Renamed: {apk_path} -> {new_path}")
        
        return str(new_path)
        
    except Exception as e:
        print(f"Error renaming {apk_path}: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: rename_artifacts.py <path> <new_prefix> [existing_prefix]", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  rename_artifacts.py ./app/build/outputs/apk/release arm64", file=sys.stderr)
        print("  rename_artifacts.py ./app/build/outputs/apk/release v2 v1", file=sys.stderr)
        print("  rename_artifacts.py ./app/build/outputs/apk/release \"\" debug  # Remove 'debug' prefix", file=sys.stderr)
        sys.exit(1)
    
    path_folder = sys.argv[1]
    new_prefix = sys.argv[2]
    existing_prefix = sys.argv[3] if len(sys.argv) > 3 else ""
    
    # Validate inputs
    if not os.path.exists(path_folder):
        print(f"Path does not exist: {path_folder}", file=sys.stderr)
        sys.exit(1)
    
    # Clean prefixes (remove leading/trailing spaces and dashes)
    new_prefix = new_prefix.strip().rstrip('-') if new_prefix else ""
    existing_prefix = existing_prefix.strip().rstrip('-') if existing_prefix else ""
    
    # Find all APK files in the path
    apk_pattern = os.path.join(path_folder, "*.apk")
    apk_files = glob.glob(apk_pattern)
    
    if not apk_files:
        print(f"No APK files found in {path_folder}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(apk_files)} APK file(s) to rename:")
    for apk in apk_files:
        print(f"  - {apk}")
    
    if existing_prefix:
        print(f"Replacing existing prefix '{existing_prefix}' with '{new_prefix}'")
    else:
        print(f"Adding prefix '{new_prefix}'" if new_prefix else "No prefix changes (dry run)")
    
    # Rename each APK file
    success_count = 0
    renamed_files = []
    
    for apk_file in apk_files:
        new_path = rename_apk_with_prefix(apk_file, new_prefix, existing_prefix)
        if new_path:
            success_count += 1
            renamed_files.append(new_path)
    
    print(f"\nRename complete: {success_count}/{len(apk_files)} files renamed successfully")
    
    if renamed_files:
        print("\nRenamed files:")
        for renamed_file in renamed_files:
            print(f"  - {renamed_file}")
    
    if success_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
