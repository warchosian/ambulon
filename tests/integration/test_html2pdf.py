#!/usr/bin/env python
"""Test html2pdf command"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dyag.commands.html2pdf import convert_html_to_pdf


def main():
    """Test html2pdf with the HTML file that has TOC and links."""

    # Use the HTML file with TOC that we generated earlier
    input_file = "examples/test-multidiagrams/multidiagrams.dos.toc.html"

    # Test both orientations
    tests = [
        {
            "output": "examples/test-multidiagrams/multidiagrams.dos.toc.portrait.pdf",
            "orientation": "portrait",
            "description": "Portrait mode"
        },
        {
            "output": "examples/test-multidiagrams/multidiagrams.dos.toc.landscape.pdf",
            "orientation": "landscape",
            "description": "Landscape mode"
        }
    ]

    for test in tests:
        print("=" * 70)
        print(f"Testing HTML to PDF conversion - {test['description']}")
        print("=" * 70)
        print(f"\nInput:       {input_file}")
        print(f"Output:      {test['output']}")
        print(f"Orientation: {test['orientation']}")
        print("\n" + "-" * 70)

        # Run the command
        result = convert_html_to_pdf(
            input_file,
            test['output'],
            orientation=test['orientation'],
            verbose=True
        )

        print("-" * 70)

        if result == 0:
            print(f"\n[SUCCESS] {test['description']} test completed!")

            # Check file was created
            if Path(test['output']).exists():
                size = Path(test['output']).stat().st_size
                print(f"PDF file size: {size:,} bytes")
        else:
            print(f"\n[FAILED] {test['description']} test failed!")
            return 1

        print("\n")

    print("=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nVerify the PDFs:")
    for test in tests:
        print(f"  - {test['output']}")
    print("\nCheck that internal links (TOC navigation) work in the PDFs!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
