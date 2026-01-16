#!/usr/bin/env python
"""Test add-toc command"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dyag.commands.add_toc import add_toc_to_html


def main():
    """Test add-toc with a generated HTML file."""

    # Use one of the HTML files we generated earlier
    input_file = "examples/test-multidiagrams/multidiagrams.dos.html"
    output_file = "examples/test-multidiagrams/multidiagrams.dos.toc.html"

    print("=" * 70)
    print("Testing add-toc command")
    print("=" * 70)
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_file}")
    print("\n" + "-" * 70)

    # Run the command
    result = add_toc_to_html(input_file, output_file, verbose=True)

    print("-" * 70)

    if result == 0:
        print("\n[SUCCESS] Test completed successfully!")

        # Check file size
        if Path(output_file).exists():
            size = Path(output_file).stat().st_size
            original_size = Path(input_file).stat().st_size
            print(f"\nOriginal file: {original_size:,} bytes")
            print(f"With TOC:      {size:,} bytes")
            print(f"Difference:    +{size - original_size:,} bytes")
    else:
        print("\n[FAILED] Test failed!")

    return result


if __name__ == "__main__":
    sys.exit(main())
