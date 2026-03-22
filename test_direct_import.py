#!/usr/bin/env python
"""Test direct module import."""
import sys

print("Testing direct import of html2md module...")
sys.stdout.flush()

# Direct import without going through conversion/__init__.py
import app.conversion.commands.html2md as html2md_module

print("Success! html2md module imported directly.")
sys.stdout.flush()

print("Exiting with os._exit(0)...")
import os
os._exit(0)
