#!/usr/bin/env python
"""Test script for md2html conversion"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dyag.commands.md2html import process_markdown_to_html

# Test file
markdown_file = "examples/test-hraccess/pseudonymes.md"
output_file = "examples/test-hraccess/pseudonymes.html"

print(f"Testing md2html conversion...")
print(f"Input: {markdown_file}")
print(f"Output: {output_file}")
print("-" * 60)

# Run conversion
exit_code = process_markdown_to_html(
    markdown_file,
    output_file,
    verbose=True,
    standalone=True
)

sys.exit(exit_code)
