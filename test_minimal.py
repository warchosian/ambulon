#!/usr/bin/env python
import sys
print("Testing minimal execution...", flush=True)

if __name__ == "__main__":
    sys.argv = ["ambulon", "--help"]
    from app.cli.cli import main
    print("About to call main()...", flush=True)
    result = main()
    print(f"main() returned: {result}", flush=True)
    sys.exit(result or 0)
