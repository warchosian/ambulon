#!/usr/bin/env python3
"""Create the pipeline directory structure."""

from pathlib import Path

dirs = [
    'src/app/pipeline',
    'src/app/pipeline/commands',
    'src/app/pipeline/core'
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)
    print(f'Created: {d}')

print('\nAll directories created successfully!')
