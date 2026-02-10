#!/usr/bin/env python
"""Test project2md command"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dyag.commands.project2md import project_to_markdown


def main():
    """Test project2md on dyag commands directory."""

    print("=" * 70)
    print("Testing project2md command")
    print("=" * 70)

    # Test on src/dyag/commands directory
    result = project_to_markdown(
        directory="src/dyag/commands",
        output_path="test_project2md_output.md",
        verbose=True
    )

    if result == 0:
        print("\n[SUCCESS] Test completed!")
        print("\nGenerated file: test_project2md_output.md")
        print("You can now open this file and copy it to an AI for analysis.")
    else:
        print("\n[FAILED] Test failed!")

    return result


if __name__ == "__main__":
    sys.exit(main())
