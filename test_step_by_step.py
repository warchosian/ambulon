#!/usr/bin/env python
"""Test step-by-step imports."""
import sys
import os

print("1. Importing app...")
sys.stdout.flush()
import app
print("   OK")

print("2. Importing app.conversion...")
sys.stdout.flush()
import app.conversion
print("   OK")

print("3. Importing app.conversion.commands...")
sys.stdout.flush()
import app.conversion.commands
print("   OK")

print("4. Importing app.conversion.commands.html2md...")
sys.stdout.flush()
import app.conversion.commands.html2md
print("   OK")

print("All imports successful!")
os._exit(0)
