import os
import sys

def write_output(lines):
    print("Output values:")
    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        # Append to the GITHUB_OUTPUT file (GitHub Actions expects key=value lines)
        try:
            with open(gh_output, "a", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception as e:
            print(f"Failed to write to GITHUB_OUTPUT={gh_output}: {e}", file=sys.stderr)
            # Fallback to printing
            for line in lines:
                print(line)
    else:
        # Not running inside GitHub Actions - print to stdout for debugging
        for line in lines:
            print(line)