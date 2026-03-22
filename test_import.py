#!/usr/bin/env python
"""Test import blocking."""
import sys
print("Starting import test...")
sys.stdout.flush()

print("Importing html.parser...")
from html.parser import HTMLParser
print("OK")
sys.stdout.flush()

print("Importing html2md...")
from app.conversion.commands import html2md
print("OK - html2md imported")
sys.stdout.flush()

print("Done!")
