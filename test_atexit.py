#!/usr/bin/env python
"""Test for atexit handlers."""
import sys
import atexit

# Patch atexit to see what's registered
original_register = atexit.register

def tracked_register(func, *args, **kwargs):
    print(f"ATEXIT registered: {func.__module__}.{func.__name__}")
    sys.stdout.flush()
    return original_register(func, *args, **kwargs)

atexit.register = tracked_register

print("Starting import...")
sys.stdout.flush()

from app.conversion.commands import html2md

print("Import done. Calling os._exit(0) to bypass atexit...")
sys.stdout.flush()

import os
os._exit(0)
