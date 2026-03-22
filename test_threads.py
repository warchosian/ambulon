#!/usr/bin/env python
"""Test for hanging threads."""
import sys
import threading

print("Starting import...")
sys.stdout.flush()

from app.conversion.commands import html2md

print(f"Active threads after import: {threading.active_count()}")
for thread in threading.enumerate():
    print(f"  - {thread.name}: daemon={thread.daemon}, alive={thread.is_alive()}")
sys.stdout.flush()

print("Exiting...")
sys.exit(0)
