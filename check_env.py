#!/usr/bin/env python3
import os
import sys

print("=== Variables d'environnement ===\n")
for key, value in sorted(os.environ.items()):
    # Masquer les valeurs sensibles
    if any(s in key.lower() for s in ['token', 'secret', 'key', 'password', 'credential']):
        print(f"{key}=***MASQUE***")
    else:
        print(f"{key}={value}")

print("\n=== PATH décomposé ===\n")
path = os.environ.get('PATH', '')
for i, p in enumerate(path.split(os.pathsep), 1):
    print(f"{i}. {p}")

print("\n=== Python executable ===\n")
print(f"sys.executable: {sys.executable}")
print(f"sys.version: {sys.version}")
