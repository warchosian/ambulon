#!/usr/bin/env python
"""Wrapper simple pour ambulon qui évite les imports bloquants."""
import sys
import os

# Force le mode non-bloquant pour stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Import et exécution directe
if __name__ == "__main__":
    from app.cli.cli import main
    sys.exit(main() or 0)
